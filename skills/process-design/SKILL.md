---
name: process-design
description: >-
  Collaborate with the user as a thought partner to design a process and produce an
  agent-readable spec ready to hand to a build agent (Claude Code, Claude Design, Python
  script, Lambda function, or any other target). Apply Working Backwards methodology to
  anchor on the desired output. Design measurement upfront across four metric categories
  before deletion decisions. Apply Elon's operating algorithm to question and aggressively
  delete. Stress-test inputs and surface edge cases. Verify the spec adversarially using
  the bundled qa-agents skill (finder + auditor + referee). Use sub-agent fan-out for MECE
  parallelizable work. Distinguish script-doable structural checks from agent-required
  semantic judgment. Produce a structured spec with explicit decision rules, requirement
  owners, per-step metrics, gates as visible diagram nodes, edge case handling, an
  implementation-agnostic build-handoff section, and a metrics review plan; render a
  Mermaid diagram with inline requirement-owner annotations. Internal gates between
  phases use iterate-in-place with soft fail (after one iteration attempt, log the gap
  as an open question and proceed). Use when the user says "design a process", "spec
  this out for an agent", "help me think through this workflow", "make this agent-readable",
  "draft a flowchart", "turn this into something Claude Code can build", "stress-test
  this design", "what edge cases am I missing", "I do this all the time but haven't
  defined it", or "document this so it can be built". Also use when the user uploads a
  hand-drawn diagram, an existing flowchart, or a description of a process they want
  hardened. This skill should trigger liberally — if there is any signal the user wants
  a process designed, hardened, or made build-ready, use this skill.
compatibility: >-
  Phase 7 invokes the bundled qa-agents skill via the Skill tool, which requires the
  Task tool. Phase 4 *fan-out* uses Task when available and falls back to in-conversation
  sequential prompting otherwise (the phase itself runs in any environment). Helper
  scripts in `scripts/` are Python 3 with stdlib only.
version: 0.1.0
---

# Process Design (Thought-Partner Mode → Build-Ready Spec)

This skill collaborates with the user to take a fuzzy process description (or no description, just an intuition) and harden it into a spec a build agent can implement without asking. The output is a single markdown file containing a structured spec (canonical, agent-readable) and a Mermaid diagram (derived, human-readable) annotated with requirement owners and verification gates.

The skill's goal is not to draw a flowchart. The goal is to ask good questions, pressure-test the design, surface what's missing, and produce a first-pass artifact that's solid enough to take to a build agent without significant rework. The diagram inherits the quality of the design that produced it.

This skill ships inside the `process-design` plugin alongside `qa-agents` and the `dmaic` skill family. Phase 7 delegates adversarial verification to the bundled `qa-agents` skill rather than re-implementing the finder/auditor/referee pattern. The produced spec's Metrics Review Plan section points the user at `dmaic` for running review cycles.

---

## Before You Start

Read these files (in this order) every session:

1. `references/elon-algorithm.md` — drives aggressive deletion in Phase 3
2. `references/metrics-principles.md` — the four metric categories, manage-inputs-not-outputs, metric evolution
3. `references/test-writing.md` — the TDD principle applied to spec design (verification suite defined before drafting)
4. `references/spec-principles.md` — the principles that make a spec agent-readable
5. `templates/process-spec-template.md` — the output scaffold

The DMAIC framing and QA Agents pattern are not bundled as reference docs — they live in the sibling skills. Invoke `Skill(dmaic)` if the user wants to walk a Metrics Review Plan, and `Skill(qa-agents)` for Phase 7 verification (see Phase 7 below).

If the user has uploaded an image of a hand-drawn or printed flowchart, transcribe it to text first (nodes + edges + labels) and confirm the transcription with the user before doing anything else.

---

## Operating Stance

This skill is the place where comradery is most dangerous. Its job is to question the user's design (or derive one with them, if there isn't one yet), not to draft what they already have in their head.

Concrete rules:

- **Output first, inputs second, metrics third, steps last.** Always anchor on the desired output.
- **Manage inputs, not outputs.** Output metrics confirm success; controllable input metrics are what you can actually move.
- **Every requirement is guilty until proven innocent.** Verify reasons. Departments cannot be held accountable; people can.
- **Every step has metrics before it can be deleted.** Deletion can destroy measurement points; the metrics phase runs before the algorithm phase.
- **Delete aggressively.** Bias toward subtraction. The 10% add-back ratio is a sanity check, not a target.
- **Be wrong, not unconfident.** "I'm proposing to delete step 4 because X" beats "you might consider whether step 4 is necessary."
- **Be a constructive partner, not just a critic.** Subtractive (Elon) and additive (gap probing) work are both required.
- **Surface assumptions explicitly.** Anything inferred gets written down to confirm.
- **Prefer scripts over agents for deterministic checks; reserve agents for judgment.** Faster, cheaper, more reliable.
- **Fan out to sub-agents for MECE parallelizable work.** Independent agents catch what context-bleed misses.

---

