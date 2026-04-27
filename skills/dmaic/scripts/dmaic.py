#!/usr/bin/env python3
"""
DMAIC orchestrator helper script.

Three subcommands:

  detect-vault   Walk up from --cwd and figure out whether we're in an
                 Obsidian vault, a Linglepedia vault, or no vault at all.
                 Returns JSON describing the vault root and known folders.

  compose        Take a spec.json with frontmatter fields and the five
                 phase blocks, and write a complete DMAIC spec markdown
                 file. Eliminates string-assembly drift between runs.

  validate       Read a DMAIC spec markdown file and check it against the
                 schema (frontmatter complete, all five sections, 2–3
                 metrics, Control non-empty, etc.). Returns JSON with
                 per-check pass/fail and exits non-zero on hard failures.

Designed to be invoked by the dmaic skill's SKILL.md. Self-contained — no
third-party dependencies. Works on any Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


# -----------------------------------------------------------------------------
# detect-vault
# -----------------------------------------------------------------------------

LINGLEPEDIA_FOLDERS = [
    "VEGA", "Finance", "GIX", "WE", "People", "Capital Partners",
    "Fiber Infrastructure Businesses", "Real Estate Properties",
    "Auto", "Books", "Eta Vision", "Mike Career", "Projects",
    "Journal", "Values and Mechanisms",
]


def detect_vault(cwd: Path) -> dict[str, Any]:
    """Walk up from cwd; report what kind of vault we're in (if any)."""
    cwd = cwd.resolve()
    candidates = [cwd, *cwd.parents]

    vault_root: Path | None = None
    vault_type = "none"
    signals: list[str] = []

    for d in candidates:
        if (d / ".obsidian").is_dir():
            vault_root = d
            vault_type = "obsidian"
            signals.append(".obsidian/ found")
            break
        if (d / "_schemas").is_dir() and (d / "CLAUDE.md").is_file():
            vault_root = d
            vault_type = "linglepedia"
            signals.append("_schemas/ + CLAUDE.md found")
            break

    # Re-check whether an Obsidian vault is also a Linglepedia vault
    if vault_root and vault_type == "obsidian" and (vault_root / "_schemas").is_dir():
        vault_type = "linglepedia"
        signals.append("_schemas/ also present")

    folders: list[str] = []
    if vault_root:
        for entry in sorted(vault_root.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                folders.append(entry.name)

    # Also report which Linglepedia-domain folders are present (for routing hints)
    linglepedia_folders_present = [f for f in LINGLEPEDIA_FOLDERS if f in folders]

    return {
        "vault_type": vault_type,
        "vault_root": str(vault_root) if vault_root else None,
        "signals": signals,
        "all_top_level_folders": folders,
        "linglepedia_domain_folders_present": linglepedia_folders_present,
    }


# -----------------------------------------------------------------------------
# compose
# -----------------------------------------------------------------------------

REQUIRED_SPEC_KEYS = [
    "process",        # human-readable name
    "owner",          # bare string or wikilink "[[Person]]"
    "status",         # draft | active | paused | retired
    "tags",           # list of strings; "dmaic" auto-added if missing
    "define_block",   # markdown string for Define section body (no heading)
    "measure_block",
    "analyze_block",
    "improve_block",
    "control_block",
]

DEFAULT_TRUTH_SCORE = 0.5


def compose_spec(spec: dict[str, Any]) -> str:
    """Assemble a DMAIC spec markdown from the spec dict."""
    missing = [k for k in REQUIRED_SPEC_KEYS if k not in spec]
    if missing:
        raise ValueError(f"spec.json is missing required keys: {missing}")

    today = date.today().isoformat()
    process = spec["process"]
    owner = spec["owner"]
    if not (owner.startswith("[[") and owner.endswith("]]")):
        # Wrap bare owner in wikilink for vault consistency.
        owner_yaml = f'"[[{owner}]]"'
    else:
        owner_yaml = f'"{owner}"'

    tags = list(spec["tags"])
    if "dmaic" not in tags:
        tags.insert(0, "dmaic")

    truth_score = spec.get("truth_score", DEFAULT_TRUTH_SCORE)
    created = spec.get("created", today)
    last_reviewed = spec.get("last_reviewed", today)
    status = spec["status"]
    summary = spec.get("summary", "").strip()
    related_extra: list[str] = spec.get("related_extra", [])

    related = ['"[[DMAIC]]"', *[f'"[[{r}]]"' for r in related_extra]]

    fm_lines = [
        "---",
        "type: dmaic-spec",
        f'process: "{process}"',
        f"owner: {owner_yaml}",
        f"status: {status}",
        f"created: {created}",
        f"last_reviewed: {last_reviewed}",
        f"truth_score: {truth_score}",
        "tags:",
        *[f"  - {t}" if t == "dmaic" else f'  - "{t}"' for t in tags],
        "related:",
        *[f"  - {r}" for r in related],
        "---",
    ]

    body_lines = [
        "",
        f"# DMAIC — {process}",
        "",
    ]
    if summary:
        body_lines.extend([f"> {summary}", ""])
    body_lines.extend([
        "---",
        "",
        "## Define",
        "",
        spec["define_block"].strip(),
        "",
        "---",
        "",
        "## Measure",
        "",
        spec["measure_block"].strip(),
        "",
        "---",
        "",
        "## Analyze",
        "",
        spec["analyze_block"].strip(),
        "",
        "---",
        "",
        "## Improve",
        "",
        spec["improve_block"].strip(),
        "",
        "---",
        "",
        "## Control",
        "",
        spec["control_block"].strip(),
        "",
        "---",
        "",
        "## Experiments Log",
        "",
        "| Date | Hypothesis | Result | Decision |",
        "|---|---|---|---|",
        "| | | | |",
        "",
        "---",
        "",
        "## Notes",
        "",
        spec.get("notes_block", "").strip() or "_No additional notes yet._",
        "",
    ])

    return "\n".join(fm_lines + body_lines)


# -----------------------------------------------------------------------------
# validate
# -----------------------------------------------------------------------------

def _section(text: str, name: str) -> str | None:
    """Return the body of a top-level section by heading name, or None.

    Stops at the next H1/H2 heading or end-of-file. Horizontal `---` rules
    inside the section are NOT treated as section endings — many specs use
    them as visual separators between metrics or sub-blocks.
    """
    m = re.search(
        rf"^#{{1,2}}\s+{re.escape(name)}\b.*?(?=^#{{1,2}}\s+\S|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return m.group(0) if m else None


def validate_spec(spec_text: str) -> dict[str, Any]:
    """Run schema checks on a DMAIC spec; return per-check results."""
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, evidence: str = "") -> None:
        checks.append({"check": name, "passed": passed, "evidence": evidence})

    # Frontmatter present
    fm_match = re.match(r"^---\n(.*?)\n---", spec_text, re.DOTALL)
    fm = fm_match.group(1) if fm_match else None
    add("frontmatter_present", fm is not None,
        "ok" if fm else "no '---' delimiters at start of file")

    if fm:
        for field in ["type", "process", "owner", "status", "created",
                       "last_reviewed", "truth_score", "tags", "related"]:
            present = bool(re.search(rf"^{field}\s*:", fm, re.MULTILINE))
            add(f"frontmatter_has_{field}", present,
                "ok" if present else f"missing field: {field}")
        # type must be dmaic-spec
        type_match = re.search(r"^type:\s*(\S+)", fm, re.MULTILINE)
        actual = type_match.group(1) if type_match else "(missing)"
        add("frontmatter_type_is_dmaic_spec", actual == "dmaic-spec",
            f"type = {actual}")
        # related includes [[DMAIC]]
        related_match = re.search(r"^related:.*?(?=^\S|\Z)", fm,
                                   re.MULTILINE | re.DOTALL)
        related_block = related_match.group(0) if related_match else ""
        add("related_includes_dmaic_wikilink",
            "[[DMAIC]]" in related_block,
            "ok" if "[[DMAIC]]" in related_block
                 else "no [[DMAIC]] wikilink in related field")

    # Five sections
    for section_name in ["Define", "Measure", "Analyze", "Improve", "Control"]:
        sect = _section(spec_text, section_name)
        add(f"section_{section_name.lower()}_present", sect is not None,
            "ok" if sect else f"no top-level '## {section_name}' section")

    # Experiments Log
    add("experiments_log_section_present",
        _section(spec_text, "Experiments Log") is not None,
        "ok" if _section(spec_text, "Experiments Log") is not None
             else "no '## Experiments Log' section")

    # Measure has 2–3 metrics
    measure = _section(spec_text, "Measure")
    if measure:
        sub = re.findall(r"^###+\s+(.+)$", measure, re.MULTILINE)
        n = len(sub)
        add("measure_has_2_or_3_metrics", 2 <= n <= 3,
            f"found {n} metric subheadings: {sub}")

        # Each metric has the four required fields
        chunks = re.split(r"^###+\s+", measure, flags=re.MULTILINE)[1:]
        bad: list[str] = []
        for c in chunks:
            first = c.split("\n", 1)[0]
            for field in ["Definition", "Collection", "Baseline", "Target"]:
                if not re.search(rf"\*\*{field}\b|^\s*{field}\s*:",
                                  c, re.MULTILINE | re.IGNORECASE):
                    bad.append(f"'{first.strip()}' missing {field}")
        add("each_metric_has_required_fields", not bad,
            "ok" if not bad else "; ".join(bad))

    # Control has monitoring + recurring review
    control = _section(spec_text, "Control")
    if control:
        has_mon = bool(re.search(r"\b(monitor|cadence|watch|alert)\b",
                                  control, re.IGNORECASE))
        has_review = bool(re.search(r"\b(review|recurring|quarterly|monthly|re-?examine)\b",
                                     control, re.IGNORECASE))
        add("control_has_monitoring_and_review", has_mon and has_review,
            f"monitoring={has_mon}, review={has_review}")

    # Analyze has thresholds
    analyze = _section(spec_text, "Analyze")
    if analyze:
        has_thresh = bool(re.search(r"\b(threshold|green|yellow|red|trigger)\b",
                                     analyze, re.IGNORECASE))
        add("analyze_has_thresholds", has_thresh,
            "ok" if has_thresh else "no threshold language in Analyze")

    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    return {
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "all_passed": passed == total,
        "checks": checks,
    }


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(prog="dmaic.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_dv = sub.add_parser("detect-vault",
                          help="Detect Obsidian/Linglepedia vault from cwd")
    p_dv.add_argument("--cwd", default=".",
                       help="Starting directory (default: current dir)")

    p_co = sub.add_parser("compose",
                          help="Compose a DMAIC spec markdown from spec.json")
    p_co.add_argument("--input", required=True, help="Path to spec.json")
    p_co.add_argument("--output", required=True,
                       help="Path to write the resulting .md file")
    p_co.add_argument("--validate-after", action="store_true",
                       help="Also run validate on the composed file")

    p_va = sub.add_parser("validate",
                          help="Validate a DMAIC spec markdown file")
    p_va.add_argument("--file", required=True, help="Path to the spec .md")
    p_va.add_argument("--strict", action="store_true",
                       help="Exit 1 if any check fails")

    args = parser.parse_args()

    if args.cmd == "detect-vault":
        result = detect_vault(Path(args.cwd))
        print(json.dumps(result, indent=2))
        return 0

    if args.cmd == "compose":
        spec = json.loads(Path(args.input).read_text())
        md = compose_spec(spec)
        Path(args.output).write_text(md)
        print(json.dumps({
            "wrote": args.output,
            "bytes": len(md),
        }, indent=2))
        if args.validate_after:
            result = validate_spec(md)
            print(json.dumps(result, indent=2))
            if not result["all_passed"]:
                return 1
        return 0

    if args.cmd == "validate":
        text = Path(args.file).read_text()
        result = validate_spec(text)
        print(json.dumps(result, indent=2))
        if args.strict and not result["all_passed"]:
            return 1
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
