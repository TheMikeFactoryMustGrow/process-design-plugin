# Process Design

A Claude Code / Cowork plugin for designing processes that build agents can actually execute.

The headliner skill, `process-design`, walks you through nine steps (Steps 0–8) and produces **two deliverables**:

1. **A rendered flowchart** (image file, foreground-surfaced in the agent's response). This is the primary deliverable — a process is reviewable iff its structure is visible at a glance.
2. **A structured markdown spec** that backs the flowchart with frontmatter, metrics map, edge cases, verification record, and an implementation-agnostic build-handoff prompt.

The diagram is hoisted **early** (Step 2, before metrics design) and gated on explicit user confirmation. You see the visual, you confirm it represents the procedure you intended, *then* the skill wires up metrics. This is the most important behavioral change from v0.1.0 — designed to catch wrong-design before it gets cemented.

The plugin bundles four supporting skill families that `process-design` calls and that you can also invoke independently:

- **`qa-agents`** — adversarial three-agent review (Finder + Auditor + Referee). Step 6 of `process-design` delegates here for semantic verification; you can also invoke it directly to stress-test any artifact: code, documents, deal memos, contracts, financial models, decisions. After synthesis it runs a **root-cause-analysis pass on confirmed major findings** (5 Whys → root cause → recurrence guard), routing each fix to `test-loop` (a regression test) or `dmaic-control` (a control) so the same class of flaw can't ship again.
- **`dmaic`** — Six Sigma cycle (Define → Measure → Analyze → Improve → Control). The Metrics Review Plan in every spec `process-design` produces points users at this skill to actually run review cycles. Five phase skills (`dmaic-define`, `dmaic-measure`, `dmaic-analyze`, `dmaic-improve`, `dmaic-control`) are individually callable for à-la-carte use.
- **`elons-operating-algorithm`** — one-shot pressure test of any artifact (spec, plan, architecture, roadmap, feature list, process). Runs Elon's full 5-step Operating Algorithm in strict order — *question every requirement → delete → simplify → accelerate → automate* — and produces a structured deletion-first review note with verdicts (KEEP / QUESTION / DECOUPLE / DEFER / DELETE / SIMPLIFY), a "what survives" synthesis, a 10% add-back log, and a deepest-question reframe. Modeled on the Bean Counter Architecture Pressure Test that compressed a 20-story roadmap to 8.
- **`test-loop`** — builds the **executable regression guard**: writes the tests that lock a spec's decision rules and the project's conventions into assertions, measures coverage (statements + branches), and treats every failure it surfaces as a bug to fix at the root. The executable companion to `dmaic-control` — DMAIC *defines* the regression guard; this *builds* the code half. Run it on the output of a `process-design` Step 7 handoff, or any time code is declared "done" but not yet trusted.

Plus one optional **data-source** skill, independent of the process-design chain:

- **`birdclaw`** — read and analyze **your own** X/Twitter data from a local [birdclaw](https://birdclaw.sh) workspace (timeline, mentions, bookmarks, likes, DMs in local SQLite with full-text search). Pulls a slice as JSONL and analyzes it three ways: a plain-language overview via birdclaw's native AI digest, targeted extraction via full-text search, or an **adversarial pass that hands the JSONL to `qa-agents`** to stress-test a take or thread before you post. Scope is your own account only — it can't fetch arbitrary public tweets or topic firehoses, and the skill says so rather than faking it.

## Why bundled

These five are designed to compose. A spec produced by `process-design` is verified by `qa-agents` (Step 6 adversarial layer), reviewed over time via `dmaic` (Step 5 cadence handoff), pressure-tested for bloat by `elons-operating-algorithm` whenever it starts to feel overbuilt, and — once built — locked down by `test-loop` (the executable regression suite). Bundling them means you install one plugin and get a working chain. Each skill is still independently invokable as `process-design:qa-agents`, `process-design:dmaic-measure`, `process-design:elons-operating-algorithm`, etc.

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

That's it. All eleven skills load namespaced as `process-design:process-design`, `process-design:qa-agents`, `process-design:dmaic`, `process-design:dmaic-define` … `process-design:dmaic-control`, `process-design:elons-operating-algorithm`, `process-design:test-loop`, `process-design:birdclaw`.

The plugin also appears in Claude Desktop's **Customize** panel automatically — a CLI install covers both surfaces.

### Cowork (drag-and-drop)

1. Download [`dist/process-design.plugin`](dist/process-design.plugin) (or build it locally with `./build.sh`)
2. Drop the file onto Cowork's plugin manager
3. Click Install, restart your session

Note: drag-and-drop installs are frozen snapshots with no update path — prefer the marketplace install above so you can pull new versions.

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

## Update

When a new version lands in this repo:

```bash
# Refresh the marketplace catalog, then update the plugin
claude plugin marketplace update process-design-plugin
claude plugin update process-design@process-design-plugin
```

(Or from inside a session: `/plugin marketplace update process-design-plugin` then `/plugin update process-design@process-design-plugin`, followed by `/reload-plugins`.)

**Set-and-forget option:** enable auto-update once — `/plugin` → **Marketplaces** tab → `process-design-plugin` → **Enable auto-update**. Every Claude Code restart then pulls the latest version automatically.

> **Note for Claude Desktop users:** the desktop app's personal-plugin UI currently has no working update path for GitHub marketplaces — the Update button stays greyed out. Use the CLI commands above; the desktop app picks up the result.

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
- **Canonical styling** (since v0.6.0): node roles differentiated by shape *and* semantic color from a fixed `classDef` palette — green entry/success, blue steps, amber gates, red hard-gates/failures, gray neutral/fallback — applied identically to every spec. The Mermaid `theme` is never locked, so the diagram follows the reader's light/dark setting while role colors stay stable; color is always in addition to shape, never instead of it.
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
│       └── skills/                          ← 10 skills
│           ├── process-design/              ← headliner
│           ├── qa-agents/                   ← bundled adversarial review + RCA
│           ├── dmaic/                       ← bundled Six Sigma orchestrator
│           ├── dmaic-define/
│           ├── dmaic-measure/
│           ├── dmaic-analyze/
│           ├── dmaic-improve/
│           ├── dmaic-control/
│           ├── elons-operating-algorithm/   ← bundled one-shot pressure test
│           ├── test-loop/                   ← bundled executable-regression-suite builder
│           └── birdclaw/                     ← optional: read & analyze your own X data
├── dist/process-design.plugin               ← prebuilt zip for Cowork drag-and-drop
├── meta-spec/                               ← process-design applied to itself (v1)
├── build.sh                                 ← rebuild dist/process-design.plugin
├── README.md
└── LICENSE
```

`evals/` and `workspaces/` are present locally for skill-creator regression testing but excluded from this public repo via `.gitignore` — they're dev artifacts that aren't needed to run or install the plugin.

## Versions

- **v0.7.0** (current) — Adds `birdclaw`, an optional **data-source** skill that reads and analyzes your *own* X/Twitter data from a local [birdclaw](https://birdclaw.sh) workspace. It drives the birdclaw CLI to pull a slice (timeline / mentions / bookmarks / likes / search) as JSONL via a defensive `pull.py` helper, then analyzes it three ways: native AI digest for an overview, full-text search for extraction, or an adversarial handoff to `qa-agents` to stress-test a take or thread before posting. Scoped to the user's own account — it explicitly refuses arbitrary-public-tweet requests rather than faking them, and never invents rows. Independent of the process-design chain; eleven skills total.
- **v0.6.0** — Bakes a **canonical flowchart format** into every spec `process-design` produces: node roles are differentiated by **shape** *and* **semantic color** (green entry/success, blue steps, amber gates, red hard-gates/failures, gray neutral/fallback), applied identically across all specs via a fixed `classDef` palette in the spec template and `SKILL.md`. Two hard rules: the Mermaid `theme` is **never locked**, so the rendered diagram follows the reader's system light/dark setting (e.g. Obsidian dark mode) while role colors stay stable; and color is always *in addition to* shape, never instead of it (the shape alone must disambiguate role). `parse_mermaid.py` now tolerates a leading `%%{init ...}%%` directive / `%%` comment before the diagram-type declaration, so specs carrying an init directive still pass the "Mermaid block parses" assertion. Still ten skills.
- **v0.5.0** — Adds `test-loop` (builds the executable regression suite that locks a spec's decision rules and conventions into tests and surfaces real bugs in the process — the executable companion to `dmaic-control`) and a **root-cause-analysis pass in `qa-agents`** (5 Whys on confirmed major findings, routed to `test-loop` or `dmaic-control`). `process-design` Step 7's build prompt now requires a spec-locking regression suite; `dmaic-control` notes that for coded processes the test suite is the primary regression guard. Ten skills total.
- **v0.4.0** — Adds `elons-operating-algorithm`: one-shot pressure test running Elon's full 5-step algorithm (question → delete → simplify → accelerate → automate) against any artifact, producing a structured deletion-first review note. Nine skills total.
- **v0.3.0** — Restructured to Claude Code marketplace layout (`.claude-plugin/marketplace.json` + `plugins/` tree); repo doubles as an installable marketplace.
- **v0.2.0** — Render hoisted to Step 2 with hard-gate review; Phase 3 dissolved into distributed deletion + concentrated Step 3 pruning; Step 0 Ingest and Step 8 Reconcile added; foregrounding requirement on the rendered image; `image_freshness` blocking assertion; `post_handoff_clarification` telemetry event.
- **v0.1.0** — Initial release. Eight phases, Mermaid-block-as-output, render burial.

## License

MIT. See [LICENSE](LICENSE).
