"""Minimal Mermaid parser for process-design specs.

Extracts node IDs, node labels, and edges from a mermaid code block in a
process-spec markdown file. Stdlib only.

Supported syntax (the subset process-design produces):
  - flowchart TD / LR
  - Node declarations:  Id["label"]   Id(["label"])   Id{{"label"}}
  - Edges: A --> B,  A -->|label| B,  A -.-> B,  A ==> B

Anything richer (subgraphs, classDef, click handlers, etc.) is tolerated by
being skipped — we only extract what the verifier needs.
"""

import re
import sys
from dataclasses import dataclass, field


NODE_DECL = re.compile(
    r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*'
    r'(?:\[\["(?P<a>[^"]*)"\]\]|'
    r'\["(?P<b>[^"]*)"\]|'
    r'\(\["(?P<c>[^"]*)"\]\)|'
    r'\(\("(?P<d>[^"]*)"\)\)|'
    r'\{\{"(?P<e>[^"]*)"\}\}|'
    r'\{"(?P<f>[^"]*)"\}|'
    r'>"(?P<g>[^"]*)"\])'
)

EDGE = re.compile(
    r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*'
    r'(?:-->|-\.->|==>|--[ox]|---)'
    r'(?:\|[^|]*\|)?\s*'
    r'([A-Za-z_][A-Za-z0-9_]*)'
)

INLINE_NODE = re.compile(
    r'([A-Za-z_][A-Za-z0-9_]*)'
    r'(?:\[\["(?P<a>[^"]*)"\]\]|'
    r'\["(?P<b>[^"]*)"\]|'
    r'\(\["(?P<c>[^"]*)"\]\)|'
    r'\(\("(?P<d>[^"]*)"\)\)|'
    r'\{\{"(?P<e>[^"]*)"\}\}|'
    r'\{"(?P<f>[^"]*)"\})'
)


@dataclass
class Graph:
    nodes: dict = field(default_factory=dict)  # id -> label
    edges: list = field(default_factory=list)  # (from_id, to_id)
    terminals: set = field(default_factory=set)  # nodes with stadium/round shape
    errors: list = field(default_factory=list)

    def referenced_ids(self):
        ids = set()
        for a, b in self.edges:
            ids.add(a)
            ids.add(b)
        return ids


def extract_mermaid_block(markdown: str) -> str | None:
    """Pull the first ```mermaid ... ``` block out of a markdown document."""
    match = re.search(r"```mermaid\s*\n(.*?)```", markdown, re.DOTALL)
    return match.group(1) if match else None


def _capture_label(match) -> str:
    for key in ("a", "b", "c", "d", "e", "f", "g"):
        try:
            value = match.group(key)
        except IndexError:
            value = None
        if value is not None:
            return value
    return ""


def parse(mermaid_src: str) -> Graph:
    g = Graph()
    if not mermaid_src.strip():
        g.errors.append("empty mermaid source")
        return g

    lines = [line.rstrip() for line in mermaid_src.splitlines()]
    if lines and not re.match(r"^\s*(flowchart|graph|stateDiagram|sequenceDiagram)", lines[0]):
        g.errors.append(f"unrecognized first line: {lines[0]!r}")

    for raw in lines:
        line = raw.split("%%", 1)[0]
        if not line.strip():
            continue

        # First, find every inline node declaration (a node may be declared
        # mid-edge: `A["x"] --> B["y"]`).
        for match in INLINE_NODE.finditer(line):
            node_id = match.group(1)
            label = _capture_label(match)
            g.nodes[node_id] = label
            # Stadium shape `Id(["..."])` is the conventional terminal marker.
            if "([" in match.group(0) and "])" in match.group(0):
                g.terminals.add(node_id)

        # Edges
        for match in EDGE.finditer(line):
            src, dst = match.group(1), match.group(2)
            g.edges.append((src, dst))

    # Any node referenced in an edge but never declared — record but don't crash.
    declared = set(g.nodes.keys())
    referenced = g.referenced_ids()
    for missing in referenced - declared:
        g.nodes[missing] = ""  # implicit — declared by being referenced

    return g


def reachable_terminals(g: Graph, start: str | None = None) -> set:
    """BFS from `start` (or any node with no incoming edge) to find which
    declared terminal nodes are reachable."""
    if not g.nodes:
        return set()
    incoming = {n: 0 for n in g.nodes}
    for a, b in g.edges:
        incoming[b] = incoming.get(b, 0) + 1
    if start is None:
        roots = [n for n, c in incoming.items() if c == 0] or [next(iter(g.nodes))]
    else:
        roots = [start]

    seen = set()
    stack = list(roots)
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        for a, b in g.edges:
            if a == node and b not in seen:
                stack.append(b)
    return seen & g.terminals


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: parse_mermaid.py <spec.md>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as fh:
        src = fh.read()
    block = extract_mermaid_block(src)
    if block is None:
        print("no mermaid block found", file=sys.stderr)
        sys.exit(1)
    graph = parse(block)
    print(f"nodes: {len(graph.nodes)}  edges: {len(graph.edges)}  terminals: {len(graph.terminals)}")
    if graph.errors:
        print("errors:")
        for err in graph.errors:
            print(f"  - {err}")
    reachable = reachable_terminals(graph)
    print(f"reachable terminals: {sorted(reachable) or '(none)'}")
