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
            key, value = kv.group(1), kv.group(2).strip()
            if value.startswith("#"):
                value = ""
            fm[key] = value.strip("'\"") if value else ""
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
    res.check(
        "Edge Cases section non-empty",
        bool(re.search(r"^\s*\|", edge_cases_body, re.MULTILINE)),
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

        owner_pattern = re.compile(r"req\s*:", re.IGNORECASE)
        nodes_with_owners = sum(1 for label in graph.nodes.values() if owner_pattern.search(label))
        non_terminal_nodes = [n for n in graph.nodes if n not in graph.terminals]
        res.check(
            "Every non-terminal node displays owner annotation",
            all(owner_pattern.search(graph.nodes.get(n, "")) for n in non_terminal_nodes if not _is_gate(graph.nodes.get(n, ""))),
            f"{nodes_with_owners}/{len(non_terminal_nodes)} non-terminal nodes annotated",
        )

        reachable = parse_mermaid.reachable_terminals(graph)
        res.check(
            "At least one terminal state reachable",
            len(reachable) >= 1,
            f"declared terminals: {sorted(graph.terminals)}, reachable: {sorted(reachable)}",
        )

    procedure = section(body, "Procedure (Canonical)") or ""
    declared_step_ids = set(re.findall(r"^\d+\.\s+\*\*([A-Za-z_][A-Za-z0-9_]*)\*\*", procedure, re.MULTILINE))
    referenced = set(re.findall(r"→\s*([A-Za-z_][A-Za-z0-9_]*)", procedure))
    missing_refs = referenced - declared_step_ids - {"Terminal", "End", "terminal", "end"}
    res.check(
        "All step ID references in Procedure resolve",
        not missing_refs,
        f"missing: {sorted(missing_refs)}" if missing_refs else "",
    )

    standard_metrics_refs = procedure.count("standard performance")
    res.check(
        "Every step references standard performance metrics",
        len(declared_step_ids) == 0 or standard_metrics_refs >= len(declared_step_ids),
        f"{standard_metrics_refs} mentions for {len(declared_step_ids)} steps",
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