## Architecture Overview

Eight phases. Phases 1–5 are dialogue (with internal gates between them). Phase 6 produces the artifact. Phases 7–8 verify and hand off.

```
Phase 1: Working Backwards   → Output → success → consumers → controllable inputs
  [Gate 1]
Phase 2: Metrics Design      → Map measurement across four categories before deletion
  [Gate 2]
Phase 3: Apply the Algorithm → Question → Delete → Simplify → Parallelize
  [Gate 3]
Phase 4: Probe for Gaps      → Stress-test inputs, surface edge cases (sub-agent fan-out)
  [Gate 4]
Phase 5: Verification Suite  → Define what passing looks like before drafting (TDD)
  [Gate 5]
Phase 6: Draft               → Generate the spec from the template
  [Gate 6 — deterministic structural checks via verify_spec.py]
Phase 7: Verify Adversarially → Invoke qa-agents skill (semantic / adversarial layer)
Phase 8: Build Handoff       → Implementation-agnostic prompt for the build agent
```

Phases 1–5 should be 30–50 minutes of conversation. Phases 6–8 are mostly mechanical given a clean Phase 5 output.

### Gate 6 vs. Phase 7 — explicit boundary

Both verify, but the layers are non-overlapping. Gate 6 owns every check that can be expressed as a deterministic operation on the spec text; Phase 7 owns every check that needs judgment.

| Layer | Tool | Catches |
|---|---|---|
| **Gate 6** (structural / topological) | `scripts/verify_spec.py` (which uses `parse_mermaid.py`) | Frontmatter parses, Mermaid parses, step-ID references resolve, every step has owner, every input has validation, all four metric categories present, **at least one terminal state reachable, no unreachable non-terminal nodes, no unbounded loops** (cycles without an exit edge). Deterministic — same spec → same result. |
| **Phase 7** (adversarial / semantic) | `Skill(qa-agents)` | Untestable rules, missing edge cases, ambiguous decisions, weak metrics, unmotivated steps, internal contradictions in the prose, gaps the structural layer can't see. Judgment-based — different runs may surface different issues. |

If a check is script-doable, it belongs in Gate 6 — not Phase 7. Phase 7 should never re-do work the script already did, and the qa-agents invocation prompt explicitly excludes the structural layer's territory.

**User-defined checks from Phase 5.** The standard checks above are hard-coded into `verify_spec.py`. Process-specific checks the user adds in Phase 5 are *not* automatically runnable by the bundled script — they must either (a) be implementable inline by the agent reading the draft (semantic), or (b) be paired with a small extension script the user writes and the agent invokes. The skill makes this explicit in Phase 5 rather than promising automatic enforcement.

---

## Gate Mechanics

Gates between phases enforce that each phase's work is complete enough to proceed. They run internally — the user only sees them when they fail and a fix is needed.

**Behavior on gate failure:**
1. Identify the specific check that failed and what's missing
2. Loop back to the precise sub-step (not the whole phase) to fill the gap
3. After one iteration attempt, if the gap still isn't resolved, log it to "Assumptions and Open Questions" and proceed to the next phase. This is a **soft fail**.

**Soft-fail accumulation.** Track soft fails per session (one process-design invocation, end-to-end through Phase 8). Each soft fail emits one telemetry event regardless of whether the user later resolves it. At **the moment a 4th soft fail would be logged** — pause before logging it, surface the running list to the user, and ask: "Resolve some of these now, or accept reduced confidence and continue?"

If the user resolves any soft fails, decrement the count. If the user opts to continue, log the 4th soft fail and continue without re-pausing until **a 7th** would be logged (i.e., another threshold of 3). New soft fails generated by the surfacing dialogue itself do not count toward the threshold until the dialogue is closed.

The threshold of 3 is a starting heuristic — Gate 6 alone has many sub-checks, and a single complex process can plausibly soft-fail two checks in early phases without indicating a quality problem. A fourth tells you the spec is starting to accumulate debt, which is the right moment to ask.

**Script vs. agent for gate checks:**

| Check type | Examples | Use |
|---|---|---|
| Structural | "All inputs named?", "Every step has owner?", "Mermaid parses?", "Successor IDs exist?" | Script (`verify_spec.py` and friends) |
| Semantic | "Is this output concrete?", "Is this rule testable?", "Does this match user's intent?" | Agent (judgment required) |
| Cross-referential | "Every step in procedure has metric assignment?", "Every input has tracked dimension?" | Script |

When script-doable, prefer scripts. They're faster, cheaper, deterministic, and auditable. When semantic judgment is required, the agent reasons directly. For mixed checks, run the script first and only escalate to the agent if the script passes.

---

## Phase 1: Working Backwards

### 1.1 Output

Ask, in order:

1. **What does this process produce?** Concrete output — artifact, state, outcome. Not a verb.
2. **What does success look like? What does failure look like?**
3. **Who or what consumes the output?**

If the user can't articulate a concrete output, the process isn't ready to design. Help them sharpen.

