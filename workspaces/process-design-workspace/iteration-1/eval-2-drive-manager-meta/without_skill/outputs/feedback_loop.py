#!/usr/bin/env python3
"""
feedback_loop.py — drive-manager routing-correction feedback loop.

Captures cases where drive-manager:process-inbox routed a file wrong,
triages them with a human in the loop, and edits the rules file with
provenance and a regression-guard replay.

See SPEC.md for the full design.

Usage:
    feedback_loop.py detect
    feedback_loop.py log-correction <file_path> [--correct-dest <dir>]
    feedback_loop.py review
    feedback_loop.py promote
    feedback_loop.py verify [--rule <rule_id>]
    feedback_loop.py status

This is a working scaffold. Edge cases (file disappears mid-detect,
rules file conflicts, etc.) are handled defensively but not exhaustively.
The triage classifier is intentionally simple and conservative — when
in doubt it asks the user rather than guessing.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    print("This script requires PyYAML. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(os.environ.get("DRIVE_MANAGER_HOME", Path.home() / ".drive-manager"))
DECISIONS_LOG = ROOT / "route-decision.jsonl"   # written by the skill
CORRECTIONS_LOG = ROOT / "corrections.jsonl"    # written by us
RULES_FILE = ROOT / "rules.yaml"                # read by the skill, written by us
BACKUP_DIR = ROOT / "rules.yaml.bak"

RECENCY_WINDOW_DAYS = 90
REPLAY_PASS_THRESHOLD = 0.90  # >=90% of historical miscalls in target folder must now route right
HIGH_CONFIDENCE_TOKENS_MIN = 1  # need at least 1 strong signal for auto-suggest "new rule"

NOW = lambda: dt.datetime.now(dt.timezone.utc)


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------


def ensure_root() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for f in (DECISIONS_LOG, CORRECTIONS_LOG):
        f.touch(exist_ok=True)
    if not RULES_FILE.exists():
        RULES_FILE.write_text("rules: []\n")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def iso(t: dt.datetime | None = None) -> str:
    return (t or NOW()).isoformat(timespec="seconds")


def parse_iso(s: str) -> dt.datetime:
    # tolerate both "Z" and "+00:00"
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


@contextmanager
def append_locked(path: Path):
    """Append-only writes need a flock so a parallel detect doesn't tear records."""
    with path.open("a", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            yield fh
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def read_jsonl(path: Path) -> list[dict]:
    out: list[dict] = []
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"warn: skipping malformed line in {path.name}: {e}", file=sys.stderr)
    return out


