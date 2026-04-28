# Principles for Agent-Readable Process Specs

This file is bundled with the `process-design` skill. It distills general engineering principles for writing specs that a build agent (Claude Code, Claude Design, or any other implementer) can implement without ambiguity. These principles are domain-agnostic and implementation-agnostic.

---

## 1. Output-First Reasoning (Working Backwards)

The spec is constructed from output to inputs, not from inputs to output. Start by defining the desired output concretely, then identify the controllable inputs that shape it, then derive the minimum process that connects them.

**Test:** Can every step in the spec be justified by drawing a line from a named input to the named output? If not, the step is a deletion candidate.

## 2. Atomic Claims

Every step, decision rule, and edge case is a single, independently verifiable claim.

**Test:** Can you mark this claim true or false on its own?

## 3. Explicit Successors

For every step, the next step (or set of possible next steps) must be named. No "and then continue" or "proceed as appropriate."

**Test:** Can you trace a finger from any step to its named successor without judgment calls?

## 4. Testable Decision Rules

Every branching point has a criterion that resolves to true or false on the input alone. If the criterion genuinely requires judgment, name *who* exercises it and *what they evaluate*.

**Test:** Can two independent agents evaluate the same input and reach the same branch?

## 5. Requirement Attribution

Every step has a named decider and a named failure mode. Without attribution, future readers cannot question the step intelligently.

The attribution lives in two places: the spec's "Requirement Owners" section (canonical) and the diagram's node labels (visual reference).

**Test:** For any step, can you name the person to talk to if you suspect the step can be improved or eliminated?

## 6. Designed-In Measurement

Every step has its measurement defined before deletion decisions are made. Metrics fall into four categories — output, controllable input, agent performance, process health — and each step participates in the categories it can. Manage to the inputs, not the outputs.

**Test:** For every step, can you name what gets measured and what question that measurement answers?

## 7. Tests Defined Before Drafting (TDD for Specs)

The verification suite — what makes the spec complete and correct — is defined before the spec is drafted. The draft is then built to pass the suite. This prevents the writer from evaluating their own work against an implicit fuzzy standard.

**Test:** Before drafting begins, can you list the specific checks the spec must pass?

## 8. Adversarial Verification

The spec is verified using the QA Agents pattern (finder + auditor + referee), not a single sub-agent. Adversarial pressure between agents catches false negatives that a single verifier rubber-stamps.

**Test:** Has at least one independent agent attempted to challenge each finding from the verifier?

## 9. Explicit Edge Cases

Edge cases are first-class citizens of the spec. For each input dimension, name what happens when:
- The input is missing
- The input is malformed
- The input is at the boundary of valid (zero, max, edge of a range)
- The input is adversarial

## 10. Surfaced Assumptions and Open Questions

Anything inferred but not fully verified gets a line in an "Assumptions and Open Questions" section. Soft-failed gate checks also land here. A spec with five surfaced assumptions is more trustworthy than a spec with zero.

## 11. Single Source of Truth

When the same fact is referenced in multiple places, one location is canonical and the others link to it. Don't restate.

## 12. Build-Agent Handoff Notes

The spec ends with explicit guidance for the implementer: what to honor strictly, what to use judgment on, what to ask before deviating. The handoff is implementation-agnostic — the spec describes architectural requirements (gates, deterministic capture, graceful degradation), not implementation mechanisms.

## 13. Canonical vs. Derived Representations

When a spec has multiple representations (procedure block + diagram), one is canonical and the others are derived. The agent-readable spec is canonical; the diagram is the human view. Gates appear in both because they're decisions, not hidden checks.

## 14. Iterative by Design

A process spec is a living artifact. The Metrics Review Plan specifies when execution data triggers spec revisit. This makes the design loop closed: design → run → review with data → redesign.
