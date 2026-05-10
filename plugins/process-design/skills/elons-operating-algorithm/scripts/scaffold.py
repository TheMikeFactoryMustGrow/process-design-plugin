#!/usr/bin/env python3
"""
elon-pressure-test scaffolding helper.

Subcommands:

  detect-vault         Walk up from --cwd; identify Obsidian / Linglepedia / none.
                       Same routing logic as the dmaic skill so pressure tests
                       file alongside other vault notes consistently.
  resolve-path         Pick the output file path for a pressure test, given the
                       subject (and optionally the source file under review).
                       Honours the case-insensitive collision check Mike's
                       memory file calls out for APFS.
  scaffold             Emit the full markdown skeleton (frontmatter + 5 step
                       sections + add-back log + open questions) for the agent
                       to fill in. Writes to --output, refuses to overwrite
                       unless --force.
  validate             Schema-check a completed pressure-test note. Returns
                       per-check results as JSON. --strict exits 1 on failure.

Self-contained — no third-party dependencies. Python 3.8+.
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
# detect-vault — copied from dmaic.py for consistency
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

    if vault_root and vault_type == "obsidian" and (vault_root / "_schemas").is_dir():
        vault_type = "linglepedia"
        signals.append("_schemas/ also present")

    folders: list[str] = []
    if vault_root:
        for entry in sorted(vault_root.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                folders.append(entry.name)

    linglepedia_folders_present = [f for f in LINGLEPEDIA_FOLDERS if f in folders]

    return {
        "vault_type": vault_type,
        "vault_root": str(vault_root) if vault_root else None,
        "signals": signals,
        "all_top_level_folders": folders,
        "linglepedia_domain_folders_present": linglepedia_folders_present,
    }


# -----------------------------------------------------------------------------
# resolve-path
# -----------------------------------------------------------------------------

_SLUG_BAD = re.compile(r"[^a-z0-9]+")


def slugify(subject: str) -> str:
    s = _SLUG_BAD.sub("-", subject.lower()).strip("-")
    return s or "pressure-test"


def case_insensitive_exists(path: Path) -> Path | None:
    """Return the existing path that case-insensitively matches `path`, if any.

    On APFS, `Foo.md` and `FOO.md` collide. A direct `path.exists()` check is
    case-sensitive at the Python layer even though the filesystem isn't, so we
    enumerate the parent directory and match case-insensitively. Per Mike's
    `feedback_case_insensitive_filenames.md` memory: never `rm` to "dedup"
    these — surface the collision and let the user pick a slug.
    """
    parent = path.parent
    if not parent.is_dir():
        return None
    target_lower = path.name.lower()
    for entry in parent.iterdir():
        if entry.name.lower() == target_lower:
            return entry
    return None


def resolve_path(subject: str, source: str | None, cwd: Path) -> dict[str, Any]:
    """Pick the output path for a pressure test.

    Rules (in order):
      1. If `source` is a real file path, write next to it: <source>-pressure-test.md
      2. If we're inside a Linglepedia vault, write to:
           <vault>/Values and Mechanisms/Reviews/<slug>-pressure-test.md
      3. Otherwise write to the current directory: ./<slug>-pressure-test.md

    Always honours the case-insensitive collision check.
    """
    slug = slugify(subject)

    chosen: Path
    why: str

    if source:
        src = Path(source).expanduser().resolve()
        if src.is_file():
            chosen = src.with_name(src.stem + "-pressure-test.md")
            why = f"alongside source file {src}"
        else:
            # Source given but doesn't exist as a file — fall through to vault/cwd
            src = None  # type: ignore[assignment]

    if 'chosen' not in dir():
        vault = detect_vault(cwd)
        if vault["vault_type"] == "linglepedia":
            reviews_dir = Path(vault["vault_root"]) / "Values and Mechanisms" / "Reviews"
            chosen = reviews_dir / f"{slug}-pressure-test.md"
            why = f"in vault Reviews/ folder ({reviews_dir})"
        else:
            chosen = cwd.resolve() / f"{slug}-pressure-test.md"
            why = f"in current working directory ({cwd.resolve()})"

    collision = case_insensitive_exists(chosen)
    return {
        "path": str(chosen),
        "slug": slug,
        "reason": why,
        "exists_case_insensitive": collision is not None,
        "existing_path": str(collision) if collision else None,
    }


# -----------------------------------------------------------------------------
# scaffold — full markdown skeleton
# -----------------------------------------------------------------------------

_FRONTMATTER = """\
---
type: pressure-test
subject: "{subject}"
fitness-metric: "{fitness_metric}"
status: draft
version: 1
created: {today}
updated: {today}
method: Elon's Operating Algorithm pressure test
author: "[[Mike Lingle]]"
tags:
{tags_yaml}
related-docs:
{related_yaml}
is_canonical: false
truth_score: agent-populated
last_verified: {today}
---
"""

_SKELETON = """\

