#!/usr/bin/env python3
"""
DMAIC orchestrator helper script.

Subcommands:

  detect-vault         Walk up from --cwd; identify Obsidian / Linglepedia / none.
  prefill              Emit a JSON skeleton with required keys + sensible
                       defaults; agent fills phase blocks.
  scaffold             Emit a markdown template for one phase (measure,
                       analyze, improve, control, define) with the right
                       number of metric / experiment slots. Replaces the
                       per-phase SKILL.md output-format prose.
  compose              Assemble a spec.json into a complete DMAIC spec .md.
                       Refuses to overwrite existing files unless --force.
  validate             Schema-check an existing spec; --strict-metrics adds
                       structural checks on metric units / baselines /
                       targets; --strict exits non-zero on any failure.
  check-causal-chain   Verify the Analyze section names ≥1 controllable
                       input per output metric — the headline G4 check.
  validate-owner       Reject department-shaped owner names ("the team",
                       "operations") that defeat individual accountability.

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
    # Wrap bare owner in wikilink for vault consistency. Detect any existing
    # `[[...]]` occurrence — not just whole-string match — so values like
    # "[[Mike]] (interim)" don't get wrapped a second time.
    if "[[" in owner and "]]" in owner:
        owner_yaml = f'"{owner}"'
    else:
        owner_yaml = f'"[[{owner}]]"'

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

    # If the agent pasted a per-phase block that itself begins with `## Phase`
    # (e.g. from a per-phase skill's standalone Output format), strip the
    # leading H2 so we don't end up with two `## Define` rows.
    #
    # Two guards:
    #   - Require the H2 to be followed by whitespace or end-of-line, so
    #     `## ImproveSomething` is NOT stripped to `Something`.
    #   - If stripping would leave the block empty, return the original
    #     block — better to write `## Define\n\n## Define` (caught by
    #     validator) than silently produce an empty section.
    def _strip_h2(block: str, phase_name: str) -> str:
        stripped = block.strip()
        # If the block is empty after strip, emit a visible placeholder rather
        # than producing an empty section that quietly passes section_present.
        if not stripped:
            return f"_(empty — fill in the {phase_name} block before promoting)_"
        # Match `## Phase` followed by whitespace or end-of-string only — so
        # `## ImproveSomething` is NOT stripped.
        m = re.match(rf"^##\s+{re.escape(phase_name)}(?=\s|$)", stripped)
        if not m:
            return stripped
        candidate = stripped[m.end():].lstrip("\n").strip()
        if not candidate:
            return f"_(empty — the {phase_name} block contained only its heading; fill in content before promoting)_"
        return candidate

    body_lines.extend([
        "---",
        "",
        "## Define",
        "",
        _strip_h2(spec["define_block"], "Define"),
        "",
        "---",
        "",
        "## Measure",
        "",
        _strip_h2(spec["measure_block"], "Measure"),
        "",
        "---",
        "",
        "## Analyze",
        "",
        _strip_h2(spec["analyze_block"], "Analyze"),
        "",
        "---",
        "",
        "## Improve",
        "",
        _strip_h2(spec["improve_block"], "Improve"),
        "",
        "---",
        "",
        "## Control",
        "",
        _strip_h2(spec["control_block"], "Control"),
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

def _split_metric_categories(measure_text: str) -> dict[str, list[dict[str, str]]]:
    """Parse the Measure section into the three category buckets.

    Looks for `### Output Metrics`, `### Controllable Input Metrics`,
    `### External Input Metrics` H3 headings, and within each, parses
    `#### Metric N: name` H4 blocks.

    Returns {"output": [...], "controllable": [...], "external": [...]} where
    each metric is {"name": str, "body": str}.

    Tolerates older flat structure: if no H3 categories are found, every
    `### Metric N` block is treated as output (legacy fallback).
    """
    out: dict[str, list[dict[str, str]]] = {
        "output": [], "controllable": [], "external": [],
    }

    def _is_category(head_lower: str) -> str | None:
        if "output metric" in head_lower:
            return "output"
        if "controllable input metric" in head_lower:
            return "controllable"
        if "external input metric" in head_lower:
            return "external"
        return None

    # Pre-scan: are ANY of the three category H3s present?
    h3_sections = re.split(r"^###\s+", measure_text, flags=re.MULTILINE)
    has_categories = any(
        _is_category(chunk.split("\n", 1)[0].strip().lower())
        for chunk in h3_sections[1:]
    )

    if not has_categories:
        # Legacy mode: no category H3s at all. Two sub-modes:
        #   1. ### Metric N blocks (older flat-H3 specs) → each H3 is an output
        #   2. #### Metric N directly under ## Measure (no H3s at all) → each H4 is an output
        if len(h3_sections) > 1:
            for chunk in h3_sections[1:]:
                first_line = chunk.split("\n", 1)[0].strip()
                body = chunk.split("\n", 1)[1] if "\n" in chunk else ""
                out["output"].append({"name": first_line, "body": body})
        else:
            h4_blocks = re.split(r"^####\s+", measure_text, flags=re.MULTILINE)
            for h4 in h4_blocks[1:]:
                metric_first = h4.split("\n", 1)[0].strip()
                metric_body = h4.split("\n", 1)[1] if "\n" in h4 else ""
                out["output"].append({"name": metric_first, "body": metric_body})
        return out

    # New mode: at least one category H3 found. Walk H3 sections; non-category
    # H3s (e.g. `### Notes`, `### Context`) are IGNORED — not silently
    # mis-attributed to outputs. This fixes the iter-3 random-H3 mis-attribution.
    for chunk in h3_sections[1:]:
        first_line = chunk.split("\n", 1)[0].strip()
        body = chunk.split("\n", 1)[1] if "\n" in chunk else ""
        cat = _is_category(first_line.lower())
        if cat is None:
            continue  # ignore non-category H3s
        h4_blocks = re.split(r"^####\s+", body, flags=re.MULTILINE)
        for h4 in h4_blocks[1:]:
            metric_first = h4.split("\n", 1)[0].strip()
            metric_body = h4.split("\n", 1)[1] if "\n" in h4 else ""
            out[cat].append({"name": metric_first, "body": metric_body})
    return out


# Case-sensitive on purpose: real placeholders are lowercase tokens
# (`<units>`, `[details TBD]`); legitimate uppercased references like
# `[Q1 2026]` should NOT trigger the placeholder rejector. Keep IGNORECASE off.
_INLINE_PLACEHOLDER = re.compile(
    r"<[a-z][a-z0-9_\- ]{0,30}>|\[[a-z][a-z0-9_\- ]{0,30}\]"
)


def _metric_field_has_value(metric_body: str, field: str, allow_na: bool) -> bool:
    """Check that a metric body has `Field:` followed by a non-placeholder value.

    Accepts both `**Field:**` (canonical, template form) and `**Field**:` and
    bare `Field:` shapes. The post-colon value must be non-empty and contain
    no `<placeholder>` or `[placeholder]` substrings — even partial values
    like `Net Revenue Retention <units>` are rejected. When allow_na, the
    literal 'N/A' (case-insensitive) is also accepted.
    """
    pattern = re.compile(
        rf"(?:\*\*{field}\*\*\s*:|\*\*{field}:\*\*|^\s*{field}\s*:)\s*(\S[^\n]*)",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(metric_body)
    if not match:
        return False
    value = match.group(1).strip()
    # If the entire value is italic (e.g. `_N/A — track only_` from the
    # template), strip just the italic markers to expose the inner text.
    # Otherwise, strip trailing italic ANNOTATIONS only — content stays.
    italic_only_match = re.fullmatch(r"_(.+)_", value) or re.fullmatch(r"\*(.+)\*", value)
    if italic_only_match:
        bare = italic_only_match.group(1).strip()
    else:
        bare = re.sub(r"_[^_]+_$", "", value).strip()
        bare = re.sub(r"\*[^*]+\*$", "", bare).strip()
    if not bare:
        return False
    # Whole-string placeholder
    if (bare.startswith("<") and bare.endswith(">")) or (bare.startswith("[") and bare.endswith("]")):
        return False
    # Inline / partial placeholder substrings (e.g. `Net Revenue Retention <units>`).
    # Any `<lowercase-thing>` or `[lowercase-thing]` of plausible placeholder shape
    # means the agent left something unfilled — fail.
    if _INLINE_PLACEHOLDER.search(bare):
        return False
    if allow_na and bare.upper().startswith("N/A"):
        return True
    # Reject explicit empty placeholders.
    if bare.upper() in ("TBD", "TBA", "?"):
        return False
    return True


def _section(text: str, name: str) -> str | None:
    """Return the body of a top-level section by heading name, or None.

    Section boundary rules:
    - Compose-output specs separate phases with `---` horizontal rules between
      `## Phase` headings, so the canonical end-of-section marker is the
      `---` divider followed by the next `## Phase` header (or end-of-file).
    - We deliberately do NOT stop at any random H1/H2 inside the body — agents
      can write `## Recent Experiments` inside Improve, `## Notes` inside
      Control, etc., and validators must still see the full body.
    - Inner `---` rules (between metrics, between sub-sections) DO NOT close
      the section; only `---` followed by `## ` (with a phase name) does.
    """
    pattern = re.compile(
        rf"^#{{1,2}}\s+{re.escape(name)}\b.*?(?=^---\s*$\n##\s+\S|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
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

    # Measure: split into the three category sub-sections and validate each
    # appropriately. 2–3 cap applies to OUTPUT metrics only; controllable +
    # external have no cap. External metric Targets are N/A.
    measure = _section(spec_text, "Measure")
    if measure:
        categories = _split_metric_categories(measure)
        # Output metric count: 1–3 allowed (the prose says "cap at 2–3" — that
        # was an upper bound, not a minimum). Single-output specs are valid
        # when one terminal measure genuinely captures process success.
        outputs = categories["output"]
        n_outputs = len(outputs)
        add("measure_has_1_to_3_outputs", 1 <= n_outputs <= 3,
            f"found {n_outputs} output metrics: {[m['name'] for m in outputs]}")
        # Controllable inputs: at least 1 expected, no upper bound.
        controllable = categories["controllable"]
        add("measure_has_at_least_one_controllable_input",
            len(controllable) >= 1,
            f"found {len(controllable)} controllable input metrics")

        # Per-metric content checks — colon-inside-bold form is the canonical
        # one (the template ships `**Definition:**`).
        bad: list[str] = []
        for category, metrics in categories.items():
            required = ["Definition", "Collection", "Baseline"]
            # Targets are required for output + controllable, not external.
            if category != "external":
                required.append("Target")
            for m in metrics:
                for field in required:
                    if not _metric_field_has_value(m["body"], field, allow_na=False):
                        bad.append(f"[{category}] '{m['name']}' missing or empty {field}")
                # External Targets allowed N/A; verify the field is at least
                # present even if N/A.
                if category == "external":
                    if not _metric_field_has_value(m["body"], "Target", allow_na=True):
                        bad.append(f"[external] '{m['name']}' missing Target line (N/A is allowed but the line must exist)")
        add("each_metric_has_required_fields_with_content", not bad,
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
# strict-metrics structural checks
# -----------------------------------------------------------------------------

# A metric Definition should mention units. We accept any unit-shaped token
# (currency, percent, time, count words). This is a heuristic; the agent gets
# to override with --strict-metrics-skip.
_UNIT_TOKENS = re.compile(
    r"(?:%|\$|€|£|¥|\bbps\b|\bms\b|\bsec(?:onds?)?\b|\bmin(?:utes?)?\b|"
    r"\bhours?\b|\bdays?\b|\bweeks?\b|\bmonths?\b|\bper\b|\bcount\b|"
    r"\bratio\b|\brate\b|\bscore\b|\busers?\b|\brequests?\b|\bevents?\b|"
    r"\bdollars?\b|\b\d+(?:\.\d+)?\s*(?:k|m|b|x)\b)",
    re.IGNORECASE,
)

# Baseline / Target values. Numeric, percent, currency, or the explicit
# "unknown — establish by ..." escape hatch the SKILL.md defines.
_VALUE_TOKEN = re.compile(
    r"(\d+(?:\.\d+)?\s*%?|\$\d+|\bunknown\b\s*[—–-]\s*establish\b)",
    re.IGNORECASE,
)


def strict_metric_checks(measure_text: str) -> list[dict[str, Any]]:
    """Per-metric structural checks beyond presence: each Definition mentions
    units; each Baseline is a value or the "unknown — establish" escape; each
    Target is a value (or `N/A` for external inputs).

    Walks the 3-category structure when present so external metric Targets
    are correctly waived from the value-shape requirement.
    """
    failures: list[dict[str, Any]] = []
    categories = _split_metric_categories(measure_text)
    # Either we found categories (new format) or we got an empty dict — fall
    # back to flat-list reading if no categories were parsed.
    flat: list[tuple[str, str, str]] = []  # (category, name, body)
    if any(categories.values()):
        for category, metrics in categories.items():
            for m in metrics:
                flat.append((category, m["name"], m["body"]))
    else:
        # Legacy fallback: every ### block is an output.
        chunks = re.split(r"^###+\s+", measure_text, flags=re.MULTILINE)[1:]
        for c in chunks:
            first = c.split("\n", 1)[0].strip()
            body = c.split("\n", 1)[1] if "\n" in c else ""
            flat.append(("output", first, body))

    for category, name, body in flat:
        # Gate every check on the placeholder rejector first — a value like
        # `<how it's calculated, with units (%, ms, $, count, etc.)>` literally
        # contains unit tokens AND `unknown — establish`, so the unit/value
        # regex pre-iter-3 false-passed it. Now we use the same
        # _metric_field_has_value contract `validate_spec` uses, so the two
        # layers agree on what "filled in" means.
        for field in ["Definition", "Baseline"]:
            if not _metric_field_has_value(body, field, allow_na=False):
                failures.append({
                    "metric": f"[{category}] {name}",
                    "check": f"{field.lower()}_filled_not_placeholder",
                    "evidence": "field is missing, empty, or still a <placeholder>/[placeholder]/TBD",
                })
        # Target: external metrics may use N/A — track only; others must be a value.
        if not _metric_field_has_value(body, "Target", allow_na=(category == "external")):
            failures.append({
                "metric": f"[{category}] {name}",
                "check": "target_filled_not_placeholder",
                "evidence": ("for external metrics, value or 'N/A — track only' is required; "
                             "for output/controllable, a numeric/percent/currency value is required"),
            })
        # Skip downstream regex checks if any field was a placeholder — the
        # earlier layer already failed; running unit/value-shape on placeholder
        # text is the iter-2 false-pass mode.
        any_placeholder = any(
            f["metric"] == f"[{category}] {name}" for f in failures
        )
        if any_placeholder:
            continue
        # Definition has units? Now safe — we know it's not a placeholder.
        def_match = re.search(
            r"\*\*Definition\*\*\s*:|\*\*Definition:\*\*|^\s*Definition\s*:",
            body, re.MULTILINE | re.IGNORECASE,
        )
        if def_match:
            after = body[def_match.end():].split("\n", 1)[0]
            if not _UNIT_TOKENS.search(after):
                failures.append({"metric": f"[{category}] {name}",
                                 "check": "definition_has_units",
                                 "evidence": after.strip()[:80]})
        # Baseline shape
        base_match = re.search(
            r"\*\*Baseline\*\*\s*:|\*\*Baseline:\*\*|^\s*Baseline\s*:",
            body, re.MULTILINE | re.IGNORECASE,
        )
        if base_match:
            after = body[base_match.end():].split("\n", 1)[0]
            if not _VALUE_TOKEN.search(after):
                failures.append({"metric": f"[{category}] {name}",
                                 "check": "baseline_value_shape",
                                 "evidence": after.strip()[:80]})
        # Target shape — same per-category logic as iter-2.
        targ_match = re.search(
            r"\*\*Target\*\*\s*:|\*\*Target:\*\*|^\s*Target\s*:",
            body, re.MULTILINE | re.IGNORECASE,
        )
        if targ_match:
            after = body[targ_match.end():].split("\n", 1)[0]
            if category == "external":
                if not (_VALUE_TOKEN.search(after) or re.search(r"\bN/?A\b", after, re.IGNORECASE)):
                    failures.append({"metric": f"[{category}] {name}",
                                     "check": "target_value_or_na",
                                     "evidence": after.strip()[:80]})
            else:
                if not _VALUE_TOKEN.search(after):
                    failures.append({"metric": f"[{category}] {name}",
                                     "check": "target_value_shape",
                                     "evidence": after.strip()[:80]})
    return failures


# -----------------------------------------------------------------------------
# prefill — emit a starter spec.json skeleton
# -----------------------------------------------------------------------------

def prefill_spec(process: str, owner: str, tags: list[str],
                 summary: str = "", related_extra: list[str] | None = None) -> dict[str, Any]:
    """Return a fully-formed spec.json dict the agent only needs to fill
    phase-block content into."""
    today = date.today().isoformat()
    return {
        "process": process,
        "owner": owner,
        "status": "draft",
        "tags": tags,
        "summary": summary,
        "related_extra": related_extra or [],
        "created": today,
        "last_reviewed": today,
        "truth_score": DEFAULT_TRUTH_SCORE,
        "define_block": "",
        "measure_block": "",
        "analyze_block": "",
        "improve_block": "",
        "control_block": "",
        "notes_block": "",
    }


# -----------------------------------------------------------------------------
# scaffold — emit per-phase markdown templates
# -----------------------------------------------------------------------------

_DEFINE_SCAFFOLD = """\
**What this process is supposed to do:** <one sentence, no jargon>

