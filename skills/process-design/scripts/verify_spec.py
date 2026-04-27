"""Verify a process-design spec against the deterministic portion of its
verification suite.

Usage:
  python verify_spec.py <spec.md>          # Gate 6 (post-draft) checks
  python verify_spec.py --final <spec.md>  # Phase 8 final blocking assertions

Exit code 0 = all checks passed, 1 = one or more failed, 2 = bad invocation.

Stdlib only. The spec is a markdown file with YAML frontmatter at the top and
sections matching templates/process-spec-template.md.
"""

import argparse
import re
import sys
from pathlib import Path

# Allow running from inside scripts/ or from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import parse_mermaid


REQUIRED_SECTIONS_DRAFT = [
    "Output (Working Backwards Anchor)",
    "Inputs",
    "Metrics Map",
    "Procedure (Canonical)",
    "Gates (Verification Decisions in the Process)",
    "Requirement Owners",
    "Decision Rules",
    "Edge Cases",
    "Terminal States",
    "Diagram (Derived, Human-Readable)",
    "Verification Suite",
]

REQUIRED_SECTIONS_FINAL = REQUIRED_SECTIONS_DRAFT + [
    "Metrics Review Plan (DMAIC Control Phase)",
    "Build Notes",
    "Verification Record",
]

METRICS_CATEGORIES = [
    "Output Metrics",
    "Controllable Input Metrics",
    "Agent Performance Metrics",
    "Process Health Metrics",
]


def read_spec(path: Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text). Raises ValueError on malformed YAML."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("missing or malformed YAML frontmatter")
    fm_raw, body = match.group(1), match.group(2)
    fm: dict = {}
    current_key = None
    for line in fm_raw.splitlines():
        if not line.strip():
            continue
        kv = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if kv:
            key, value = kv.group(1), kv.group(2)
            # Strip inline `# comment` (preserving `#` inside quotes is over-engineering for our use).
            comment_idx = value.find("#")
            if comment_idx >= 0:
                value = value[:comment_idx]
            value = value.strip().strip("'\"")
            fm[key] = value
            current_key = key
        elif line.startswith("  - ") and current_key:
            fm.setdefault(current_key + "_list", []).append(line[4:].strip())
    return fm, body


def section(body: str, heading: str) -> str | None:
    """Return the body text under `## heading` up to the next `## ` or EOF."""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    match = pattern.search(body)
    return match.group(1) if match else None


def has_subsection(body: str, parent_heading: str, sub_heading: str) -> bool:
    parent = section(body, parent_heading) or ""
    return bool(re.search(rf"^###\s+{re.escape(sub_heading)}\s*$", parent, re.MULTILINE))


class Result:
    def __init__(self):
        self.passed: list[str] = []
        self.failed: list[str] = []

    def check(self, label: str, ok: bool, detail: str = ""):
        if ok:
            self.passed.append(label)
        else:
            self.failed.append(f"{label}{(' — ' + detail) if detail else ''}")

    def report(self) -> str:
        out = []
        for ok in self.passed:
            out.append(f"PASS  {ok}")
        for fail in self.failed:
            out.append(f"FAIL  {fail}")
        out.append("")
        out.append(f"{len(self.passed)} passed, {len(self.failed)} failed")
        return "\n".join(out)