# {title}

> **Method:** Elon's Operating Algorithm. Each requirement, component, and decision in {subject} is treated as a hypothesis that must justify itself against the fitness metric. The 5 steps run in strict order — questioning and deletion before simplification, simplification before acceleration, acceleration before automation.

> **Fitness metric:** {fitness_metric}

---

## 0. Fitness metric

<2–3 sentences expanding on the metric. Why this metric and not another. What "moves the needle" looks like in concrete terms. If multiple metrics were in tension, name the tradeoff and pick one as primary.>

---

## 1. Step 1 — Question Every Requirement

> *"Every requirement must trace to a named person. The more senior the person, the more dangerous the requirement, because people are less likely to question it."*

### 1.1 Requirements that survive questioning

| Requirement | Who required it? | Justification | Verdict |
|---|---|---|---|
| <requirement> | <[[Person]]> | <why it serves the fitness metric> | **KEEP** |

### 1.2 Requirements that need harder questioning

| Requirement | Who required it? | Challenge | Recommendation |
|---|---|---|---|
| <requirement> | <[[Person]] or "(unattributed)"> | <specific challenge> | **QUESTION / DECOUPLE / DEFER / DELETE / SIMPLIFY** |

### 1.3 The deepest question

<One paragraph reframing the artifact's premise. Every pressure test should produce one of these.>

---

## 2. Step 2 — Delete Any Part or Process

> *"If you aren't adding back at least 10% of what you delete, you're not deleting enough."*

### 2.1 Candidates for deletion

| Component / step / story | Current status | Verdict | Reasoning |
|---|---|---|---|
| <name> | <where it lives in the source> | **DELETE / DEFER / DECOUPLE / SIMPLIFY** | <why> |

### 2.2 What survives deletion

<Numbered list — the compressed deliverable.>

1. <Surviving piece 1>

---

## 3. Step 3 — Simplify and Optimize

> *"The most common error is optimizing something that shouldn't exist."*

### 3.1 Simplification targets

- **<piece>:** <current shape> → <simpler shape>. <one-line rationale>.

---

## 4. Step 4 — Accelerate Cycle Time

> *"Speed up every process — but only after you've deleted what shouldn't exist."*

### 4.1 Cycle-time levers

- <lever>: <expected effect on the fitness metric>.

---

## 5. Step 5 — Automate

> *"Last, not first. Automating waste produces waste faster."*

### 5.1 Automation candidates (deferred)

- <process>: automate when <condition>.

---

## Add-back log

<Items deleted in §2 that were reinstated by the end of the pressure test. Aim for ~10% of deletions.>

- <item>: deleted in §2 because <reason>; added back because <new reason>.

---

## Open questions

<Each addressed to a named person with a date.>