**What success looks like:** <concrete, observable end state>

**What failure looks like:** <equally concrete; absence of success>
"""

_MEASURE_SCAFFOLD_TEMPLATE = """\
### Output Metrics (terminal — confirm success)

{output_blocks}

### Controllable Input Metrics (the levers — owner can move these)

{controllable_blocks}

### External Input Metrics (context — affect output, can't be moved)

{external_blocks}
"""

_METRIC_BLOCK = """\
#### Metric {n}: <name>
- **Definition:** <how it's calculated, with units (%, ms, $, count, etc.)>
- **Collection:** <how + how often gathered; manual or automated>
- **Baseline:** <current value, OR `unknown — establish by YYYY-MM-DD`>
- **Target:** <where it needs to land>
"""

_EXTERNAL_METRIC_BLOCK = """\
#### Metric {n}: <name>
- **Definition:** <how it's calculated, with units (%, ms, $, count, etc.)>
- **Collection:** <how + how often gathered; manual or automated>
- **Baseline:** <current value, OR `unknown — establish by YYYY-MM-DD`>
- **Target:** N/A — track only
"""

_ANALYZE_SCAFFOLD_TEMPLATE = """\
### Causal Chain (which inputs drive which outputs)

For each output metric, name the controllable input(s) that move it. If an
output has no controllable input, the spec is incomplete — go back to Measure
and add the missing lever.

