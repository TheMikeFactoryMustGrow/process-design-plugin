---
name: build-workflow
description: >-
  Compile a verified process-design spec into a runnable Claude Code Workflow script
  (.claude/workflows/<slug>.js), test it live, and mark the spec implemented. This is
  the build step of the design→build→harden pipeline: process-design designs ONE
  process; this skill makes that one process runnable; system-map holds many processes
  together. Deterministic control flow (branches, loops, fan-out) becomes plain
  JavaScript; each judgment step becomes a schema-forced subagent call; script gates
  become code checks; human gates become split points that return a needs-decision
  payload. Tests follow the graph-max pattern: one happy-path run with real inputs,
  plus one seeded-failure run per agent gate, so every fail branch runs live before
  the spec is marked implemented. Use when the user says "build this spec", "compile
  this process", "implement this spec", "make this runnable", "turn this spec into a
  workflow", "turn this spec into a script", or picks the claude-code-workflow build
  target at process-design Phase 8. Do NOT use to design a process (that is
  process-design) or to map how processes fit together (that is system-map).
compatibility: >-
  The test phase requires the Workflow tool (Claude Code). Without it, still write the
  script and hand back invocation instructions, and mark the test phase as not-run in
  the report — never mark a spec implemented without a live test pass.
version: 0.1.0
---

# build-workflow — compile a process spec into a runnable Workflow script

One process-design spec in, three artifacts out:

1. `.claude/workflows/<slug>.js` — the runnable Workflow script.
2. A test report with a coverage table (which graph edge each run exercised).
3. The spec flipped `verified → implemented`, with a Change Log line that links both.

The unit of build is always ONE process. If the spec's "steps" are themselves whole
processes with their own owners and runs, stop — that is a system. Hand off to the
`system-map` skill and come back here one box at a time.

---

## Phase 0 — Preflight (gate on the spec)

1. Locate the spec. It must have `type: process-spec`. Check `build_target` — this
   skill serves `claude-code` / `claude-code-workflow` targets.
2. Check `status`. Require `verified`. If the spec is `draft`, offer to run the
   process-design verification phase first. If the user chooses to proceed anyway,
   record a waiver in the test report — do not upgrade the status silently.
3. Run the altitude check (above). Escalate to system-map if the boxes are processes.
4. Inventory the spec: steps + successors, gates + methods, decision rules, edge
   cases, parallelization section, metrics map, inputs + validation, terminal states.
5. Honor the spec's Build Notes contract: decision rules, edge cases, gates, success
   criterion, and metrics are non-negotiable. Language and structure are your
   judgment. Anything else ambiguous: ask, do not guess.

## Phase 1 — Compile plan (summarize before writing)

Read `references/compile-mapping.md` for the full spec→script mapping and code
patterns. Then present the compile plan to the user BEFORE writing code:

- Which gates run as script checks, which as agent judgments, which as human splits.
- Where parallel fan-out happens and where the joins are.
- The args signature (derived from the spec's Inputs section).
- Expected agent count per run. Stay inside the session's workflow size guideline;
  flag it if the spec implies more.
- Every ambiguity you found, surfaced — not papered over.

**Human gates:** a Workflow script runs unattended, so a `method: human` gate cannot
pause mid-run. Never downgrade it to an agent gate silently. Split the script at the
gate: the run returns a `{ state: "needs-decision", ... }` payload, the orchestrating
session presents the decision to the human (decision-list widget where available,
AskUserQuestion otherwise), and a second invocation continues with the decision passed
in `args`.

## Phase 2 — Write the script

Target: `.claude/workflows/<slug>.js`. Rules:

- `meta` block: `name` = the spec slug; `phases` mirror the spec's step groups.
- Accept `args` as an object OR a JSON string:
  `const input = typeof args === 'string' ? JSON.parse(args) : args` — some harness
  paths deliver a string.
- Validate required inputs at the top of the script with exact error messages, using
  the spec's input validation rules.
- Decision rules compile to schema enums / booleans. Branch on validated fields,
  never on prose parsing.
- Script gates are plain JS between `agent()` calls (free, deterministic). Agent
  gates are one `agent()` call with a verdict schema.
- Parallel sections: `pipeline()` by default; `parallel()` only where a stage
  genuinely needs ALL prior results together (a true join).
- Metrics: `log()` at each step boundary; return a structured run record with the
  per-step outcomes the spec's Metrics Map names. The harness journal already
  captures per-agent tokens and duration — do not duplicate it.
- Terminal states: return a payload whose `state` field names the spec's terminal_id.
- Comments follow the project's code-text style rule when one exists (Linglepedia:
  ASD-STE100).

Worked example, when the project carries it: `.claude/workflows/graph-max.js` — the
first compiled graph (plan → work → parallel review → pass gate → deliver).

## Phase 3 — Test (the graph-max pattern)

1. **Happy path.** Run once with real inputs — from the user when available, else
   realistic inputs built from the spec's validation rules. Verify the output against
   the spec's success criterion.
2. **Fail branches.** One seeded-defect run per agent gate: construct an input that
   deterministically fails the gate on the first pass and succeeds after the loop.
   Every gate's fail edge must run live, not just read clean.
3. **Edge cases.** Run the cheap ones from the spec's Edge Cases table. List the rest
   as code-reviewed-only in the report — no silent coverage claims.
4. **Contract check.** If the spec names Consumers, verify the output parses as the
   consumers' declared input format.

Record a coverage table (graph edge / behavior → which run covered it). Example
report, in Linglepedia: `_claude_config/graph-max-workflow-test-2026-07-25.md`.

## Phase 4 — Close out

1. Spec: `status: implemented`; Change Log line; links to the script and the report.
2. If a system-map lists this process, update its inventory row and reconcile the
   contracts (system-map Phase 6, bottom-up direction) — the built reality often
   differs from the contract the map assumed. Log the delta there.
3. Commit per the repo's git rules.

---

## Harness gotchas (learned live, 2026-07-25)

- `args` may arrive as a JSON string. Parse defensively (Phase 2 rule).
- `Date.now()`, `Math.random()`, and argless `new Date()` THROW inside workflow
  scripts (resume safety). The caller stamps timestamps or passes them via args.
- `parallel()` resolves failed thunks to `null` — `.filter(Boolean)` before use.
- Scripts in `.claude/workflows/` become invocable by name once versioned. Check
  the project's `.gitignore` — a `.claude/*` ignore needs a `!.claude/workflows/`
  exception (Linglepedia added it 2026-07-25).