- For <[[Person]]>, by <YYYY-MM-DD>: <question>.
"""


def scaffold(subject: str, fitness_metric: str, source_link: str | None,
             extra_tags: list[str]) -> str:
    today = date.today().isoformat()

    tags = ["pressure-test", "operating-algorithm", *extra_tags]
    tags_yaml = "\n".join(f"  - {t}" for t in tags)

    related = ['  - "[[Elon\'s Operating Algorithm]]"']
    if source_link:
        # Caller passes either a bare title or already-wrapped "[[Foo]]"
        if "[[" in source_link and "]]" in source_link:
            related.append(f'  - "{source_link}"')
        else:
            related.append(f'  - "[[{source_link}]]"')
    related_yaml = "\n".join(related)

    fm = _FRONTMATTER.format(
        subject=subject,
        fitness_metric=fitness_metric,
        today=today,
        tags_yaml=tags_yaml,
        related_yaml=related_yaml,
    )
    body = _SKELETON.format(
        title=f"{subject} — Pressure Test",
        subject=subject,
        fitness_metric=fitness_metric,
    )
    return fm + body


# -----------------------------------------------------------------------------
# validate
# -----------------------------------------------------------------------------

REQUIRED_FRONTMATTER_FIELDS = [
    "type", "subject", "fitness-metric", "status", "created", "updated",
    "method", "tags", "related-docs", "is_canonical", "truth_score",
    "last_verified",
]

REQUIRED_SECTIONS = [
    ("0. Fitness metric", r"^##\s+0\.\s+Fitness metric"),
    ("1. Step 1 — Question Every Requirement", r"^##\s+1\.\s+Step\s*1"),
    ("1.1 Requirements that survive questioning", r"^###\s+1\.1\b"),
    ("1.2 Requirements that need harder questioning", r"^###\s+1\.2\b"),
    ("1.3 The deepest question", r"^###\s+1\.3\b"),
    ("2. Step 2 — Delete Any Part or Process", r"^##\s+2\.\s+Step\s*2"),
    ("2.1 Candidates for deletion", r"^###\s+2\.1\b"),
    ("2.2 What survives deletion", r"^###\s+2\.2\b"),
    ("3. Step 3 — Simplify and Optimize", r"^##\s+3\.\s+Step\s*3"),
    ("4. Step 4 — Accelerate Cycle Time", r"^##\s+4\.\s+Step\s*4"),
    ("5. Step 5 — Automate", r"^##\s+5\.\s+Step\s*5"),
    ("Add-back log", r"^##\s+Add-back log"),
    ("Open questions", r"^##\s+Open questions"),
]

_PLACEHOLDER = re.compile(r"<[a-z][a-z0-9_\-/.,'\" ]{0,80}>")

# Match a single verdict in **bold**. The pressure-test scaffold lists every
# verdict alternative inside one set of bold markers (e.g.
# `**QUESTION / DECOUPLE / DEFER / DELETE / SIMPLIFY**`); that is the unfilled
# placeholder shape and must NOT count as a landed verdict. Only a bold span
# whose contents are a single verdict word counts.
_LONE_VERDICT = re.compile(
    r"\*\*\s*(KEEP|QUESTION|DECOUPLE|DEFER|DELETE|SIMPLIFY)\s*\*\*"
)
_MULTI_VERDICT = re.compile(
    r"\*\*[^*]*\b(?:KEEP|QUESTION|DECOUPLE|DEFER|DELETE|SIMPLIFY)\b[^*]*"
    r"(?:/|,|\|)[^*]*\b(?:KEEP|QUESTION|DECOUPLE|DEFER|DELETE|SIMPLIFY)\b[^*]*\*\*"
)


def _cell_is_placeholder(cell: str) -> bool:
    """A table cell counts as a placeholder if it's empty, wrapped in <...>,
    or is a multi-verdict marker (e.g. `**KEEP / DELETE**` from the scaffold).

    Real cells have content the agent wrote — even short content counts.
    """
    s = cell.strip()
    if not s:
        return True
    # Whole-cell <placeholder>
    if _PLACEHOLDER.fullmatch(s):
        return True
    # The scaffold's Step 1 row uses `<[[Person]] or "(unattributed)">` — a
    # placeholder containing nested quotes / brackets. The strict fullmatch
    # above won't catch it because of the nested chars; check a second time
    # with a permissive pattern for cells that begin with `<` and end with `>`.
    if s.startswith("<") and s.endswith(">"):
        return True
    # Multi-verdict marker (the scaffold's "**A / B / C**" shape)
    if _MULTI_VERDICT.fullmatch(s):
        return True
    return False


def _section_body(text: str, anchor_pattern: str) -> str | None:
    """Return the body of the section matching anchor_pattern through the next
    section at the same level (or end-of-file)."""
    head_re = re.compile(anchor_pattern, re.MULTILINE)
    m = head_re.search(text)
    if not m:
        return None
    start = m.start()
    # Find the next heading of equal or higher level
    level = 0
    while m.group()[level] == "#":
        level += 1
    next_re = re.compile(rf"^#{{1,{level}}}\s", re.MULTILINE)
    rest = text[m.end():]
    n = next_re.search(rest)
    end = m.end() + n.start() if n else len(text)
    return text[start:end]


def _table_data_rows(section_text: str) -> int:
    """Count data rows in markdown tables inside the section.

    A data row is a `|...|` line that:
      - is not the header row (we skip the first | line per table)
      - is not the separator row (`|---|---|`)
      - is not a placeholder-only row (every cell wrapped in <...>)
    """
    rows = 0
    in_table = False
    seen_header = False
    seen_sep = False
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
                seen_header = True
                seen_sep = False
                continue
            if seen_header and not seen_sep:
                if re.match(r"^\|[\s\-:|]+\|$", stripped):
                    seen_sep = True
                    continue
            # Data row — but skip if every cell is a placeholder, or if MOST
            # cells are placeholders (the scaffold ships with one fake row
            # whose verdict cell is a multi-verdict marker but whose other
            # cells are <...> placeholders; we want to treat that as empty).
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            real_cells = [c for c in cells if not _cell_is_placeholder(c)]
            # Need at least 2 real cells to count as a filled-in row. A single
            # filled cell in a 4-column table is almost certainly a half-edit.
            if len(real_cells) >= 2:
                rows += 1
        else:
            if in_table and not stripped:
                # Blank line — table ended
                in_table = False
                seen_header = False
                seen_sep = False
            elif in_table:
                in_table = False
                seen_header = False
                seen_sep = False
    return rows


def validate(text: str) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, evidence: str = "") -> None:
        checks.append({"check": name, "passed": passed, "evidence": evidence})

    # Frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    fm = fm_match.group(1) if fm_match else None
    add("frontmatter_present", fm is not None,
        "ok" if fm else "no '---' delimiters at start of file")

    if fm:
        for field in REQUIRED_FRONTMATTER_FIELDS:
            present = bool(re.search(rf"^{re.escape(field)}\s*:", fm, re.MULTILINE))
            add(f"frontmatter_has_{field.replace('-', '_')}", present,
                "ok" if present else f"missing field: {field}")
        type_match = re.search(r"^type:\s*(\S+)", fm, re.MULTILINE)
        actual = type_match.group(1) if type_match else "(missing)"
        add("frontmatter_type_is_pressure_test", actual == "pressure-test",
            f"type = {actual}")
        # fitness-metric must be non-empty and not a placeholder
        fm_match = re.search(r'^fitness-metric:\s*"?([^"\n]*)"?', fm, re.MULTILINE)
        fm_value = fm_match.group(1).strip() if fm_match else ""
        is_real = bool(fm_value) and not _PLACEHOLDER.fullmatch(fm_value)
        add("fitness_metric_is_filled", is_real,
            "ok" if is_real else f"fitness-metric is empty or a <placeholder>: {fm_value!r}")
        # related-docs includes the algorithm wikilink
        related_match = re.search(r"^related-docs:.*?(?=^\S|\Z)", fm,
                                   re.MULTILINE | re.DOTALL)
        related_block = related_match.group(0) if related_match else ""
        add("related_includes_algorithm_wikilink",
            "[[Elon's Operating Algorithm]]" in related_block,
            "ok" if "[[Elon's Operating Algorithm]]" in related_block
                 else "no [[Elon's Operating Algorithm]] wikilink in related-docs")

    # Section presence
    for label, pattern in REQUIRED_SECTIONS:
        present = re.search(pattern, text, re.MULTILINE) is not None
        # Slug for the check name (lowercase letters/digits, dash separators)
        slug = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
        add(f"section_{slug}_present", present,
            "ok" if present else f"missing section: {label}")

    # Step 1.2 must have at least one filled-in row
    s12 = _section_body(text, r"^###\s+1\.2\b")
    if s12 is not None:
        n12 = _table_data_rows(s12)
        add("step_1_2_has_at_least_one_real_row", n12 >= 1,
            f"found {n12} non-placeholder data rows in 1.2")

    # Step 2.1 must have at least one filled-in row
    s21 = _section_body(text, r"^###\s+2\.1\b")
    if s21 is not None:
        n21 = _table_data_rows(s21)
        add("step_2_1_has_at_least_one_real_row", n21 >= 1,
            f"found {n21} non-placeholder data rows in 2.1")

    # Step 2.2 ("What survives") must have at least one numbered item
    s22 = _section_body(text, r"^###\s+2\.2\b")
    if s22 is not None:
        survivors = re.findall(r"^\s*\d+\.\s+(?!<).+", s22, re.MULTILINE)
        add("step_2_2_has_named_survivors", len(survivors) >= 1,
            f"found {len(survivors)} numbered survivor lines (excluding <placeholder> rows)")

    # At least one *single* verdict landed in the body. The scaffold's
    # multi-verdict markers (e.g. **A / B / C**) don't count — they're
    # placeholders. Use _LONE_VERDICT to catch only solo bold spans.
    body_after_h1 = re.split(r"^# ", text, flags=re.MULTILINE, maxsplit=2)
    body_text = body_after_h1[-1] if body_after_h1 else text
    # Find spans containing a verdict but exclude those inside multi-verdict markers
    multi_spans = [(m.start(), m.end()) for m in _MULTI_VERDICT.finditer(body_text)]

    def _in_multi(pos: int) -> bool:
        return any(s <= pos < e for s, e in multi_spans)

    verdicts_used: set[str] = set()
    for m in _LONE_VERDICT.finditer(body_text):
        if not _in_multi(m.start()):
            verdicts_used.add(m.group(1))
    # Require ≥2 distinct verdicts. A pressure test in which only KEEP appears
    # has nothing to delete and is, by the algorithm's own definition,
    # under-deleted. The scaffold ships with only **KEEP** in 1.1, so this
    # gate also forces the agent to actually fill in 1.2 / 2.1 with a real
    # verdict (DELETE / DEFER / DECOUPLE / SIMPLIFY / QUESTION).
    add("at_least_two_distinct_verdicts_used", len(verdicts_used) >= 2,
        f"verdicts used: {sorted(verdicts_used) or 'none'}")

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
    parser = argparse.ArgumentParser(prog="scaffold.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_dv = sub.add_parser("detect-vault",
                          help="Detect Obsidian/Linglepedia vault from cwd")
    p_dv.add_argument("--cwd", default=".",
                       help="Starting directory (default: current dir)")

    p_rp = sub.add_parser("resolve-path",
                          help="Pick the output path for a pressure-test note")
    p_rp.add_argument("--subject", required=True, help="Short subject name")
    p_rp.add_argument("--source", default="",
                       help="Path to source artifact (optional)")
    p_rp.add_argument("--cwd", default=".",
                       help="Starting directory (default: current dir)")

    p_sc = sub.add_parser("scaffold",
                          help="Write the pressure-test skeleton to --output")
    p_sc.add_argument("--subject", required=True,
                       help="Subject of the pressure test")
    p_sc.add_argument("--fitness-metric", required=True,
                       help="One-sentence fitness metric")
    p_sc.add_argument("--source-link", default="",
                       help="Optional vault title to wikilink in related-docs")
    p_sc.add_argument("--extra-tags", default="",
                       help="Comma-separated extra tags to add")
    p_sc.add_argument("--output", required=True,
                       help="Path to write the skeleton .md file")
    p_sc.add_argument("--force", action="store_true",
                       help="Overwrite the output file if it already exists "
                            "(otherwise refuse on case-insensitive match)")

    p_va = sub.add_parser("validate",
                          help="Validate a completed pressure-test note")
    p_va.add_argument("--file", required=True, help="Path to the .md file")
    p_va.add_argument("--strict", action="store_true",
                       help="Exit 1 if any check fails")

    args = parser.parse_args()

    if args.cmd == "detect-vault":
        result = detect_vault(Path(args.cwd))
        print(json.dumps(result, indent=2))
        return 0

    if args.cmd == "resolve-path":
        result = resolve_path(args.subject, args.source or None, Path(args.cwd))
        print(json.dumps(result, indent=2))
        return 0

    if args.cmd == "scaffold":
        out_path = Path(args.output).expanduser()
        collision = case_insensitive_exists(out_path)
        if collision and not args.force:
            print(json.dumps({
                "error": "output file already exists (case-insensitive)",
                "requested_path": str(out_path),
                "existing_path": str(collision),
                "hint": "pass --force to overwrite, or pick a different --output",
            }, indent=2), file=sys.stderr)
            return 1
        extra_tags = [t.strip() for t in args.extra_tags.split(",") if t.strip()]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        md = scaffold(args.subject, args.fitness_metric,
                       args.source_link or None, extra_tags)
        out_path.write_text(md)
        print(json.dumps({
            "wrote": str(out_path),
            "bytes": len(md),
        }, indent=2))
        return 0

    if args.cmd == "validate":
        text = Path(args.file).read_text()
        result = validate(text)
        print(json.dumps(result, indent=2))
        if args.strict and not result["all_passed"]:
            return 1
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