{causal_rows}

### Per-output thresholds and playbooks

{output_analyze_blocks}
"""

_CAUSAL_ROW = "| <Output Metric {n}> | <Controllable Input(s) — comma-separated> | <External Inputs that bound the relationship> |"

_OUTPUT_ANALYZE_BLOCK = """\
#### <Output Metric {n}>
- **Threshold (red / yellow / green):** <e.g. red ≤ baseline, yellow ≤ midpoint, green ≥ target>
- **Known failure modes (3–5):** <named cause 1>, <2>, <3>
- **First action when threshold trips:** <action> — owned by <[[Person]]>
- **Time-to-resolve target:** <e.g. 24h, 1 week>
"""

_IMPROVE_SCAFFOLD_TEMPLATE = """\
{experiment_blocks}
"""

_EXPERIMENT_BLOCK = """\
### Experiment {n}
- **Hypothesis:** We believe <change> will <effect> because <reasoning>.
- **Test plan:** <what changes, on what scope, for how long>
- **Success criterion:** <which metric moves, by how much>
- **Failure criterion:** <result that triggers revert>
- **Owner:** <[[Person]]>
- **Decision date:** <YYYY-MM-DD>
- **Status:** proposed | running | succeeded | failed | reverted
"""

_CONTROL_SCAFFOLD = """\
### Monitoring
- **Metric watched:** <which output metric>
- **Cadence:** <e.g. weekly Monday review, real-time alert>
- **Watcher:** <[[Person]]>