### 1.2 Inputs

For each input:
1. What is it, where does it come from, what's its format?
2. Is it controllable? (Critical — controllable inputs become the levers in Phase 2.)
3. What makes it valid? Invalid?
4. What happens if it's missing?

### 1.3 Constraints

- Timing, cost, quality bar.

### 1.4 Existing Process or Intuition

Now ask: *do you have a defined process for this, or do you do it intuitively?*

When defined: walk through it, then mentally derive the minimum path from inputs to output yourself, then compare. Differences are signal — steps that don't connect → deletion candidates; missing connections → gap candidates.

When intuitive: derive the steps from inputs to output together.

### 1.5 Build Target

Where does this spec end up? Claude Code, Claude Design, Python script, Lambda, manual, other. Determines the handoff format in Phase 8.

### Gate 1 (Working Backwards Complete)

| Check | Type | Method |
|---|---|---|
| Output is a noun (not a verb) | Semantic | Agent |
| Output is concrete and specific | Semantic | Agent |
| At least one controllable input named | Structural | Script |
| Every input has validation criteria | Structural | Script |
| Build target specified | Structural | Script |

On fail: loop back to the sub-step (1.1, 1.2, etc.) that needs more work. After one retry, log gap as open question and proceed (soft fail).

---

## Phase 2: Metrics Design

Design measurement before deletion. Run this phase even when the user is impatient.

### 2.1 Output Metrics

Restate the success criterion as a measurable metric. *"Output is correct"* is not a metric; *"output quality scored ≥4/5 by reviewer"* is.

### 2.2 Controllable Input Metrics

For each controllable input, name dimensions worth tracking (quality, volume, source, recency). Instrument every controllable input even when uncertain which will matter — the point is to find out.

Ask: *"After 50 runs, what would let you rank controllable inputs by how much each affected output quality?"* If the answer is "nothing currently," design that capability in here.

Note to user: expect input metrics to evolve. The first version is rarely the right one. The Metrics Review Plan (later in the spec, implemented via `dmaic`) is the mechanism by which they refine over time.

### 2.3 Agent Performance Metrics

Every step emits the standard set: latency, retry count, confidence/uncertainty, clarification requests, failures, unexpected paths. Mandatory.

For specific high-risk steps, additional signals beyond the standard set may be specified.

### 2.4 Process Health Metrics

Cycle time, cost per run, throughput, parallelization efficiency.

### 2.5 Anecdote and Exception Capture

Where do specific case logs live for review beyond aggregate metrics? What conditions trigger detailed logging?

### Gate 2 (Metrics Map Complete)

| Check | Type | Method |
|---|---|---|
| All four metric categories have entries | Structural | Script |
| Every controllable input has ≥1 tracked dimension | Cross-ref | Script |
| Output metric is testable | Semantic | Agent |
| Anecdote/exception capture conditions named | Structural | Script |

On fail: loop back to the relevant sub-step. Soft fail on retry.

---

## Phase 3: Apply the Algorithm

The Metrics Map from Phase 2 is now a constraint on deletion. See `references/elon-algorithm.md` for the full operating principles.

### 3.1 Question Every Requirement

Three tests per step:
- **Trace test**: does this step move a controllable input toward the output?
- **Owner test**: who decided this needs to happen? What breaks if removed?
- **Metrics test**: what does this step emit from the Metrics Map? Where does that signal go if deleted?

Mark each step ✅ / 🚩 / ❓.

### 3.2 Delete

For each 🚩, propose deletion. Direct language: "I'm proposing to delete step N." Name the metrics consequence explicitly.

The bias is aggressive deletion. Track add-back ratio (steps re-added during review / steps proposed for deletion) as a sanity check — target ~10%, hard ceiling 30%. If no steps were proposed for deletion, the ratio is 0 by convention (vacuous), the gate passes, and the algorithm phase exits with a note that the design proposed no deletions — which itself warrants user reflection.

### 3.3 Simplify

Look for redundant steps, dead branches, no-op transitions, beneficial re-orderings. Each simplification proposal accounts for metrics impact.

### 3.4 Parallelize

For each step or group: MECE? Shared state? Join points? Coordination cost vs. cycle-time gain?

### Gate 3 (Algorithm Phase Complete)

| Check | Type | Method |
|---|---|---|
| All deletion proposals explicitly accepted/rejected | Structural | Script |
| Metrics impact named for each deletion | Cross-ref | Script |
| Every surviving step has named owner and failure mode | Cross-ref | Script |
| Add-back ratio ≤ 0.30 (or vacuous if no deletions) | Numerical | Script |

On fail: loop back. Soft fail on retry.

---

## Phase 4: Probe for Gaps

The constructive thought-partner phase. **Phase 4 is the canonical sub-agent fan-out point** — the four sub-types are MECE and parallelizable.

**Implementation:** spawn four `Task` tool invocations in parallel (single message, four tool calls):