def write_jsonl(path: Path, records: Iterable[dict]) -> None:
    """Rewrite the whole file. Used for status updates on existing corrections."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    tmp.replace(path)


def tokenize(s: str) -> list[str]:
    out, cur = [], []
    for ch in s.lower():
        if ch.isalnum():
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    return [t for t in out if len(t) >= 2]


def confirm(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n] " if default else " [y/N] "
    try:
        ans = input(prompt + suffix).strip().lower()
    except EOFError:
        return default
    if not ans:
        return default
    return ans.startswith("y")


def prompt_for(prompt: str, default: str = "") -> str:
    try:
        ans = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    except EOFError:
        ans = ""
    return ans or default


# ---------------------------------------------------------------------------
# Rules store — abstracted so YAML can be swapped for JSON/TOML
# ---------------------------------------------------------------------------


@dataclass
class Rule:
    id: str
    match: dict[str, Any] = field(default_factory=dict)
    route_to: str = ""
    weight: float = 0.5
    provenance: dict[str, Any] = field(default_factory=dict)
    ask_user: bool = False  # if true, skill should prompt instead of auto-routing


class RulesStore:
    def __init__(self, path: Path = RULES_FILE):
        self.path = path

    def load(self) -> list[Rule]:
        data = yaml.safe_load(self.path.read_text()) or {}
        raw = data.get("rules", []) or []
        return [Rule(**r) for r in raw]

    def save(self, rules: list[Rule], reason: str) -> None:
        self._backup(reason)
        out = {"rules": [asdict(r) for r in rules]}
        self.path.write_text(yaml.safe_dump(out, sort_keys=False))

    def _backup(self, reason: str) -> None:
        # Prefer git if the rules file is tracked
        if self._is_git_tracked():
            try:
                subprocess.run(
                    ["git", "-C", str(self.path.parent), "add", self.path.name],
                    check=True, capture_output=True,
                )
                subprocess.run(
                    ["git", "-C", str(self.path.parent), "commit",
                     "-m", f"feedback_loop: pre-edit snapshot ({reason})"],
                    check=False, capture_output=True,
                )
                return
            except Exception:
                pass  # fall through to file backup
        ts = NOW().strftime("%Y%m%dT%H%M%SZ")
        dest = BACKUP_DIR / f"rules-{ts}.yaml"
        if self.path.exists():
            shutil.copy2(self.path, dest)

    def _is_git_tracked(self) -> bool:
        try:
            r = subprocess.run(
                ["git", "-C", str(self.path.parent), "ls-files", "--error-unmatch", self.path.name],
                capture_output=True,
            )
            return r.returncode == 0
        except FileNotFoundError:
            return False


# ---------------------------------------------------------------------------
# Rules engine — toy version, sufficient for replay/verify
# ---------------------------------------------------------------------------


def evaluate_rules(rules: list[Rule], signals: dict[str, Any]) -> tuple[Rule | None, float]:
    """Returns (best_rule, score). Higher score wins; None if nothing matches."""
    best: Rule | None = None
    best_score = 0.0
    tokens = set(signals.get("filename_tokens", [])) | set(
        tokenize(" ".join(signals.get("ocr_keywords", [])))
    )
    sender = (signals.get("sender") or "").lower()

    for r in rules:
        m = r.match or {}
        score = 0.0
        all_tokens = set(t.lower() for t in m.get("filename_tokens_all", []))
        any_tokens = set(t.lower() for t in m.get("filename_tokens_any", []))
        sender_match = (m.get("sender") or "").lower()

        if all_tokens and not all_tokens.issubset(tokens):
            continue
        if any_tokens and not any_tokens & tokens:
            continue
        if sender_match and sender_match not in sender:
            continue

        # rough scoring: rule weight + bonus for specificity
        score = r.weight + 0.05 * len(all_tokens) + 0.02 * len(any_tokens & tokens)
        if score > best_score:
            best, best_score = r, score

    return best, best_score


# ---------------------------------------------------------------------------
# DETECT — find miscalls by comparing decision log against current filesystem
# ---------------------------------------------------------------------------


def cmd_detect(_args) -> int:
    decisions = read_jsonl(DECISIONS_LOG)
    existing_corrections = read_jsonl(CORRECTIONS_LOG)
    seen_decisions = {c.get("decision_id") for c in existing_corrections}

    new_records: list[dict] = []
    for d in decisions:
        decision_id = d.get("id")
        if decision_id in seen_decisions:
            continue
        chosen = Path(d.get("chosen_path", ""))
        if not chosen.exists() or not chosen.is_dir():
            continue  # destination folder gone? skip; not our problem
        file_hash = d.get("file_hash")
        if not file_hash:
            continue

        # Did the file end up somewhere other than chosen_path?
        actual = _locate_file_by_hash(file_hash, chosen)
        if actual is None or actual.parent == chosen:
            continue  # still where the skill put it, or we can't find it

        record = _make_correction(d, actual)
        new_records.append(record)

    if not new_records:
        print("detect: no new miscalls found.")
        return 0

    with append_locked(CORRECTIONS_LOG) as fh:
        for r in new_records:
            fh.write(json.dumps(r) + "\n")

    print(f"detect: captured {len(new_records)} correction(s).")
    for r in new_records:
        print(f"  {r['id']}  {r['file']['name']!r}  -> {r['user_chose']}")
    return 0


def _locate_file_by_hash(file_hash: str, originally_chosen: Path) -> Path | None:
    """
    Search likely locations for a file with this hash. We don't want to walk
    the whole drive, so we look at: the user's known drive roots, common
    inbox-adjacent paths, and skip if not found in a reasonable scan.

    A real implementation would maintain a separate index. This scaffold
    walks two configurable roots.
    """
    roots_env = os.environ.get("DRIVE_MANAGER_SEARCH_ROOTS", "")
    roots = [Path(p).expanduser() for p in roots_env.split(":") if p.strip()]
    if not roots:
        # sensible defaults
        roots = [
            Path.home() / "Library/CloudStorage",
            Path.home() / "Documents",
        ]
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            try:
                if p.stat().st_size > 200 * 1024 * 1024:  # skip huge files
                    continue
                if sha256_of(p) == file_hash:
                    return p
            except (OSError, PermissionError):
                continue
    return None


def _make_correction(decision: dict, actual: Path) -> dict:
    cid = f"corr-{NOW().strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:6]}"
    fname = decision.get("file_name") or actual.name
    return {
        "id": cid,
        "decision_id": decision.get("id"),
        "ts": iso(),
        "file": {
            "name": fname,
            "hash": decision.get("file_hash"),
            "size": decision.get("file_size"),
            "mime": decision.get("mime"),
        },
        "skill_chose": decision.get("chosen_path"),
        "skill_rule_id": decision.get("rule_id"),
        "skill_confidence": decision.get("confidence"),
        "user_chose": str(actual.parent),
        "signals_available_at_decision": decision.get("signals", {
            "filename_tokens": tokenize(fname),
            "ocr_keywords": [],
            "sender": None,
        }),
        "user_note": "",
        "status": "new",
        "triage_bucket": None,
        "promoted_rule_id": None,
    }


# ---------------------------------------------------------------------------
# LOG-CORRECTION — manual entry path
# ---------------------------------------------------------------------------


def cmd_log_correction(args) -> int:
    f = Path(args.file_path).expanduser().resolve()
    if not f.is_file():
        print(f"error: {f} is not a file", file=sys.stderr)
        return 1

    fhash = sha256_of(f)
    decisions = read_jsonl(DECISIONS_LOG)
    decision = next((d for d in reversed(decisions) if d.get("file_hash") == fhash), None)

    if decision is None:
        print("warn: no matching decision in audit log; recording as orphan correction")
        decision = {
            "id": None,
            "file_hash": fhash,
            "file_name": f.name,
            "file_size": f.stat().st_size,
            "chosen_path": prompt_for("Where did the skill route this (best guess)?", ""),
            "rule_id": None,
            "confidence": None,
            "signals": {"filename_tokens": tokenize(f.name), "ocr_keywords": [], "sender": None},
        }

    actual_dir = args.correct_dest or str(f.parent)
    record = _make_correction(decision, Path(actual_dir) / f.name)
    note = prompt_for("User note (why is this the right home?)", "")
    record["user_note"] = note

    with append_locked(CORRECTIONS_LOG) as fh:
        fh.write(json.dumps(record) + "\n")
    print(f"log-correction: recorded {record['id']}")
    return 0


# ---------------------------------------------------------------------------
# TRIAGE — classify each `new` correction into A/B/C/D
# ---------------------------------------------------------------------------


def _signal_strength(corr: dict) -> int:
    """Cheap proxy: count distinctive tokens (length>=4, not stopwordy)."""
    sig = corr.get("signals_available_at_decision", {})
    toks = set(sig.get("filename_tokens", [])) | set(
        tokenize(" ".join(sig.get("ocr_keywords", [])))
    )
    stop = {"invoice", "report", "doc", "file", "scan", "image", "pdf", "draft"}
    return sum(1 for t in toks if len(t) >= 4 and t not in stop)


def _recurrence(corr: dict, all_corrs: list[dict]) -> int:
    """How many other recent corrections route to the same destination with overlapping signals?"""
    cutoff = NOW() - dt.timedelta(days=RECENCY_WINDOW_DAYS)
    target = corr["user_chose"]
    my_toks = set(corr.get("signals_available_at_decision", {}).get("filename_tokens", []))
    n = 0
    for c in all_corrs:
        if c["id"] == corr["id"]:
            continue
        if c["user_chose"] != target:
            continue
        try:
            if parse_iso(c["ts"]) < cutoff:
                continue
        except Exception:
            continue
        their_toks = set(c.get("signals_available_at_decision", {}).get("filename_tokens", []))
        if my_toks & their_toks:
            n += 1
    return n


def _suggest_bucket(corr: dict, all_corrs: list[dict], rules: list[Rule]) -> tuple[str, str]:
    """Returns (bucket_letter, reason). A=new rule, B=strengthen, C=ask_user, D=noise."""
    recurrence = _recurrence(corr, all_corrs)
    strength = _signal_strength(corr)

    skill_chose = corr.get("skill_chose", "")
    user_chose = corr.get("user_chose", "")
    existing_targets = {r.route_to.rstrip("/") for r in rules}
    target_already_a_rule = any(
        user_chose.rstrip("/").startswith(t) for t in existing_targets if t
    )

    # quick D check: super weak signal AND not recurring
    if strength == 0 and recurrence == 0:
        return ("D", "no distinctive signals and no recurrence — looks like a one-off")

    # C check: same signals previously routed to a *different* user_chose
    sig_tokens = set(corr.get("signals_available_at_decision", {}).get("filename_tokens", []))
    conflicting = [
        c for c in all_corrs
        if c["id"] != corr["id"]
        and sig_tokens & set(c.get("signals_available_at_decision", {}).get("filename_tokens", []))
        and c["user_chose"] != corr["user_chose"]
    ]
    if conflicting:
        return ("C", f"signals collide with {len(conflicting)} other correction(s) targeting different folders")

    # B check: target already has a rule, but skill missed it -> strengthen
    if target_already_a_rule and skill_chose != user_chose:
        return ("B", "target folder already has a rule; existing rule needs strengthening")

    # A check: clean signal + (recurrence>=1 OR explicit user note)
    if strength >= HIGH_CONFIDENCE_TOKENS_MIN and (recurrence >= 1 or corr.get("user_note")):
        return ("A", f"clean signal (strength={strength}), recurrence={recurrence}")

    # default: defer
    return ("D", "insufficient evidence to act yet — defer")


def cmd_review(_args) -> int:
    corrs = read_jsonl(CORRECTIONS_LOG)
    rules = RulesStore().load()
    new_ones = [c for c in corrs if c.get("status") == "new"]

    if not new_ones:
        print("review: no new corrections.")
        return 0

    print(f"review: {len(new_ones)} new correction(s) to triage.")
    for c in new_ones:
        bucket, reason = _suggest_bucket(c, corrs, rules)
        print()
        print(f"  id:          {c['id']}")
        print(f"  file:        {c['file']['name']}")
        print(f"  skill chose: {c['skill_chose']}  (rule={c.get('skill_rule_id')}, conf={c.get('skill_confidence')})")
        print(f"  user chose:  {c['user_chose']}")
        if c.get("user_note"):
            print(f"  note:        {c['user_note']}")
        print(f"  suggested:   bucket {bucket} — {reason}")

        ans = prompt_for("Accept (a) / override (b/c/d/A) / skip (s) / reject (r)", bucket).strip()
        if ans.lower() == "s":
            continue
        if ans.lower() == "r":
            c["status"] = "rejected"
            c["triage_bucket"] = "D"
            c["triage_reason"] = "user rejected"
            continue
        chosen = ans.upper()[0] if ans else bucket
        if chosen not in ("A", "B", "C", "D"):
            print("  -> unrecognised, skipping")
            continue
        c["status"] = "triaged" if chosen != "D" else "rejected"
        c["triage_bucket"] = chosen
        c["triage_reason"] = reason if ans.lower() == "a" or not ans else "user-overridden"

    write_jsonl(CORRECTIONS_LOG, corrs)
    counts = Counter(c.get("triage_bucket") for c in corrs if c.get("status") in ("triaged", "rejected"))
    print(f"\nreview: done. Triaged buckets so far -> {dict(counts)}")
    return 0


# ---------------------------------------------------------------------------
# PROMOTE — apply triaged corrections to the rules file
# ---------------------------------------------------------------------------


def cmd_promote(_args) -> int:
    corrs = read_jsonl(CORRECTIONS_LOG)
    store = RulesStore()
    rules = store.load()
    triaged = [c for c in corrs if c.get("status") == "triaged"]

    if not triaged:
        print("promote: nothing triaged.")
        return 0

    # Group by (bucket, target folder) so we batch related corrections into one rule edit
    groups: dict[tuple[str, str], list[dict]] = {}
    for c in triaged:
        key = (c["triage_bucket"], c["user_chose"])
        groups.setdefault(key, []).append(c)

    edits_applied = 0
    for (bucket, target), group in groups.items():
        print(f"\npromote: bucket {bucket} -> {target}  ({len(group)} correction(s))")
        for c in group:
            print(f"  - {c['id']}  {c['file']['name']}")

        if not confirm("  apply this edit?", default=True):
            continue

        if bucket == "A":
            new_rule = _synthesize_new_rule(group, rules)
            rules.append(new_rule)
            for c in group:
                c["status"] = "promoted"
                c["promoted_rule_id"] = new_rule.id
            print(f"  -> added new rule {new_rule.id}")
            edits_applied += 1

        elif bucket == "B":
            r = _pick_rule_to_strengthen(group, rules)
            if not r:
                print("  -> no obvious rule to strengthen, skipping")
                continue
            _strengthen_rule(r, group)
            for c in group:
                c["status"] = "promoted"
                c["promoted_rule_id"] = r.id
            print(f"  -> strengthened rule {r.id}")
            edits_applied += 1

        elif bucket == "C":
            ask_rule = _synthesize_ask_user_rule(group)
            rules.append(ask_rule)
            for c in group:
                c["status"] = "promoted"
                c["promoted_rule_id"] = ask_rule.id
            print(f"  -> added ask_user rule {ask_rule.id}")
            edits_applied += 1

    if edits_applied == 0:
        print("\npromote: no edits applied.")
        return 0

    # Regression-guard replay before saving
    ok, report = _replay_check(rules, corrs)
    print(f"\nverify (replay): {report}")
    if not ok:
        if not confirm("  replay shows regressions. apply anyway?", default=False):
            print("  -> aborting; rules file untouched")
            return 1

    store.save(rules, reason=f"promote {edits_applied} edit(s)")
    write_jsonl(CORRECTIONS_LOG, corrs)
    print(f"\npromote: applied {edits_applied} edit(s) to {RULES_FILE}")
    return 0


def _synthesize_new_rule(group: list[dict], rules: list[Rule]) -> Rule:
    # token frequency across the group; pick tokens that show up in >= half
    counter: Counter[str] = Counter()
    for c in group:
        toks = c.get("signals_available_at_decision", {}).get("filename_tokens", [])
        counter.update(set(toks))
    threshold = max(1, len(group) // 2)
    common = [t for t, n in counter.items() if n >= threshold and len(t) >= 3]
    common.sort(key=lambda t: -counter[t])

    base_id = "auto-" + "-".join(common[:2]) if common else f"auto-{uuid.uuid4().hex[:6]}"
    rule_id = base_id
    n = 2
    while any(r.id == rule_id for r in rules):
        rule_id = f"{base_id}-{n}"
        n += 1

    return Rule(
        id=rule_id,
        match={
            "filename_tokens_all": common[:1],
            "filename_tokens_any": common[:5] or list(counter.keys())[:3],
        },
        route_to=group[0]["user_chose"],
        weight=0.6 if len(group) == 1 else 0.75,
        provenance={
            "created_from": [c["id"] for c in group],
            "last_modified": iso(),
        },
    )


def _pick_rule_to_strengthen(group: list[dict], rules: list[Rule]) -> Rule | None:
    target = group[0]["user_chose"]
    candidates = [r for r in rules if r.route_to.rstrip("/") == target.rstrip("/")]
    if not candidates:
        # fall back to any rule prefix-matching the target
        candidates = [r for r in rules if target.rstrip("/").startswith(r.route_to.rstrip("/")) and r.route_to]
    return candidates[0] if candidates else None


def _strengthen_rule(rule: Rule, group: list[dict]) -> None:
    counter: Counter[str] = Counter()
    for c in group:
        counter.update(c.get("signals_available_at_decision", {}).get("filename_tokens", []))
    new_any = list(rule.match.get("filename_tokens_any", []))
    for t, _ in counter.most_common(5):
        if t not in new_any and len(t) >= 3:
            new_any.append(t)
    rule.match["filename_tokens_any"] = new_any
    rule.weight = min(0.95, rule.weight + 0.05)
    rule.provenance.setdefault("strengthened_from", []).extend([c["id"] for c in group])
    rule.provenance["last_modified"] = iso()


def _synthesize_ask_user_rule(group: list[dict]) -> Rule:
    # ask_user rules don't pick a destination — they tell the skill to stop and prompt
    counter: Counter[str] = Counter()
    for c in group:
        counter.update(c.get("signals_available_at_decision", {}).get("filename_tokens", []))
    common = [t for t, _ in counter.most_common(3)]
    rid = "ask-" + "-".join(common[:2]) if common else f"ask-{uuid.uuid4().hex[:6]}"
    return Rule(
        id=rid,
        match={"filename_tokens_all": common[:1], "filename_tokens_any": common},
        route_to="",
        weight=0.99,  # high so it beats other matches
        ask_user=True,
        provenance={
            "created_from": [c["id"] for c in group],
            "last_modified": iso(),
            "reason": "signals collide; user must disambiguate",
        },
    )


# ---------------------------------------------------------------------------
# VERIFY — regression replay
# ---------------------------------------------------------------------------


def _replay_check(rules: list[Rule], corrs: list[dict]) -> tuple[bool, str]:
    """
    Replay every promoted/triaged correction and check the rules now route it correctly.
    Pass = >= REPLAY_PASS_THRESHOLD fraction route to user_chose.
    """
    cutoff = NOW() - dt.timedelta(days=RECENCY_WINDOW_DAYS)
    sample = [
        c for c in corrs
        if c.get("status") in ("triaged", "promoted", "verified")
        and parse_iso(c["ts"]) >= cutoff
    ]
    if not sample:
        return True, "no historical corrections to replay"

    correct = 0
    misses: list[str] = []
    for c in sample:
        signals = c.get("signals_available_at_decision", {})
        rule, _score = evaluate_rules(rules, signals)
        if rule and not rule.ask_user and rule.route_to.rstrip("/") == c["user_chose"].rstrip("/"):
            correct += 1
        elif rule and rule.ask_user:
            correct += 1  # ask_user is a valid outcome for collisions
        else:
            misses.append(c["id"])
    pct = correct / len(sample)
    ok = pct >= REPLAY_PASS_THRESHOLD
    summary = f"{correct}/{len(sample)} ({pct:.0%}) replay correctly"
    if misses[:3]:
        summary += f"; misses include {', '.join(misses[:3])}"
    return ok, summary


def cmd_verify(args) -> int:
    rules = RulesStore().load()
    corrs = read_jsonl(CORRECTIONS_LOG)
    if args.rule:
        rules = [r for r in rules if r.id == args.rule]
        if not rules:
            print(f"error: rule {args.rule!r} not found", file=sys.stderr)
            return 1
    ok, report = _replay_check(rules, corrs)
    print(f"verify: {report}  -> {'OK' if ok else 'REGRESSION'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# STATUS — counts and metrics
# ---------------------------------------------------------------------------


def cmd_status(_args) -> int:
    corrs = read_jsonl(CORRECTIONS_LOG)
    decisions = read_jsonl(DECISIONS_LOG)

    counts = Counter(c.get("status") for c in corrs)
    buckets = Counter(c.get("triage_bucket") for c in corrs if c.get("triage_bucket"))

    # capture rate
    last30_decisions = [
        d for d in decisions
        if "ts" in d and parse_iso(d["ts"]) >= NOW() - dt.timedelta(days=30)
    ]
    last30_corrs = [
        c for c in corrs
        if parse_iso(c["ts"]) >= NOW() - dt.timedelta(days=30)
    ]
    capture_rate = (
        f"{len(last30_corrs)} corrections / {len(last30_decisions)} decisions in last 30d"
    )

    # promotion latency
    latencies: list[float] = []
    for c in corrs:
        if c.get("status") == "promoted" and c.get("promoted_at"):
            try:
                latencies.append(
                    (parse_iso(c["promoted_at"]) - parse_iso(c["ts"])).total_seconds() / 86400
                )
            except Exception:
                pass
    median_latency = (
        f"{sorted(latencies)[len(latencies)//2]:.1f}d" if latencies else "n/a"
    )

    # repeat-miss
    last30 = [c for c in corrs if parse_iso(c["ts"]) >= NOW() - dt.timedelta(days=30)]
    repeats = 0
    for c in last30:
        prior = [
            x for x in corrs
            if x["id"] != c["id"]
            and parse_iso(x["ts"]) < parse_iso(c["ts"])
            and parse_iso(x["ts"]) >= parse_iso(c["ts"]) - dt.timedelta(days=90)
            and set(x.get("signals_available_at_decision", {}).get("filename_tokens", []))
                & set(c.get("signals_available_at_decision", {}).get("filename_tokens", []))
        ]
        if prior:
            repeats += 1
    repeat_rate = f"{repeats}/{len(last30)}" if last30 else "0/0"

    print("status:")
    print(f"  corrections by status: {dict(counts)}")
    print(f"  triage buckets:        {dict(buckets)}")
    print(f"  capture rate:          {capture_rate}")
    print(f"  median promotion lag:  {median_latency}")
    print(f"  repeat-miss (30d):     {repeat_rate}")

    # top recurring signatures still untriaged
    new_ones = [c for c in corrs if c.get("status") == "new"]
    sig_counter: Counter[tuple[str, ...]] = Counter()
    for c in new_ones:
        toks = tuple(sorted(c.get("signals_available_at_decision", {}).get("filename_tokens", []))[:3])
        if toks:
            sig_counter[toks] += 1
    if sig_counter:
        print("  top untriaged signatures:")
        for sig, n in sig_counter.most_common(5):
            print(f"    {n}x  {sig}")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ensure_root()
    p = argparse.ArgumentParser(description="drive-manager routing-correction feedback loop")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("detect", help="scan audit log for files moved away from skill's pick")

    pl = sub.add_parser("log-correction", help="manually log a correction for one file")
    pl.add_argument("file_path")
    pl.add_argument("--correct-dest", default=None,
                    help="folder the file should have been routed to (defaults to its current parent)")

    sub.add_parser("review", help="interactive triage of new corrections")
    sub.add_parser("promote", help="apply triaged corrections to the rules file")

    pv = sub.add_parser("verify", help="replay historical corrections against current rules")
    pv.add_argument("--rule", default=None)

    sub.add_parser("status", help="show counts and metrics")

    args = p.parse_args(argv)
    handlers = {
        "detect": cmd_detect,
        "log-correction": cmd_log_correction,
        "review": cmd_review,
        "promote": cmd_promote,
        "verify": cmd_verify,
        "status": cmd_status,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
