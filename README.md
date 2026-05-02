# Process Design

A Claude Code / Cowork plugin for designing processes that build agents can actually execute.

The headliner skill, `process-design`, walks you through nine steps (Steps 0–8) and produces **two deliverables**:

1. **A rendered flowchart** (image file, foreground-surfaced in the agent's response). This is the primary deliverable — a process is reviewable iff its structure is visible at a glance.
2. **A structured markdown spec** that backs the flowchart with frontmatter, metrics map, edge cases, verification record, and an implementation-agnostic build-handoff prompt.

The diagram is hoisted **early** (Step 2, before metrics design) and gated on explicit user confirmation. You see the visual, you confirm it represents the procedure you intended, *then* the skill wires up metrics. This is the most important behavioral change from v0.1.0 — designed to catch wrong-design before it gets cemented.

The plugin bundles two supporting skill families that `process-design` calls and that you can also invoke independently:

- **`qa-agents`** — adversarial three-agent review (Finder + Auditor + Referee). Step 6 of `process-design` delegates here for semantic verification; you can also invoke it directly to stress-test any artifact: code, documents, deal memos, contracts, financial models, decisions.
- **`dmaic`** — Six Sigma cycle (Define → Measure → Analyze → Improve → Control). The Metrics Review Plan in every spec `process-design` produces points users at this skill to actually run review cycles. Five phase skills (`dmaic-define`, `dmaic-measure`, `dmaic-analyze`, `dmaic-improve`, `dmaic-control`) are individually callable for à-la-carte use.

## Why bundled

These three are designed to compose. A spec produced by `process-design` is verified by `qa-agents` (Step 6 adversarial layer) and reviewed over time via `dmaic` (Step 5 cadence handoff). Bundling them means you install one plugin and get a working chain. Each skill is still independently invokable as `process-design:qa-agents`, `process-design:dmaic-measure`, etc.

## What `process-design` does, step by step

```
Step 0: Ingest existing description       (conditional — only if user supplies one)
Step 1: Anchor (1A Output → 1B Inputs → 1C Transitions → 1D Failure modes)
        with distributed deletion at every sub-step
Step 1 exit: Gap-probe fan-out (4 parallel sub-agents) with completion gate
Step 2: Render — Mermaid → image file, validate, foreground in response
[Step 2 Review — HARD GATE: confirm / reject+named / reject-silent]
Step 3: Final pruning (concentrated Elon pass, post-visual)
Step 4: Metrics design (output / controllable input / agent / health)
Step 5: Review cadence + DMAIC handoff + telemetry destination
Step 6: Verify — verify_spec.py (structural) + qa-agents (semantic)
Step 7: Build handoff — implementation-agnostic prompt + foregrounded artifacts
Step 8: Reconcile spec ↔ source                 (conditional — only if Step 0 fired)
```

Distributed deletion means every input, transition, metric, and check is challenged at the moment of addition (P2 — *useful iff its output produces value the inputs alone don't*) — not in a single late phase. A concentrated Elon pass then runs at Step 3, after the visual exists and bloat becomes obvious. Both modes, not either-or.

## Install

### Claude Code (recommended for most colleagues)

```bash
# 1. Add this repo as a marketplace
/plugin marketplace add TheMikeFactoryMustGrow/process-design-plugin

# 2. Install the plugin from the marketplace
/plugin install process-design@process-design-plugin
```

That's it. All eight skills load namespaced as `process-design:process-design`, `process-design:qa-agents`, `process-design:dmaic`, `process-design:dmaic-define` … `process-design:dmaic-control`.

### Cowork (drag-and-drop)

1. Download [`dist/process-design.plugin`](dist/process-design.plugin) (or build it locally with `./build.sh`)
2. Drop the file onto Cowork's plugin manager
3. Click Install, restart your session

### Local development install

If you want to hack on the plugin in place:

```bash
git clone git@github.com:TheMikeFactoryMustGrow/process-design-plugin.git ~/Documents/Linglepedia/_claude_config/process-design
```

Cowork will scan `_claude_config/` and find the plugin manifest at `plugins/process-design/.claude-plugin/plugin.json`.

For Mermaid → image rendering at Step 2, the skill uses `mmdc` (Mermaid CLI). If not installed:

```bash
npm install -g @mermaid-js/mermaid-cli
```

(Falls back to Obsidian-renderable fenced markdown if `mmdc` is unavailable.)

## Use

The headliner triggers on phrases like:

- "Design a process for X"
- "Spec this out for an agent"
- "Help me think through this workflow"
- "What edge cases am I missing?"
- "Turn this into something Claude Code can build"
- "Draft a flowchart for X"
- "I do this all the time but haven't defined it"

The supports trigger on their own phrases — `qa-agents` on "QA this", "stress test this", "red team this"; `dmaic` on "design metrics for this", "make this measurable", and similar.

## What `process-design` produces

A pair of files (flowchart + spec) conforming to `plugins/process-design/skills/process-design/templates/process-spec-template.md`:

**Flowchart** (`<process-slug>.flowchart.png`):
- Rendered via `mmdc` to a PNG next to the spec
- Step nodes with inline `req: <owner> / breaks: <consequence>` annotations
- Gates as visible hexagonal decision nodes
- Terminal states as stadium nodes
- The agent's final response surfaces this image path on its own line — never buried in prose

**Markdown spec** (`<process-slug>.process-spec.md`):
- YAML frontmatter (`status: draft` mid-session, `verified` after Step 6 passes)
- Output / Inputs / Constraints
- Procedure with explicit successor conditions and step IDs
- Gates table with verification methods (script / agent / human)
- Requirement Owners table (people, not departments)
- Decision Rules with testable criteria
- Edge Cases and Terminal States
- Metrics Map across four categories (output, controllable input, agent performance, process health) plus anecdote / exception capture
- Verification Suite (TDD-style — defined before drafting)
- Metrics Review Plan pointing at `dmaic` for execution
- Build Notes (architecture-only, no implementation prescriptions)
- Verification Record (Step 6 mode logged: `skill_invocation` or `inline_simulation`)

## Helper scripts

`plugins/process-design/skills/process-design/scripts/`:

- `verify_spec.py <path>` — runs the deterministic portion of the verification suite; add `--final` for the Step 7 blocking-assertion set. In `--final` mode prints a structured `PASSED: N/N final blocking assertions` summary line as proof-of-work evidence (the count itself is the contract — drift between this count, the SKILL.md assertion table, and the eval expectations is a defect).
- `parse_mermaid.py <path>` — extracts and parses the Mermaid block; reports nodes, edges, reachable terminals, and unbounded loops.
- `render_handoff.py <path> --target <build-target>` — renders the Step 7 build-handoff prompt with target-specific capture-mechanism examples.

All stdlib Python 3.

## Telemetry

`process-design` writes session telemetry to `$PROCESS_DESIGN_LOG_DIR/<date>-<process-slug>.jsonl`, defaulting to `~/.claude/process-design-sessions/`. Best-effort — if the destination is unreachable, the skill completes anyway with a degraded-mode warning. Output correctness does not depend on telemetry working.

The headline measurable signal is `post_handoff_clarification` — the rate at which the build agent comes back asking for spec clarification. A high rate indicates the spec is leaving ambiguities the build agent can't resolve. DMAIC reviews use this to drive improvements.

Other tracked events: `session_start`, `phase_start`, `phase_complete` (with `mode` for fan-out / qa-agents), `gate_hard_fail`, `gate_soft_fail`, `gate_pass`, `soft_fail_threshold_surfaced`, `step_aborted`, `user_decision`, `loop_back`, `qa_finding`, `step_2_review_outcome`, `step_8_drift_item`, `session_complete`.

## Repository layout

```
process-design-plugin/                       (this repo, also the Claude Code marketplace)
├── .claude-plugin/marketplace.json          ← marketplace manifest (Claude Code reads this)
├── plugins/
│   └── process-design/                      ← plugin source
│       ├── .claude-plugin/plugin.json       ← plugin manifest (Cowork reads this)
│       └── skills/                          ← 8 skills
│           ├── process-design/              ← headliner
│           ├── qa-agents/                   ← bundled adversarial review
│           ├── dmaic/                       ← bundled Six Sigma orchestrator
│           ├── dmaic-define/
│           ├── dmaic-measure/
│           ├── dmaic-analyze/
│           ├── dmaic-improve/
│           └── dmaic-control/
├── dist/process-design.plugin               ← prebuilt zip for Cowork drag-and-drop
├── meta-spec/                               ← process-design applied to itself (v1)
├── build.sh                                 ← rebuild dist/process-design.plugin
├── README.md
└── LICENSE
```

`evals/` and `workspaces/` are present locally for skill-creator regression testing but excluded from this public repo via `.gitignore` — they're dev artifacts that aren't needed to run or install the plugin.

## Versions

- **v0.2.0** (current) — Render hoisted to Step 2 with hard-gate review; Phase 3 dissolved into distributed deletion + concentrated Step 3 pruning; Step 0 Ingest and Step 8 Reconcile added; foregrounding requirement on the rendered image; `image_freshness` blocking assertion; `post_handoff_clarification` telemetry event.
- **v0.1.0** — Initial release. Eight phases, Mermaid-block-as-output, render burial.

## License

MIT. See [LICENSE](LICENSE).