- **Agent A — Input stress-testing (4.1):** for each input, walk the four dimensions — missing, malformed, boundary, adversarial / unexpected combinations
- **Agent B — Decision rule stress-testing (4.2):** for each branch — resolves on input alone? Two agents reach same branch? Boundary input? Ambiguous input?
- **Agent C — Failure-mode probing (4.3):** for each step — fails partway? Detectable? Recoverable? Bounded retry? State left behind on abort?
- **Agent D — Missing-step probing (4.4):** what does the process assume the user does manually? What does it assume already exists? What handoffs are implied? What observability is missing?

Each agent receives the spec-in-progress (Phases 1–3 outputs) and returns a list of gaps in its category. After all four return, run **4.5 — Metrics Coverage Probing**: with all stress-test results in hand, does every step's metric assignment hold up? Are there steps where measurement should be added based on what the four agents surfaced?

If sub-agents are not available in the runtime, fall back to running 4.1–4.4 sequentially in this same conversation.

**Mode logging.** Whichever execution mode runs — `task_fanout` (four parallel Task subagents) or `inline_simulation` (sequential, same context) — emit a `phase_complete` event with `phase: 4` and `detail.mode: task_fanout | inline_simulation` (single canonical telemetry shape), and reflect the mode in the Verification Record so a downstream reader knows without consulting session-notes:

> **Phase 4 mode:** task_fanout — four parallel sub-agents returned independent gap lists, integrated in 4.5.

or

> **Phase 4 mode:** inline_simulation — Task tool unavailable; sub-types 4.1–4.4 run sequentially in this context. Adversarial isolation between sub-types is partial; treat 4.5 integration as lower-confidence than a fan-out pass.

### Gate 4 (Gap Probing Complete)

