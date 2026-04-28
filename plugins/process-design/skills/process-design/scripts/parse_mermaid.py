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


def reachable_from_roots(g: Graph) -> set:
    """Set of all nodes reachable from any root (nodes with no incoming edge).
    If no roots exist (every node has an incoming edge), starts from the first
    declared node — this can only happen when the graph is one big cycle."""
    if not g.nodes:
        return set()
    incoming = {n: 0 for n in g.nodes}
    for _, b in g.edges:
        incoming[b] = incoming.get(b, 0) + 1
    roots = [n for n, c in incoming.items() if c == 0] or [next(iter(g.nodes))]
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
    return seen


def reachable_terminals(g: Graph) -> set:
    return reachable_from_roots(g) & g.terminals


def unreachable_nodes(g: Graph) -> set:
    """Nodes that exist but cannot be reached from any root."""
    return set(g.nodes) - reachable_from_roots(g)


def unbounded_loops(g: Graph) -> list:
    """Strongly-connected components of size >1 with no edge leaving the SCC.
    A cycle that has at least one outgoing edge to a node outside is bounded
    (the process can leave). A cycle with no exit is an infinite loop.

    Returns a list of frozensets, one per SCC found."""
    # Tarjan's SCC algorithm.
    index_counter = [0]
    stack: list = []
    on_stack = set()
    indices: dict = {}
    lowlinks: dict = {}
    sccs: list = []

    successors: dict = {n: [] for n in g.nodes}
    for a, b in g.edges:
        if a in successors:
            successors[a].append(b)

    def strongconnect(node):
        indices[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)
        for succ in successors.get(node, []):
            if succ not in indices:
                strongconnect(succ)
                lowlinks[node] = min(lowlinks[node], lowlinks[succ])
            elif succ in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[succ])
        if lowlinks[node] == indices[node]:
            component = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == node:
                    break
            sccs.append(frozenset(component))

    for node in g.nodes:
        if node not in indices:
            strongconnect(node)

    unbounded = []
    for scc in sccs:
        if len(scc) < 2:
            # singleton: unbounded only if it has a self-loop with no other exit
            (only,) = scc
            outgoing = [b for a, b in g.edges if a == only]
            self_loops = [b for b in outgoing if b == only]
            if self_loops and len(outgoing) == len(self_loops):
                unbounded.append(scc)
            continue
        # SCC of size >= 2: unbounded iff no edge leaves the component
        outgoing_to_outside = [
            (a, b) for a, b in g.edges if a in scc and b not in scc
        ]
        if not outgoing_to_outside:
            unbounded.append(scc)
    return unbounded


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
    unreachable = unreachable_nodes(graph)
    if unreachable:
        print(f"unreachable nodes: {sorted(unreachable)}")
    loops = unbounded_loops(graph)
    if loops:
        for scc in loops:
            print(f"unbounded loop: {sorted(scc)}")
