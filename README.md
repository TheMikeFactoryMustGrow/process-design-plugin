# Process Design

A Claude Code / Cowork plugin for designing processes that build agents can actually execute.

The headliner skill, `process-design`, walks you through eight phases — Working Backwards, metrics design, Elon's algorithm, gap probing, verification suite, draft, adversarial verify, build handoff — and produces a structured markdown spec with a Mermaid diagram. The diagram inherits the quality of the design that produced it; the goal is the design, not the picture.

The plugin bundles two supporting skill families that `process-design` calls and that you can also invoke independently:

- **`qa-agents`** — adversarial three-agent review (Finder + Auditor + Referee). Phase 7 of `process-design` delegates here; you can also invoke it directly to stress-test any artifact: code, documents, deal memos, contracts, financial models, decisions.
- **`dmaic`** — Six Sigma cycle (Define → Measure → Analyze → Improve → Control). The Metrics Review Plan in every spec `process-design` produces points users at this skill to actually run review cycles. Five phase skills (`dmaic-define` etc.) are individually callable for à-la-carte use.

## Why bundled

These three are designed to compose. A spec produced by `process-design` is verified by `qa-agents` and reviewed over time via `dmaic`. Bundling them means you install one plugin and get a working chain. Each skill is still independently invokable as `process-design:qa-agents`, `process-design:dmaic-measure`, etc.

## Install

1. Build: `./build.sh` produces `dist/process-design.plugin`.
2. Drop the file into Cowork's plugin manager.
3. Restart your session.

## Use

The headliner triggers on phrases like:

- "Design a process for X"
- "Spec this out for an agent"
- "Help me think through this workflow"
- "What edge cases am I missing?"
- "Turn this into something Claude Code can build"
- "I do this all the time but haven't defined it"

The supports trigger on their own phrases — `qa-agents` on "QA this", "stress test this", "red team this"; `dmaic` on "design metrics for this", "make this measurable", and similar.

## What `process-design` produces

A single markdown file conforming to `skills/process-design/templates/process-spec-template.md`:

- YAML frontmatter (`status: draft` mid-session, `verified` after Phase 7 passes)
- Output / Inputs / Preconditions
- Metrics Map across four categories (output, controllable input, agent performance, process health) plus anecdote / exception capture
- Procedure with explicit successor conditions and step IDs
- Gates as visible decision nodes
- Requirement Owners table (people, not departments)
- Decision Rules with testable criteria
- Edge Cases and Terminal States
- Mermaid diagram with inline owner annotations (`req: <name>`)
- Verification Suite (TDD-style — defined before drafting)
- Metrics Review Plan that points the user at `dmaic` for execution
- Build Notes (architecture-only, no implementation prescriptions)

## Helper scripts

`skills/process-design/scripts/`:

- `verify_spec.py <path>` — runs the deterministic portion of the verification suite (Gate 6); add `--final` for the Phase 8 blocking-assertion set.
- `parse_mermaid.py <path>` — extracts and parses the Mermaid block; reports nodes, edges, and reachable terminals.
- `render_handoff.py <path> --target <build-target>` — renders the Phase 8 build-handoff prompt with target-specific capture-mechanism examples.

All stdlib Python 3.

## Telemetry

`process-design` writes session telemetry to `$PROCESS_DESIGN_LOG_DIR/<date>-<process-slug>.jsonl`, defaulting to `~/.claude/process-design-sessions/`. Best-effort — if the destination is unreachable, the skill completes anyway with a degraded-mode warning. Output correctness does not depend on telemetry working.

## License

MIT. See [LICENSE](LICENSE).