def verify(path: Path, final: bool) -> Result:
    res = Result()

    try:
        fm, body = read_spec(path)
        res.check("YAML frontmatter parses", True)
    except (OSError, ValueError) as exc:
        res.check("YAML frontmatter parses", False, str(exc))
        return res

    res.check(
        "frontmatter has required keys",
        all(k in fm for k in ("type", "diagram_type", "status", "build_target")),
        f"got keys: {sorted(fm.keys())}",
    )
    res.check(
        "diagram_type is recognized",
        fm.get("diagram_type") in {"flowchart", "stateDiagram-v2", "sequenceDiagram"},
        f"got {fm.get('diagram_type')!r}",
    )
    if final:
        res.check(
            "status is verified",
            fm.get("status") == "verified",
            f"got {fm.get('status')!r}",
        )

    required = REQUIRED_SECTIONS_FINAL if final else REQUIRED_SECTIONS_DRAFT
    for heading in required:
        res.check(f"section present: {heading}", section(body, heading) is not None)

    metrics_body = section(body, "Metrics Map") or ""
    for cat in METRICS_CATEGORIES:
        res.check(
            f"Metrics Map has {cat}",
            bool(re.search(rf"^###\s+{re.escape(cat)}", metrics_body, re.MULTILINE)),
        )

    edge_cases_body = section(body, "Edge Cases") or ""
    edge_case_rows = [
        line for line in edge_cases_body.splitlines()
        if line.startswith("|") and not line.startswith("|---") and "Edge case" not in line
    ]
    if final:
        # In --final mode, reject template-placeholder rows (`<...>`) as
        # not-real edge cases. A draft with placeholders passes Gate 6 but
        # cannot be promoted to verified.
        real_rows = [r for r in edge_case_rows if not re.search(r"<[^>]+>", r)]
        res.check(
            "Edge Cases section has real content (not just placeholders)",
            len(real_rows) >= 1,
            f"{len(real_rows)} content rows out of {len(edge_case_rows)} table rows",
        )
    else:
        res.check(
            "Edge Cases section non-empty",
            bool(edge_case_rows),
        )

    if final:
        build_notes = section(body, "Build Notes") or ""
        res.check("Build Notes section non-empty", bool(build_notes.strip()))

        review_plan = section(body, "Metrics Review Plan (DMAIC Control Phase)") or ""
        res.check(
            "Metrics Review Plan names cadence",
            "**Cadence**" in review_plan or "Cadence:" in review_plan,
        )
        res.check(
            "Metrics Review Plan names trigger conditions",
            "Trigger conditions" in review_plan,
        )

        record = section(body, "Verification Record") or ""
        res.check(
            "qa-agents verification logged",
            "QA Agents" in record or "qa-agents" in record,
        )

    block = parse_mermaid.extract_mermaid_block(body)
    res.check("Mermaid block present", block is not None)
    if block is not None:
        graph = parse_mermaid.parse(block)
        res.check("Mermaid block parses without errors", not graph.errors,
                  "; ".join(graph.errors))

        # Step nodes (rectangles) require owner annotations. Gates (hexagons,
        # `{{...}}`) and terminal stadium nodes are exempt by spec convention —
        # gates' accountability is in the verification method; terminals are
        # end states, not requirements.
        owner_pattern = re.compile(r"req\s*:", re.IGNORECASE)
        step_nodes = [
            n for n in graph.nodes
            if n not in graph.terminals and not _is_gate(graph.nodes.get(n, ""))
        ]
        annotated = [n for n in step_nodes if owner_pattern.search(graph.nodes.get(n, ""))]
        res.check(
            "Every step node (non-gate, non-terminal) displays owner annotation",
            len(annotated) == len(step_nodes),
            f"{len(annotated)}/{len(step_nodes)} step nodes annotated; "
            f"missing: {sorted(set(step_nodes) - set(annotated))}",
        )

        reachable = parse_mermaid.reachable_terminals(graph)
        res.check(
            "At least one terminal state reachable",
            len(reachable) >= 1,
            f"declared terminals: {sorted(graph.terminals)}, reachable: {sorted(reachable)}",
        )

        unreachable = parse_mermaid.unreachable_nodes(graph)
        res.check(
            "No unreachable nodes",
            not unreachable,
            f"unreachable: {sorted(unreachable)}",
        )

        loops = parse_mermaid.unbounded_loops(graph)
        res.check(
            "No unbounded loops (cycles with no exit edge)",
            not loops,
            "; ".join(sorted(",".join(sorted(scc)) for scc in loops)),
        )

    procedure = section(body, "Procedure (Canonical)") or ""
    # Allow snake_case, kebab-case, dot-paths, and ASCII identifiers in step IDs.
    declared_step_ids = set(re.findall(
        r"^\s*\d+\.\s+\*\*([A-Za-z_][A-Za-z0-9_.\-]*)\*\*", procedure, re.MULTILINE
    ))
    referenced = set(re.findall(r"→\s*([A-Za-z_][A-Za-z0-9_.\-]*)", procedure))
    missing_refs = referenced - declared_step_ids - {"Terminal", "End", "terminal", "end"}
    res.check(
        "All step ID references in Procedure resolve",
        not missing_refs,
        f"missing: {sorted(missing_refs)}" if missing_refs else "",
    )

    if block is not None and declared_step_ids:
        # Cross-link procedure step IDs to diagram nodes: each procedure step
        # must appear by ID-token (or as the bold-name prefix) in at least one
        # diagram node's label.
        diagram_label_text = " | ".join(graph.nodes.values())
        unlinked = sorted(s for s in declared_step_ids if s not in diagram_label_text)
        res.check(
            "Every Procedure step ID appears in the diagram",
            not unlinked,
            f"missing in diagram: {unlinked}" if unlinked else "",
        )

    inputs_body = section(body, "Inputs") or ""
    declared_inputs = re.findall(r"^\-\s+\*\*([^*]+)\*\*", inputs_body, re.MULTILINE)
    inputs_with_validation = re.findall(
        r"^\-\s+\*\*([^*]+)\*\*[\s\S]*?-\s*Validation:", inputs_body, re.MULTILINE
    )
    res.check(
        "Every Input has documented validation",
        len(declared_inputs) == 0 or len(inputs_with_validation) == len(declared_inputs),
        f"{len(inputs_with_validation)}/{len(declared_inputs)} inputs have a Validation line",
    )

    # Decision Rules: every entry should name a Criterion line.
    decision_rules_body = section(body, "Decision Rules") or ""
    decision_blocks = re.findall(r"^\*\*([^*]+)\*\*", decision_rules_body, re.MULTILINE)
    rules_with_criterion = decision_rules_body.count("Criterion:")
    res.check(
        "Every Decision Rule has a Criterion",
        len(decision_blocks) == 0 or rules_with_criterion >= len(decision_blocks),
        f"{rules_with_criterion} criteria for {len(decision_blocks)} rules",
    )

    # Gates table: each gate row must have a non-empty Method column.
    gates_body = section(body, "Gates (Verification Decisions in the Process)") or ""
    gate_rows = [
        line for line in gates_body.splitlines()
        if line.startswith("|") and not line.startswith("|---") and "Gate ID" not in line
    ]
    gate_rows = [r for r in gate_rows if r.count("|") >= 6]  # 6 columns + leading/trailing pipes = 7 |s
    methods_named = []
    for row in gate_rows:
        cols = [c.strip() for c in row.strip("|").split("|")]
        if len(cols) >= 4:
            method = cols[3]
            if method and not method.startswith("<"):
                methods_named.append(row)
    res.check(
        "Every Gate row names a verification Method",
        len(gate_rows) == 0 or len(methods_named) == len(gate_rows),
        f"{len(methods_named)}/{len(gate_rows)} gate rows name a method",
    )

    # Cross-ref: every controllable input has at least one Controllable Input
    # Metric dimension (we look for the input name appearing in the
    # Controllable Input Metrics subsection).
    controllable_metrics_body = ""
    cim_match = re.search(
        r"###\s+Controllable Input Metrics(.*?)(?=^###\s|^##\s|\Z)",
        body, re.DOTALL | re.MULTILINE,
    )
    if cim_match:
        controllable_metrics_body = cim_match.group(1)
    if declared_inputs:
        controllable_inputs = re.findall(
            r"^\-\s+\*\*([^*]+)\*\*[\s\S]*?Controllable:\s*yes",
            inputs_body, re.MULTILINE | re.IGNORECASE,
        )
        unmetricked = [i for i in controllable_inputs if i not in controllable_metrics_body]
        res.check(
            "Every controllable input has ≥1 tracked dimension",
            not unmetricked,
            f"missing dimensions for: {unmetricked}" if unmetricked else "",
        )

    # Match either `standard performance` or the abbreviated `standard set`,
    # case-insensitive — the SKILL.md uses both interchangeably as canonical
    # ways of referencing the per-step performance metrics block.
    standard_metrics_pattern = re.compile(r"\bstandard\s+(performance|set)\b", re.IGNORECASE)
    standard_metrics_refs = len(standard_metrics_pattern.findall(procedure))
    res.check(
        "Every step references the standard performance metrics block",
        len(declared_step_ids) == 0 or standard_metrics_refs >= len(declared_step_ids),
        f"{standard_metrics_refs} mentions of `standard performance` or `standard set` "
        f"for {len(declared_step_ids)} steps",
    )

    return res


def _is_gate(label: str) -> bool:
    return "GATE" in label.upper()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Verify a process-design spec.")
    parser.add_argument("spec", type=Path)
    parser.add_argument("--final", action="store_true",
                        help="run the Phase 8 final blocking assertion set")
    args = parser.parse_args(argv)

    if not args.spec.is_file():
        print(f"no such file: {args.spec}", file=sys.stderr)
        return 2

    res = verify(args.spec, args.final)
    print(res.report())
    return 0 if not res.failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