### Alert
- **Trigger:** <threshold or condition>
- **Destination:** <Slack channel, pager, email>
- **Responder:** <[[Person]]>
- **Response SLA:** <e.g. 24 hours>

### Recurring spec review
- **Cadence:** <e.g. quarterly>
- **Reviewer:** <[[Person]]>
- **Trigger conditions for off-cycle review:** <e.g. output drift > 20%, 3 alerts in a week>
"""


def scaffold_phase(phase: str, metrics: int = 3, experiments: int = 1) -> str:
    """Return a markdown scaffold for the named phase. The agent fills in the
    angle-bracket placeholders.

    metrics applies to Measure (output count) and Analyze (causal-row count
    and threshold-block count). experiments applies to Improve."""
    if phase == "define":
        return _DEFINE_SCAFFOLD
    if phase == "measure":
        if metrics < 1:
            raise ValueError(
                f"--metrics must be >= 1 (got {metrics}); a Measure scaffold needs at least one output metric"
            )
        output_blocks = "\n".join(_METRIC_BLOCK.format(n=i+1) for i in range(metrics))
        controllable = "\n".join(_METRIC_BLOCK.format(n=f"C{i+1}") for i in range(metrics))
        # External metrics: scaffold one external block by default; the count
        # doesn't couple to outputs (externals bound levers, not outputs).
        external = _EXTERNAL_METRIC_BLOCK.format(n="E1")
        return _MEASURE_SCAFFOLD_TEMPLATE.format(
            output_blocks=output_blocks,
            controllable_blocks=controllable,
            external_blocks=external,
        )
    if phase == "analyze":
        causal = "\n".join(_CAUSAL_ROW.format(n=i+1) for i in range(metrics))
        causal_table = (
            "| Output Metric | Controllable Inputs | External Inputs (bounds) |\n"
            "|---|---|---|\n" + causal
        )
        analyze_blocks = "\n".join(_OUTPUT_ANALYZE_BLOCK.format(n=i+1) for i in range(metrics))
        return _ANALYZE_SCAFFOLD_TEMPLATE.format(
            causal_rows=causal_table,
            output_analyze_blocks=analyze_blocks,
        )
    if phase == "improve":
        if experiments < 1:
            return "_No experiments in flight yet. Add as they're proposed._\n"
        return "\n".join(_EXPERIMENT_BLOCK.format(n=i+1) for i in range(experiments))
    if phase == "control":
        return _CONTROL_SCAFFOLD
    raise ValueError(f"unknown phase: {phase!r}")


# -----------------------------------------------------------------------------
# check-causal-chain — every Output Metric named in Analyze must trace to ≥1
# Controllable Input. Headline G4 enforcement.
# -----------------------------------------------------------------------------

def check_causal_chain(spec_text: str) -> dict[str, Any]:
    """Inspect the Analyze section's causal-chain table; verify every output
    metric has at least one controllable input listed.

    A placeholder row (output name wrapped in `<...>` or controllable cell
    wrapped in `<...>`) means the spec is incomplete — counted as a failure,
    not silently skipped. The headline G4 gate must fire on unfilled drafts.
    """
    analyze = _section(spec_text, "Analyze") or ""
    table_match = re.search(
        r"(\|[^\n]*Output Metric[^\n]*Controllable Input[^\n]*\|)\s*\n"
        r"\|[\s\-:|]+\|\s*\n"
        r"((?:\|[^\n]*\|\s*\n?)+)",
        analyze, re.IGNORECASE,
    )
    if not table_match:
        return {
            "all_outputs_traced": False,
            "missing": [],
            "placeholder_rows": [],
            "real_rows_checked": 0,
            "table_found": False,
            "evidence": "no causal-chain table found in Analyze (expected header row with 'Output Metric' and 'Controllable Input' columns)",
        }
    rows = [r.strip() for r in table_match.group(2).splitlines() if r.strip().startswith("|")]
    missing: list[str] = []
    placeholder_rows: list[str] = []
    real_rows = 0
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) < 2:
            continue
        output_name, controllable = cells[0], cells[1]
        is_placeholder_output = (
            (output_name.startswith("<") and output_name.endswith(">"))
            or output_name.startswith("[") and output_name.endswith("]")
        )
        is_placeholder_controllable = (
            (controllable.startswith("<") and controllable.endswith(">"))
            or controllable.startswith("[") and controllable.endswith("]")
            or controllable.lower() in ("none", "n/a", "")
        )
        if is_placeholder_output or is_placeholder_controllable:
            placeholder_rows.append(output_name)
            # Count as missing — an unfilled row is an unfilled spec.
            missing.append(output_name + " (placeholder)")
            continue
        real_rows += 1
        if not controllable:
            missing.append(output_name)
    return {
        # Strict success requires at least one real row AND zero unfilled rows
        # AND every real row traced.
        "all_outputs_traced": real_rows >= 1 and not missing,
        "missing": missing,
        "placeholder_rows": placeholder_rows,
        "real_rows_checked": real_rows,
        "table_found": True,
    }


# -----------------------------------------------------------------------------
# validate-owner — reject department-shaped names
# -----------------------------------------------------------------------------

_DEPARTMENT_DENYLIST = {
    "the team", "team", "operations", "ops", "marketing", "engineering",
    "product", "design", "leadership", "management", "everyone", "all hands",
    "tbd", "tba", "various", "n/a",
}


def validate_owner(owner: str) -> dict[str, Any]:
    """Reject department-shaped owners. People are accountable; departments
    aren't. Returns {"ok": bool, "reason": str}.

    Catches both single-token forms ("Operations") and multi-token forms
    ("Operations Team", "GIX Operations") by checking whether any denylist
    word appears as a token in the normalized name.
    """
    bare = owner.replace("[[", "").replace("]]", "").strip().lower()
    bare = re.sub(r"\([^)]*\)", "", bare).strip()
    if not bare:
        return {"ok": False, "reason": "owner is empty"}
    # Whole-string match (catches "the team", "operations" alone)
    if bare in _DEPARTMENT_DENYLIST:
        return {"ok": False, "reason": f"'{owner}' is a department, not a person — name a specific accountable individual"}
    # Token match — split on WHITESPACE only (not hyphens). A hyphenated
    # surname like "Operations-Lingle" is a single token; the false-positive
    # iter-2 hit ("Mike Operations-Lingle" rejected because hyphen split
    # made "operations" its own token) is fixed here.
    tokens = set(re.split(r"\s+", bare))
    overlap = tokens & _DEPARTMENT_DENYLIST
    if overlap:
        # One more guard: only flag multi-word names where the denylist token
        # is a *standalone word*, not part of a multi-word phrase that's
        # clearly a name (e.g. "the team" → ["the", "team"], both in denylist).
        return {
            "ok": False,
            "reason": (
                f"'{owner}' contains department-shaped token(s) {sorted(overlap)} — "
                "name a specific accountable individual (e.g. '[[Sarah Chen]]' "
                "instead of 'Operations Team' or 'GIX Operations'). "
                "Hyphenated surnames like 'Operations-Lingle' are fine — "
                "only whitespace-separated tokens are checked."
            ),
        }
    return {"ok": True, "reason": "ok"}


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
    p_co.add_argument("--force", action="store_true",
                       help="Overwrite the output file if it already exists")

    p_va = sub.add_parser("validate",
                          help="Validate a DMAIC spec markdown file")
    p_va.add_argument("--file", required=True, help="Path to the spec .md")
    p_va.add_argument("--strict", action="store_true",
                       help="Exit 1 if any check fails")
    p_va.add_argument("--strict-metrics", action="store_true",
                       help="Also run structural checks on metric units, "
                            "baseline shapes, target shapes")

    p_pf = sub.add_parser("prefill",
                          help="Emit a JSON skeleton with required keys filled in")
    p_pf.add_argument("--process", required=True, help="Process name (human-readable)")
    p_pf.add_argument("--owner", required=True, help="Owner — bare name or [[Wikilink]]")
    p_pf.add_argument("--tags", default="", help="Comma-separated tags (dmaic auto-added)")
    p_pf.add_argument("--summary", default="", help="One-sentence summary")
    p_pf.add_argument("--related-extra", default="",
                       help="Comma-separated extra wikilink targets")

    p_sc = sub.add_parser("scaffold",
                          help="Emit a markdown template for one phase")
    p_sc.add_argument("--phase", required=True,
                       choices=["define", "measure", "analyze", "improve", "control"])
    p_sc.add_argument("--metrics", type=int, default=3,
                       help="Number of output metric blocks (default 3; "
                            "controllable + external scale with this)")
    p_sc.add_argument("--experiments", type=int, default=1,
                       help="Number of experiment blocks for --phase improve")

    p_cc = sub.add_parser("check-causal-chain",
                          help="Verify every output metric in Analyze has ≥1 controllable input")
    p_cc.add_argument("--file", required=True, help="Path to the spec .md")
    p_cc.add_argument("--strict", action="store_true",
                       help="Exit 1 if any output is missing a controllable input")

    p_vo = sub.add_parser("validate-owner",
                          help="Reject department-shaped owner names")
    p_vo.add_argument("--owner", required=True, help="Owner string to validate")

    args = parser.parse_args()

    if args.cmd == "detect-vault":
        result = detect_vault(Path(args.cwd))
        print(json.dumps(result, indent=2))
        return 0

    if args.cmd == "compose":
        spec = json.loads(Path(args.input).read_text())
        md = compose_spec(spec)
        out_path = Path(args.output)
        if out_path.exists() and not args.force:
            print(json.dumps({
                "error": "output file already exists",
                "path": str(out_path),
                "hint": "pass --force to overwrite, or pick a different --output",
            }, indent=2), file=sys.stderr)
            return 1
        out_path.write_text(md)
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
        if args.strict_metrics:
            measure = _section(text, "Measure") or ""
            metric_failures = strict_metric_checks(measure)
            result["strict_metric_failures"] = metric_failures
            result["strict_metrics_pass"] = not metric_failures
            if metric_failures:
                result["all_passed"] = False
                result["failed"] += len(metric_failures)
                result["total"] += len(metric_failures)
        print(json.dumps(result, indent=2))
        if args.strict and not result["all_passed"]:
            return 1
        return 0

    if args.cmd == "prefill":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        related = [r.strip() for r in args.related_extra.split(",") if r.strip()]
        skel = prefill_spec(args.process, args.owner, tags,
                             summary=args.summary, related_extra=related)
        print(json.dumps(skel, indent=2))
        return 0

    if args.cmd == "scaffold":
        print(scaffold_phase(args.phase, metrics=args.metrics,
                              experiments=args.experiments))
        return 0

    if args.cmd == "check-causal-chain":
        text = Path(args.file).read_text()
        result = check_causal_chain(text)
        print(json.dumps(result, indent=2))
        if args.strict and not result["all_outputs_traced"]:
            return 1
        return 0

    if args.cmd == "validate-owner":
        result = validate_owner(args.owner)
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