The four input stress-test dimensions are: **missing**, **malformed**, **boundary**, **adversarial / unexpected combinations** (the last collapses 4.1's open-ended fifth question into the adversarial bucket).

| Check | Type | Method |
|---|---|---|
| All 4 stress-test sub-types performed (4.1–4.4) | Structural | Script |
| Every input stress-tested across the four named dimensions | Cross-ref | Script |
| Every decision rule stress-tested across the four 4.2 questions | Cross-ref | Script |
| New gaps from 4.1–4.4 reflected in spec sections | Semantic | Agent |

On fail: loop back. Soft fail on retry.

---

## Phase 5: Verification Suite

Apply the TDD principle: define what makes the spec complete and correct *before* drafting. See `references/test-writing.md`.

### 5.1 Diagram Type Selection

| Process shape | Diagram type |
|---|---|
| Branches, loops, no persistent state | `flowchart` (default) |
| Things dwell in named states, react to events | `stateDiagram-v2` |
| Multiple actors exchanging messages | `sequenceDiagram` |
| Concurrent processes with explicit synchronization | `flowchart` with subgraphs |

State the choice and reason explicitly.

### 5.2 Define the Verification Suite

The set of checks the spec must pass. Many fall out of `references/spec-principles.md`:

- Every step has named requirement owner
- Every decision rule testable on input alone
- Every input has documented validation
- Metrics Map has entries in all four categories
- Every controllable input has at least one tracked dimension
- Every diagram node displays its owner annotation
- Every gate in the spec has a named verification method
- Successor step IDs all exist
- At least one terminal state is reachable

Process-specific checks may be added based on what surfaced in Phases 1–4.

For each check, classify as script-doable or agent-required. Gate 6 routes to `verify_spec.py` for the script-doable set; the agent-required subset is checked inline during Phase 6.

### Gate 5 (Verification Suite Complete)

| Check | Type | Method |
|---|---|---|
| Diagram type chosen with explicit justification | Semantic | Agent |
| Verification suite enumerates checks | Structural | Script |
| Each check classified as script or agent | Structural | Script |

On fail: loop back to the relevant sub-step (5.1 or 5.2). Soft fail on retry — log to Assumptions and proceed.

---

## Phase 6: Draft

Use `templates/process-spec-template.md` as the scaffold. Build the spec to pass the verification suite from Phase 5.

### Mid-session checkpointing

**Write the draft to disk as soon as Phase 6 completes**, with `status: draft` in frontmatter. Long sessions can crash; checkpointing prevents loss. The status field flips to `verified` only after Phase 7 passes (see Phase 7 below).

**Path and filename rules.** Default filename: `<process-slug>.process-spec.md` where `<process-slug>` is a kebab-case derivation of the process name from Phase 1.1 (lowercase, alphanumerics + hyphens). Default directory: the user's current working directory at the time the skill was invoked. If a file with the same name already exists, do not overwrite — surface the existing path, show the user what's already there, and ask whether to (a) resume that draft, (b) write to a sibling path with a numeric suffix, or (c) name a different path. Do not write silently.

### Diagram Annotation

Every **step node** (rectangular, the actions in the procedure) includes the requirement owner inline:

```
Step4["Validate input<br/><sub><i>req: Sarah / breaks: corrupt data</i></sub>"]
```

**Gates** appear as explicit decision nodes (hexagon shape) and are **exempt from the owner annotation rule** — a gate's accountability lives in its named verification method (script / agent / human), not in a person. Terminal-state nodes (stadium shape) are also exempt — they represent end states, not requirements.

```
Gate1{{"GATE: input validation passes"}}
Gate1 -->|pass| NextStep
Gate1 -->|fail| Retry
```

### Drafting Principles

- **Atomic claims.** Every decision rule, edge case, successor, and metric is one verifiable statement.
- **Explicit successors.** Every step names possible next steps with testable conditions.
- **Metrics referenced, not restated.** The procedure references "standard performance metrics" and named additions; full definitions live in the Metrics Map.
- **No verifier-workaround commentary in the spec body.** If a `verify_spec.py` check appears to fail for a regex/parsing quirk rather than a real design defect, do **not** reshape the spec to dodge the bug. The spec is the build artifact; workaround commentary corrupts it. Instead: surface the script defect to the user, log it to `session-notes.md`, and either fix the script before continuing, or treat the false fail as a script defect — but only if the carve-out has been earned. **Verifier-bug carve-out is not a free pass.** To exclude a check failure from the soft-fail accumulator, the agent must record three things in a separate `verifier_bugs.md` alongside session-notes: (a) the exact failing check name and the spec content that triggered it, (b) a concrete repro the user can run (`echo "<spec snippet>" | verify_spec.py /dev/stdin`) that demonstrates the script bug, and (c) a description of the input the script *would* have passed if not buggy. Without all three, the failure counts as a regular soft fail and contributes to the threshold-3 accumulator. The carve-out exists to keep script noise out of the user's quality-debt signal — not to give the agent license to dismiss inconvenient design gaps as bugs.

### Gate 6 (Draft Complete — deterministic layer)

Run `scripts/verify_spec.py <path-to-draft>`. The script runs every script-doable check from Phase 5's suite and exits non-zero on any blocking failure. Agent-required checks from the suite are evaluated inline by reading the draft.

Gate 6 catches **structure**: parse failures, missing fields, broken references, unreachable terminals. It is deterministic — the same draft always passes or fails the same way.

On fail: fix the specific check failure. Soft fail on retry — log to Assumptions.

---

## Phase 7: Verify Adversarially (delegates to qa-agents)

Phase 7 catches what Gate 6 cannot: untestable rules, ambiguous decisions, missing edge cases, internal contradictions in the prose, weak metric definitions. It is adversarial-semantic. **Reachability and unbounded-loop detection live in Gate 6**, not here — qa-agents must not be asked to re-do the structural layer's work.

### Invocation contract

Invoke the bundled qa-agents skill via the Skill tool. Pass a single args string of the form:

```
artifact=<absolute-path-to-draft-spec.md> rubric=process-spec scope="semantic only — Gate 6 covers structure, reachability, and loops. Find: untestable decision rules, ambiguous criteria, missing edge cases, weak or vanity metrics, internal contradictions in the prose, unmotivated surviving steps, gaps the structure cannot see."
```

If the qa-agents skill ships a `process-spec` rubric, it will use that; otherwise it falls back to its `document` rubric. The skill handles the finder/auditor/referee orchestration internally and returns a synthesized markdown report containing:

- A list of confirmed findings, each tagged with **finding type** (one of: `output`, `metric`, `step-deletion`, `edge-case`, `verification-check`, `drafting`, `unbounded-loop`, `internal-contradiction`, `metric-impact`, `other`)
- Severity (low / medium / critical, mapped from +1 / +5 / +10)
- Auditor's borderline-flag list (low-confidence accepted findings)
- A score line (Finder total, Auditor net, Referee net)

**Do not re-implement the three-agent pattern here when qa-agents is available.**

**When qa-agents is unreachable.** Some runtimes lack the Skill tool or the Task subagent capability qa-agents requires. In that case, simulate the three-agent pattern inline using the rubric in this SKILL.md. **The simulation is structurally similar but adversarially weaker** — the agent doing the finding, auditing, and refereeing shares context with the agent that drafted the spec, so isolation is partial. The skill must still complete and produce its spec. But:

- Telemetry: emit a `phase_complete` event with `phase: 7` and `detail.mode: inline_simulation` (the real path emits the same event with `detail.mode: skill_invocation`). One canonical event shape — see the Telemetry section.
- Add an explicit line to the spec's Verification Record:

  > **Phase 7 simulation note:** qa-agents skill not reachable; finder/auditor/referee simulated inline. Adversarial isolation collapsed. Treat findings as lower-confidence than a real qa-agents pass; re-run Phase 7 against this spec from a runtime with subagent capability before treating the spec as production-grade.

A downstream reviewer reading the spec must be able to see this without trusting the session notes alone — the spec is the build artifact, and confidence in its verification must be visible at the artifact level.

### Routing real findings back into the design loop

For each confirmed finding, route by **finding type** — not by your reading of the prose. **Routing is binding when Phase 7 ran in `skill_invocation` mode** (real qa-agents, real adversarial isolation) — the wrong phase wastes a retry and risks layering the fix on top of broken upstream work. **In `inline_simulation` mode the routing weakens** (see "Inline-simulation lowers confidence in routing" below) — Auditor disprovals become advisory and borderline findings route to Assumptions instead of upstream phases.

| Finding type | Loop back to |
|---|---|
| `output` — output unclear, success criterion ambiguous, build target wrong | Phase 1 (Working Backwards) |
| `metric` — metric gap, untracked controllable input, unreachable measurement, vanity metric | Phase 2 (Metrics Design) |
| `metric-impact` — deletion proposal whose metrics consequence was not named or named wrong | Phase 3 (Algorithm) |
| `step-deletion` — surviving step that should be deleted, undeleted step without justification | Phase 3 (Algorithm) |
| `edge-case` — missing edge case, untested input class, undetectable failure mode | Phase 4 (Gap Probing) |
| `verification-check` — verification suite check missing or classification wrong | Phase 5 (Verification Suite) |
| `drafting` — typo, broken reference, missing template field, restated-not-referenced metric | Phase 6 (re-draft only, no re-design) |
| `unbounded-loop` — Gate 6 should have caught; if Phase 7 finds one, treat as Gate 6 escape and patch the script | Phase 6 + open issue against `verify_spec.py` |
| `internal-contradiction` — prose says X here, Y there | The earlier of the two contradicting phases (treat the later as the inheritor) |
| `other` — finding doesn't fit | Surface to user — judgment call needed |

**Inline-simulation lowers confidence in routing.** When Phase 7 ran in `inline_simulation` mode, the Auditor shares context with the drafter. That makes false negatives more likely (an Auditor disprovals a real finding using the drafter's own reasoning). Two adjustments apply only in inline-simulation mode:

1. **Auditor disprovals are advisory, not authoritative.** Treat any Finder finding the inline Auditor "disproved" as a borderline finding the user should examine before dismissal. Surface it.
2. **Borderline findings route to Assumptions, not upstream phases.** A medium-severity finding the inline simulator marked borderline should be logged to "Assumptions and Open Questions" with `inline_simulation_borderline: true`, not loop back to Phase 1–5. Re-run Phase 7 from a real-isolation runtime later to resolve.

In `skill_invocation` mode the routing table applies as-is.

After a fix, always re-run Gate 6 (structural layer must re-pass on any draft mutation). Re-invoke qa-agents (full Phase 7) under any of these conditions:

1. The fix looped back to Phase 1, 2, 3, 4, or 5 (the upstream phase changed substantive design content; the resulting draft is materially different).
2. Two or more findings were confirmed in the prior qa-agents pass (multiple sections affected, even if each fix is small).
3. A single finding's fix touched more than one section of the spec.

**The only case where qa-agents need not re-run:** a single `drafting`-typed finding (typo, broken reference, missing template field) confined to one section. Anything else gets re-validated. The cost of an extra qa-agents pass is small; the cost of shipping an unverified design change is large.

### When findings are false positives

Auditor disproved → no spec change. Note the finding for skill improvement (optional: log to telemetry). When the referee disagrees with both finder and auditor, surface to the user — judgment call needed.

### Promotion

After all real gaps are fixed (or logged as Assumptions on soft fail), update the spec frontmatter from `status: draft` to `status: verified` and proceed to Phase 8.

**Soft-failed gaps and Phase 8.** Phase 8's Final Verification Assertions are blocking on a verified spec. If a soft-failed gap from any earlier phase corresponds to a Phase 8 blocking assertion (e.g., "Edge case section non-empty" — soft-failed at Phase 4), promotion to `verified` is **not** allowed; the spec stays at `status: draft` and surfaces to the user with the remaining-blockers list. Soft fail trades quality for momentum within the design loop, but it does not let an incomplete spec escape Phase 8. The user's choices at this point: resolve the blocker, or downgrade scope until Phase 8's assertion is honestly satisfiable. (See "Phase 8 → loop-back" below.)

---

## Phase 8: Build Handoff

Generate the prompt the user pastes into the build agent. **Implementation-agnostic** — describe architectural requirements, not implementation mechanisms. `scripts/render_handoff.py` produces this from the verified spec given a `--target` flag.

### Architectural Requirements (Always)

Every build prompt includes:
1. Honor the spec strictly: decision rules, edge cases, gates, success criterion, metrics specifications.
2. Use deterministic capture for metrics — whatever mechanism fits the build target. Capture must not depend on the executing agent or system "remembering."
3. Implement gates as named in the spec — script, agent, or human, per the gate's specification.
4. Graceful degradation: if telemetry capture fails, the process completes with output and logs a degraded-mode warning. Output correctness must not depend on telemetry working.
5. Surface ambiguity rather than papering it over. Ask before deviating.

### Build-Target-Specific Phrasing

| Target | Capture mechanism examples |
|---|---|
| Claude Code | Hooks (`PreToolUse`, `PostToolUse`, `Stop`), MCP servers |
| Claude Design | Built-in event tracking, session telemetry |
| Python script | Decorators, context managers, structured logging |
| Lambda function | Middleware, CloudWatch Metrics, X-Ray |
| n8n / Zapier | Built-in execution data, custom webhooks |
| Arbitrary code | Structured logging library, OpenTelemetry |

The skill names examples; the build agent picks. Prompt template:

> "Implement the process described in `<path-to-spec>`. Honor every decision rule, edge case, gate, and terminal state strictly. The Metrics Map specifies what gets measured at every step — implement deterministic capture using the mechanism appropriate to the build target. Capture must not depend on the executing system remembering to log. If telemetry storage is unreachable at runtime, the process completes with output and logs a degraded-mode warning — output correctness must not depend on telemetry working. Use judgment on implementation language, library choice, file structure, and capture mechanism. Before you start, summarize the spec back to me, including which gates run as scripts vs. agents vs. humans. Surface any ambiguity — don't paper over it."

### Final Verification Assertions

Run by `verify_spec.py --final` after Phase 7 has promoted the spec to `status: verified`. **All assertions are blocking.** If any fails, the agent (a) demotes the frontmatter back to `status: draft`, (b) loops back per the table below, (c) re-runs the affected gate after the fix, and (d) re-promotes only on a clean re-run. Do not present the artifact as complete with status `verified` while any blocking assertion fails.

**Single canonical assertion → loop-back table.** Every blocking assertion is enumerated here with both its blocking property and its loop-back target. Adding a row to this table is the only way a new blocking check enters the spec; `verify_spec.py --final` is kept in sync with this table.

| Assertion | Blocking | Loop back to on fail |
|---|---|---|
| Spec file written | Yes | Phase 6 (write) |
| YAML frontmatter parses | Yes | Phase 6 (drafting fix) |
| Mermaid block parses | Yes | Phase 6 (drafting fix) |
| All step ID references resolve | Yes | Phase 6 (drafting fix) |
| Every step has requirement owner | Yes | Phase 6 (drafting fix) |
| Every step node displays owner annotation in diagram | Yes | Phase 6 (drafting fix) |
| Every Procedure step ID appears in the diagram | Yes | Phase 6 (drafting fix) |
| Every decision rule has a Criterion | Yes | Phase 1 if rule missing; Phase 6 if Criterion line missing |
| Every input has documented validation | Yes | Phase 1 if validation missing; Phase 6 if line missing |
| Metrics Map covers all four categories | Yes | Phase 2 |
| Every controllable input has ≥1 tracked dimension | Yes | Phase 2 |
| Every step references the standard performance metrics block | Yes | Phase 6 (drafting fix) |
| Metrics Review Plan names cadence and triggers | Yes | Phase 2 (extends to Review Plan) |
| Every Gate names a verification Method | Yes | Phase 5 |
| At least one terminal state reachable | Yes | Phase 6 + Gate 6 escape (structural layer should have caught — patch `verify_spec.py`) |
| No unreachable non-terminal nodes | Yes | Phase 6 (drafting fix) |
| No unbounded loops | Yes | Phase 6 (drafting fix) — add an exit edge |
| Edge Case section non-empty with content (not just placeholder rows) | Yes | Phase 4 |
| Build Notes section non-empty | Yes | Phase 6 (drafting fix) |
| qa-agents verification logged in Verification Record (no placeholder) | Yes | Phase 7 (re-run; see Promotion above) |
| Phase 4 mode named in Verification Record | Yes | Phase 6 (drafting fix — add the mode line) |
| Phase 7 mode named in Verification Record | Yes | Phase 6 (drafting fix — add the mode line) |
| Phase 7 inline_simulation: Simulation Note present | Yes (only if Phase 7 mode = inline_simulation) | Phase 6 (drafting fix — add the Simulation Note) |
| Inputs section parses into ≥1 input declaration when non-empty | Yes | Phase 6 (drafting fix — bullet syntax must be `- **name**: …` at column 0) |

`verify_spec.py --final` is the executable definition of this table. SKILL.md and the script must change together — drift is a defect.

If a blocking assertion fails, do not present the artifact as complete. Fix and re-verify.

---

## Telemetry (deterministic capture for the skill itself)

The skill captures its own session telemetry — gate fires, soft fails, qa-agents findings, phase loop-backs, user decisions, threshold surfacings. Telemetry is **best-effort**; if the destination is unreachable, the skill completes anyway with a degraded-mode warning. **Output correctness does not depend on telemetry working.**

**Default location:** `$PROCESS_DESIGN_LOG_DIR/<YYYY-MM-DD>-<process-slug>.jsonl`. If the env var is unset, default to `~/.claude/process-design-sessions/`. The skill never hardcodes vault- or environment-specific paths.

**Event taxonomy.** Every line is a single JSON object: `{ "ts": ISO8601, "phase": int, "event": <type>, "detail": {...} }`. Types separate session boundaries from in-phase events:

| Event | When | `detail` keys |
|---|---|---|
| `session_start` | Skill invocation | `process_slug`, `build_target` |
| `phase_start` | Each phase enters | `phase`, `phase_name` |
| `phase_complete` | Each phase passes its gate | `phase`, `duration_ms`, `mode` (Phase 4 only: `task_fanout` \| `inline_simulation`; Phase 7 only: `skill_invocation` \| `inline_simulation`) |
| `gate_hard_fail` | First failure of a gate check (before retry) | `phase`, `gate`, `check`, `detail` |
| `gate_soft_fail` | After one retry failed; gap logged to Assumptions | `phase`, `gate`, `check`, `detail` |
| `gate_pass` | Gate passes (after retry, if any) | `phase`, `gate` |
| `soft_fail_threshold_surfaced` | 4th, 7th, … soft fail about to log | `accumulated_count`, `unresolved_list` |
| `user_decision` | User answers a surfacing or path question | `prompt`, `response_summary` |
| `loop_back` | Phase 7 routes a finding to an earlier phase | `from_phase`, `to_phase`, `finding_type`, `severity` |
| `qa_finding` | Single confirmed finding from qa-agents | `finding_type`, `severity` (low/medium/critical), `where`, `summary` |
| `session_complete` | Phase 8 final assertions passed | `outcome` (verified / draft-with-blockers), `total_soft_fails` |

A telemetry consumer (e.g., a `dmaic` review session over many process-design runs) can reconstruct the full session shape: clean runs, hard-failed-then-recovered runs, soft-failed-and-shipped runs, abandoned runs. The `mode` dimension on Phase 4 / Phase 7 events lets a consumer slice further — e.g., compare `inline_simulation` runs against `task_fanout` runs to see if simulation mode produces more late-stage soft fails or weaker qa-agents finding sets.

---

## What This Skill Does NOT Do

- **No implementation.** Spec only.
- **No telemetry storage decisions for the produced spec's process.** Spec names what to capture; build agent decides where for its own runtime.
- **No domain expertise.** The skill questions; it doesn't validate domain reasoning.
- **No silent deletion.** Every deletion proposed and confirmed, with metrics impact named.
- **No diagram-free output.** Diagram is mandatory.
- **No vault-specific assumptions in the produced spec.** Portable.
- **No re-implementation of qa-agents internals.** Phase 7 delegates.
- **No implementation prescriptions in handoff.** Architecture, not mechanism.

---

## Worked Example: Approval Workflow

**Phase 1:** Output: approved/rejected request with reasoning. Controllable inputs: request content, reviewer evaluation. Uncontrollable: reviewer availability, submission timing. Build target: Python script.

**Gate 1 passes.**

**Phase 2:** Output metrics: % reaching terminal state, % approved, reasoning completeness score. Controllable input metrics: request.content.completeness, request.content.length, reviewer.evaluation.specificity. Standard performance metrics on every step. Process health: submission-to-decision cycle time, % escalated, throughput per reviewer. Anecdote/exception: log every escalation in detail; log any decision >7 days from submission.

**Gate 2 passes.**

**Phase 3:** Trace test fails on "notify reviewer" and "notify submitter" — these don't move inputs toward output. Metrics test confirms they emit nothing. Deleted cleanly. Add-back zero. Add-back ratio: 0 / 2 = 0 (sanity check passes).

**Gate 3 passes.**

**Phase 4 (sub-agent fan-out):** Four parallel `Task` invocations return findings. Notable additions: reviewer-never-responds → SLA + escalation gate; submitter-resubmits-unchanged → diff-required validation; ambiguous-criteria → reviewer escalates; malformed-request → validation gate before review.

**Gate 4 passes.**

**Phase 5:** Diagram type: flowchart (procedure with loop, no dwelling). Verification suite enumerated, all checks classified as script or agent.

**Phase 6:** Spec drafted with two visible gates (input validation, SLA timeout). Written to disk as `status: draft`. `verify_spec.py` (Gate 6) passes on first run.

**Phase 7:** `Skill(qa-agents)` invoked on the draft. Finder identifies 4 issues (3 low, 1 medium). Auditor disproves 2 as false positives (the spec already addresses them). Referee confirms 2 real issues — both are missing edge cases. Per the routing table, both fixes loop back to Phase 4. Phase 4 re-run for those edges, spec updated, verify_spec.py re-run on the updated draft. Re-invoke qa-agents on the updated draft: clean. Spec promoted to `status: verified`.

**Phase 8:** `render_handoff.py --target python-script` generates the build prompt — capture mechanism examples include decorators and context managers; structured logging library prescribed for the deterministic-capture property.

The artifact is now (a) executable by an agent, code, or human, (b) auditable at-a-glance via the diagram with visible gates, (c) measurable from day one with input metrics that will evolve, and (d) iteratively improvable through the metrics review loop (run `Skill(dmaic)` against it to walk the cycle). That's the bar.
