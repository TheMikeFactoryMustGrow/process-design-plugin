# Process Design

A Claude Code / Cowork plugin for designing processes that build agents can actually execute.

The headliner skill, `process-design`, walks you through eight phases — Working Backwards, metrics design, Elon's algorithm, gap probing, verification suite, draft, adversarial verify, build handoff — and produces a structured markdown spec with a Mermaid diagram. The diagram inherits the quality of the design that produced it; the goal is the design, not the picture.

The plugin bundles two supporting skill families that `process-design` calls and that you can also invoke independently:

- **`qa-agents`** — adversarial three-agent review (Finder + Auditor + Referee). Phase 7 of `process-design` delegates here; you can also invoke it directly to stress-test any artifact: code, documents, deal memos, contracts, financial models, decisions.
- **`dmaic`** — Six Sigma cycle (Define → Measure → Analyze → Improve → Control). The Metrics Review Plan in every spec `process-design` produces points users at this skill to actually run review cycles. Five phase skills (`dmaic-define` etc.) are individually callable for à-la-carte use.

## Why bundled

These three are designed to compose. A spec produced by `process-design` is verified by `qa-agents` and reviewed over time via `dmaic`. Bundling them means you install one plugin and get a working chain. Each skill is still independently invokable as `process-design:qa-agents`, `process-design:dmaic-measure`, etc.

## Install

### Claude Code (recommended for most colleagues)

```bash
# 1. Add this repo as a marketplace
/plugin marketplace add TheMikeFactoryMustGrow/process-design-plugin

# 2. Install the plugin from the marketplace
/plugin install process-design@process-design-plugin
```

That's it. All 8 skills load namespaced as `process-design:process-design`, `process-design:qa-agents`, `process-design:dmaic`, `process-design:dmaic-define` … `process-design:dmaic-control`.

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

A single markdown file conforming to `plugins/process-design/skills/process-design/templates/process-spec-template.md`:

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

`plugins/process-design/skills/process-design/scripts/`:

- `verify_spec.py <path>` — runs the deterministic portion of the verification suite (Gate 6); add `--final` for the Phase 8 blocking-assertion set.
- `parse_mermaid.py <path>` — extracts and parses the Mermaid block; reports nodes, edges, and reachable terminals.
- `render_handoff.py <path> --target <build-target>` — renders the Phase 8 build-handoff prompt with target-specific capture-mechanism examples.

All stdlib Python 3.

## Telemetry

`process-design` writes session telemetry to `$PROCESS_DESIGN_LOG_DIR/<date>-<process-slug>.jsonl`, defaulting to `~/.claude/process-design-sessions/`. Best-effort — if the destination is unreachable, the skill completes anyway with a degraded-mode warning. Output correctness does not depend on telemetry working.

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
├── workspaces/                              ← dev artifacts (eval runs, qa-agents reviews)
├── build.sh                                 ← rebuild dist/process-design.plugin
├── README.md
└── LICENSE
```

## License

MIT. See [LICENSE](LICENSE).
