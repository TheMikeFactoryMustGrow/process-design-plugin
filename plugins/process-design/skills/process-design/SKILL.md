---
name: process-design
description: >-
  Collaborate with the user as a thought partner to design a process and produce an
  agent-readable spec PLUS a rendered, foreground-surfaced flowchart, ready to hand
  to a build agent (Claude Code, Claude Design, Python script, Lambda function, or
  any other target). Apply Working Backwards methodology to anchor on the desired
  output. Apply distributed deletion at every sub-step (challenge each addition at
  the moment it is added, not after). Render the visual EARLY, before metrics
  design, and gate it on explicit user confirmation — the flowchart is the primary
  deliverable and must be foreground-surfaced in the agent response, never buried.
  Stress-test inputs and surface edge cases via parallel sub-agent fan-out. Verify
  the spec adversarially using the bundled qa-agents skill (finder + auditor +
  referee). Distinguish script-doable structural checks from agent-required
  semantic judgment. Produce a structured spec with explicit decision rules,
  requirement owners, per-step metrics, gates as visible diagram nodes, edge case
  handling, an implementation-agnostic build-handoff section, and a metrics review
  plan. Internal gates between phases use iterate-in-place with soft fail (after
  one iteration attempt, log the gap as an open question and proceed). Use when the
  user says "design a process", "spec this out for an agent", "help me think
  through this workflow", "make this agent-readable", "draft a flowchart", "turn
  this into something Claude Code can build", "stress-test this design", "what
  edge cases am I missing", "I do this all the time but haven't defined it",
  or "document this so it can be built". Also use when the user uploads a
  hand-drawn diagram, an existing flowchart, or a description of a process they
  want hardened. This skill should trigger liberally — if there is any signal the
  user wants a process designed, hardened, or made build-ready, use this skill.
compatibility: >-
  Phase 6 (Verify) invokes the bundled qa-agents skill via the Skill tool, which
  requires the Task tool. Step 1-exit gap-probe fan-out uses Task when available
  and falls back to in-conversation sequential prompting otherwise (the step
  itself runs in any environment, with the mode logged in the Verification
  Record). Step 2 (Render) uses `mmdc` (Mermaid CLI) when available and falls back
  to Obsidian-renderable fenced markdown otherwise. Helper scripts in `scripts/`
  are Python 3 with stdlib only.
version: 0.2.0
---

# Process Design (Thought-Partner Mode → Reviewable Flowchart + Build-Ready Spec)

This skill collaborates with the user to take a fuzzy process description (or no description, just an intuition) and harden it into a reviewable flowchart backed by an agent-readable spec.

The skill's two deliverables, in priority order:

1. **PRIMARY** — A rendered flowchart (image file on disk, surfaced explicitly in the agent response) that the user can review at a glance.
2. **SECONDARY** — A markdown spec supporting the flowchart: frontmatter, structured sections, metrics map, verification record. The spec is the audit trail; the flowchart is what the user actually consumes.

The skill's goal is not to draw a flowchart for its own sake. The goal is to ask good questions, pressure-test the design, surface what's missing, and produce a first-pass artifact a build agent can implement without significant rework. The visual exists because **a process is reviewable iff its structure is visible at a glance** (P6 below). The spec exists because the visual alone can't carry the metric definitions, edge cases, and verification record that a build agent needs.

This skill ships inside the `process-design` plugin alongside `qa-agents` and the `dmaic` skill family. Step 6 (Verify) delegates adversarial verification to the bundled `qa-agents` skill rather than re-implementing the finder/auditor/referee pattern. The produced spec's Metrics Review Plan section points the user at `dmaic` for running review cycles.

---

## Before You Start

Read these files (in this order) every session:

1. `references/elon-algorithm.md` — drives the distributed deletion stance applied at every sub-step (Steps 1A–1D) plus the concentrated final pruning (Step 3)
2. `references/metrics-principles.md` — the four metric categories, manage-inputs-not-outputs, metric evolution
3. `references/test-writing.md` — the TDD principle applied to spec design (verification suite defined before drafting)
4. `references/spec-principles.md` — the principles that make a spec agent-readable
5. `templates/process-spec-template.md` — the output scaffold

The DMAIC framing and QA Agents pattern are not bundled as reference docs — they live in the sibling skills. Invoke `Skill(dmaic)` if the user wants to walk a Metrics Review Plan, and `Skill(qa-agents)` for Step 6 verification (see Step 6 below).

If the user has uploaded an image of a hand-drawn or printed flowchart, **Step 0 (Ingest)** handles it — transcribe to text first (nodes + edges + labels), confirm the transcription with the user, then proceed.

---

## First Principles

The procedure derives from six principles, not from convention. Every step justifies itself against one of them:

- **P1.** A process is a function `Input → Output`. No defined output → no design possible.
- **P2.** A process is *useful* iff its output produces value the inputs alone don't. Otherwise: overhead. (Powers distributed deletion.)
- **P3.** A process is *correct* iff for valid inputs it produces the specified output, and for invalid inputs it produces a specified failure mode.
- **P4.** A process is *measurable* iff its inputs, transitions, and output emit observable signal.
- **P5.** A process is *improvable* iff measurement connects to a feedback loop that modifies it.
- **P6.** A process is *reviewable* iff its structure is visible at a glance. **The flowchart is the primary deliverable.**

---

## Operating Stance

This skill is the place where comradery is most dangerous. Its job is to question the user's design (or derive one with them, if there isn't one yet), not to draft what they already have in their head.

Concrete rules:

- **Output first, inputs second, transitions third, failure modes fourth.** Always anchor on the desired output.
- **Render early, review hard.** The flowchart is produced before metrics design, and a hard gate confirms the design with the user before metrics get wired.
- **Manage inputs, not outputs.** Output metrics confirm success; controllable input metrics are what you can actually move.
- **Every requirement is guilty until proven innocent.** Verify reasons. Departments cannot be held accountable; people can.
- **Delete at the moment of addition.** P2 applies as a recurring constraint, not a single phase. Every input, every transition, every metric, every check is challenged when it is added.
- **Plus a final pruning pass.** After the visual exists and bloat becomes visible, run the concentrated Elon pass. Two modes (distributed + concentrated), not either-or.
- **Be wrong, not unconfident.** "I'm proposing to delete step 4 because X" beats "you might consider whether step 4 is necessary."
- **Surface assumptions explicitly.** Anything inferred gets written down to confirm.
- **Prefer scripts over agents for deterministic checks; reserve agents for judgment.** Faster, cheaper, more reliable.
- **Fan out to sub-agents for MECE parallelizable work.** Independent agents catch what context-bleed misses.
- **Foreground the visual.** The agent's final response always names the rendered image path on its own line. Never buried.

---

## Architecture Overview

Nine steps (Steps 0–8). Step 0 and Step 8 are conditional. Steps 1A–1D run inside Step 1 with distributed deletion at each sub-step. Step 2 Review is the **HARD GATE** — user confirms the visual before metrics design proceeds.

```
Step 0: Ingest existing description?     (conditional — only fires if user supplied one)
   ↓
Step 1: Anchor — A/B/C/D with distributed deletion
   ↓
Step 1 exit: Gap-probe fan-out (4 sub-agents) with per-agent completion gate
   ↓
Step 2: Render — Mermaid → image file, validate post-render
   ↓
[Step 2 Review — HARD GATE: confirm / reject+named / reject-silent]
   ↓ confirm
Step 3: Final pruning — concentrated Elon pass against the visualized procedure
   ↓
Step 4: Metrics design — output / controllable input / agent / health
   ↓
Step 5: Review cadence + DMAIC plan + telemetry destination
   ↓
Step 6: Verify — verify_spec.py + qa-agents (or inline_simulation)
   ↓
Step 7: Handoff — build prompt + image path + spec path (foreground-surfaced)
   ↓
Step 8: Reconcile spec ↔ source description?  (conditional — only if Step 0 fired)
   ↓
[terminal: spec status:verified + flowchart image + build prompt]
```

Steps 1–2 should be 30–50 minutes of conversation. Steps 3–8 are mostly mechanical given a clean Step 2 confirmation.

### Step 6 vs. Phase 7-style adversarial verify — same boundary, renumbered

| Layer | Tool | Catches |
|---|---|---|
| **Step 6 structural** | `scripts/verify_spec.py` (uses `parse_mermaid.py`) | Frontmatter parses, Mermaid parses, step-ID references resolve, every step has owner, every input has validation, all four metric categories present, at least one terminal state reachable, no unreachable non-terminal nodes, no unbounded loops, **image_freshness (image mtime ≥ spec mtime when image present)**. Deterministic — same spec → same result. |
| **Step 6 adversarial / semantic** | `Skill(qa-agents)` | Untestable rules, missing edge cases, ambiguous decisions, weak metrics, unmotivated steps, internal contradictions in the prose, gaps the structural layer can't see. Judgment-based — different runs may surface different issues. |

If a check is script-doable, it belongs in the structural layer — not the adversarial layer. The qa-agents invocation prompt explicitly excludes the structural layer's territory.

**User-defined checks from Step 1's verification suite.** The standard checks are hard-coded into `verify_spec.py`. Process-specific checks the user adds are *not* automatically runnable by the bundled script — they must either (a) be implementable inline by the agent reading the draft (semantic), or (b) be paired with a small extension script the user writes and the agent invokes. The skill makes this explicit rather than promising automatic enforcement.

---

## Gate Mechanics

Gates between steps enforce that each step's work is complete enough to proceed. Most run internally — the user only sees them when they fail and a fix is needed. **Step 2 Review is the exception: it is always user-visible, by design.**

**Behavior on gate failure:**
1. Identify the specific check that failed and what's missing
2. Loop back to the precise sub-step (not the whole step) to fill the gap
3. After one iteration attempt, if the gap still isn't resolved, log it to "Assumptions and Open Questions" and proceed. This is a **soft fail**.

**Soft-fail accumulation.** Track soft fails per session. Each soft fail emits one telemetry event regardless of whether the user later resolves it. At **the moment a 4th soft fail would be logged** — pause before logging it, surface the running list to the user, and ask: "Resolve some of these now, or accept reduced confidence and continue?"

If the user resolves any soft fails, decrement the count. If the user opts to continue, log the 4th soft fail and continue without re-pausing until **a 7th** would be logged (i.e., another threshold of 3). New soft fails generated by the surfacing dialogue itself do not count toward the threshold until the dialogue is closed.

**Script vs. agent for gate checks:**

| Check type | Examples | Use |
|---|---|---|
| Structural | "All inputs named?", "Every step has owner?", "Mermaid parses?", "Image freshness?" | Script (`verify_spec.py` and friends) |
| Semantic | "Is this output concrete?", "Is this rule testable?", "Does this match user's intent?" | Agent (judgment required) |
| Cross-referential | "Every step in procedure has metric assignment?", "Every input has tracked dimension?" | Script |
| Decision | "Is this the procedure you intended?" (Step 2 Review), "Which is canonical, spec or source?" (Step 8) | **Human** |

When script-doable, prefer scripts. They're faster, cheaper, deterministic, and auditable. When semantic judgment is required, the agent reasons directly. When a real design decision needs to be made, the user makes it.

---

## Step 0: Ingest *(conditional — only fires if user supplied a source description)*

If the user uploaded a hand-drawn diagram, an existing flowchart, an old SKILL.md, or a description of a process they want hardened — ingest it before anchoring.

### 0.1 Parse / transcribe

- Text input: read directly.
- Image input: transcribe nodes + edges + labels to text. Surface OCR uncertainty.
- Markdown / SKILL.md / spec input: parse sections.

### 0.2 Confirm

Show the user what you parsed. Wait for confirmation before proceeding. Do not proceed on silence.

### 0.3 Set the flag

Record `step_0_fired = true` in session state. **Step 8 (Reconcile) consumes this flag.**

### Step 0 exit gate

| Check | Type | Method |
|---|---|---|
| Source description parsed without error | Structural | Script |
| User explicitly confirmed transcription | Decision | Human |
| step_0_fired flag set | Structural | Script |

On fail: re-prompt for re-input or clarification. After one retry, surface to user — Step 0 cannot soft-fail (the source either ingests or doesn't).

---

## Step 1: Anchor

The Working Backwards step. **Distributed deletion stance applied at every sub-step** — challenge every output, every input, every transition, every failure mode at the moment of addition. The deletion isn't a separate phase; it's a recurring constraint.

### 1.1 (Step 1A) Output

Ask, in order:

1. **What does this process produce?** Concrete output — artifact, state, outcome. Not a verb.
2. **What does success look like? What does failure look like?**
3. **Who or what consumes the output?**

**Distributed deletion at 1A:** for each candidate output, ask "is this output necessary, or could the consumer get the same value from the inputs alone?" (P2 test). If output is bloated (multiple outputs when one suffices), challenge.

**Concreteness rule:** the output noun must be (a) singular common noun, (b) consumer-namable. "Data" fails; "approval decision" passes. Order: name noun → name consumers → cross-check that consumers can name this exact noun.

If the user can't articulate a concrete output, the process isn't ready to design. Help them sharpen — do not proceed to 1B.

### 1.2 (Step 1B) Inputs

For each input:
1. What is it, where does it come from, what's its format?
2. Is it controllable? (Critical — controllable inputs become the levers in Step 4.)
3. What makes it valid? Invalid?
4. What happens if it's missing?

**Distributed deletion at 1B:** for each input, ask "is this input necessary, or could the process produce the same output without it?" If two inputs always vary together, can they collapse?

**Cross-input consistency check:** if Step 0 fired (existing description present), the existing description and the named build target must not contradict (e.g., description says "Lambda handler", target says "python script CLI"). Surface conflicts.

### 1.3 (Step 1C) Transitions

Steps, decisions, gates, terminal states.

**Distributed deletion at 1C:** for each candidate transition, run the **trace test**: does it move a controllable input toward the output? If no, propose deletion. If yes, name which input it moves and how.

This is where most aggressive deletion happens — most premature transitions don't survive the trace test.

### 1.4 (Step 1D) Failure modes

Per-step failure + recovery.

**Distributed deletion at 1D:** don't specify failures the process won't actually handle. A failure mode without a recovery plan is documentation theater.

### Step 1 exit gate

| Check | Type | Method |
|---|---|---|
| Output is a noun (not a verb) | Semantic | Agent |
| Output is concrete and consumer-namable | Semantic | Agent |
| At least one controllable input named | Structural | Script |
| Every input has validation criteria | Structural | Script |
| Cross-input consistency: source description doesn't contradict build target (if Step 0 fired) | Cross-ref | Agent |
| Build target specified | Structural | Script |
| Every transition passes the trace test | Semantic | Agent |
| Every step has a named failure mode | Structural | Script |

On fail: loop back to the sub-step (1A, 1B, etc.) that needs more work. After one retry, log gap as open question and proceed (soft fail).

---

## Step 1 Exit: Gap-Probe Fan-Out

The constructive thought-partner phase. **This is the canonical sub-agent fan-out point** — the four sub-types are MECE and parallelizable.

**Implementation:** spawn four `Task` tool invocations in parallel (single message, four tool calls):

- **Agent A — Input stress-testing:** for each input, walk the four dimensions — missing, malformed, boundary, adversarial / unexpected combinations
- **Agent B — Decision rule stress-testing:** for each branch — resolves on input alone? Two agents reach same branch? Boundary input? Ambiguous input?
- **Agent C — Failure-mode probing:** for each step — fails partway? Detectable? Recoverable? Bounded retry? State left behind on abort?
- **Agent D — Missing-step probing:** what does the process assume the user does manually? What does it assume already exists? What handoffs are implied? What observability is missing?

Each agent receives the spec-in-progress (Step 1's outputs) and returns a list of gaps in its category. After all four return, run a **metrics-coverage probe**: with all stress-test results in hand, does every step's metric assignment hold up? Are there steps where measurement should be added based on what surfaced?

If sub-agents are not available in the runtime, fall back to running the four sub-types sequentially in this same conversation. Log the mode in the Verification Record.

### Per-agent completion gate

A wholesale "Task tool unavailable → fall back" check is insufficient: fan-out can succeed for 3 of 4 sub-agents and fail silently for the 4th, leaving a coverage gap the agent doesn't notice. Instead:

- **Per-agent valid-output check.** Each of the 4 must return a parseable, severity-tagged finding list.
- **Partial fan-out → surgical fallback.** If only N of 4 returned valid output, retry the missing slots OR fall back to inline_simulation **for the missing slots only**, not the whole fan-out. Log the mixed mode (`task_fanout` for 3, `inline_simulation` for 1) explicitly.
- **Two-or-more failures → full inline_simulation fallback.** Treat as broad runtime issue.

**Mode logging.** Whichever execution mode runs, emit a `phase_complete` event with `phase: 1_exit` and `detail.mode` (`task_fanout` | `inline_simulation` | `partial_<count>_of_4`), and reflect the mode in the Verification Record as a top-level bullet:

```markdown
- Step 1-exit gap-probe mode: task_fanout
```

or

```markdown
- Step 1-exit gap-probe mode: inline_simulation
```

or

```markdown
- Step 1-exit gap-probe mode: partial_3_of_4 — Agent C timed out; ran inline as fallback
```

### Step 1 exit gate (gap-probe complete)

| Check | Type | Method |
|---|---|---|
| All 4 stress-test sub-types performed | Structural | Script |
| Every input stress-tested across the four dimensions | Cross-ref | Script |
| Every decision rule stress-tested | Cross-ref | Script |
| New gaps reflected in spec sections | Semantic | Agent |
| Every sub-agent returned valid output (or fallback logged) | Structural | Script |

On fail: loop back. Soft fail on retry.

---

## Step 2: Render

**The flowchart is the primary deliverable.** Generate Mermaid → image file.

### 2.1 Mermaid generation

Use the diagram conventions from `templates/process-spec-template.md`. Annotation rules:

**Step nodes (rectangular)** include the requirement owner inline:

```
Step4["Validate input<br/><sub><i>req: Sarah / breaks: corrupt data</i></sub>"]
```

**Gates (hexagons, `{{...}}`)** are exempt from owner annotation — gates' accountability lives in their named verification method (script / agent / human), not in a person.

**Terminal states (stadium, `(...)`)** are exempt — they're end states, not requirements.

### 2.2 Render to image

Run `mmdc` (Mermaid CLI) to render the diagram to `<process-slug>.flowchart.png` next to the spec.

If `mmdc` is not installed, fall back to Obsidian-renderable fenced markdown — write the Mermaid block to a separate `.md` file the user can open in Obsidian for native rendering. Log the fallback mode in the Verification Record.

### 2.3 Post-render validation

- Image file exists at the expected path
- File size > 1 KB (catches truncated renders)
- Exit code 0 from `mmdc`
- Mermaid roundtrip parse: re-read the source from the spec, confirm it matches what rendered

If any fails, surface to user, do not proceed.

### 2.4 Foreground the result

**Critical rule — the headline behavior of this step.** After rendering, the agent's response **MUST** include the image path on its own line at the top of the response, like:

```
**Flowchart:** /path/to/<process-slug>.flowchart.png

Open this image in your viewer to review the procedure before we proceed to Step 2 Review (hard gate).
```

The flowchart is the primary deliverable. It must be findable in the agent's response without scrolling, without searching. **Burying the image path inside a long spec is a defect of this skill** — the user complaint that motivated the foregrounding requirement.

### Step 2 Review — HARD GATE (user-visible, three explicit outcomes)

The user reviews the rendered flowchart and replies with one of three outcomes:

| Outcome | Agent action |
|---|---|
| `confirm` | Proceed to Step 3 (Final pruning) |
| `reject + <step-name>` (named target) | Loop to user-named step (e.g., `reject + Step 1C: I want different transitions`) |
| `reject` (silent — no named target) | Default to Step 1A (Output anchored) — most upstream restart |

**Partial-confirm handling.** "Yes but…" answers are treated as `reject + <step the user names in the clarification>`. Ambiguous "kind of" or "mostly" replies are surfaced back to the user with the three-outcome menu — do not infer.

**Ambiguous-reply rule.** If the user's reply doesn't unambiguously map to one of the three outcomes, do NOT guess. Re-prompt with the three-outcome menu and an explicit "I read your reply as X — confirm or correct."

This gate is the user's first reality check on the design. Skipping it (assuming "they probably mean confirm") defeats the purpose of hoisting render to Step 2.

---

## Step 3: Final Pruning

**Concentrated Elon pass, post-visual.** With the flowchart rendered and reviewed, bloat that wasn't visible in prose now becomes obvious. Run the algorithm one more time.

See `references/elon-algorithm.md` for full operating principles.

### 3.1 Question every surviving requirement

Three tests per step:
- **Trace test:** does this step move a controllable input toward the output?
- **Owner test:** who decided this needs to happen? What breaks if removed?
- **Visualization test (new — only available post-render):** does this node make the flowchart denser without making it more useful?

Mark each step ✅ / 🚩 / ❓.

### 3.2 Delete

For each 🚩, propose deletion. Direct language: "I'm proposing to delete step N." Name the metrics consequence (even though metrics aren't yet wired — reason about what *would* be measured if it were).

The bias is aggressive deletion. Track add-back ratio (steps re-added during review / steps proposed for deletion) as a sanity check — target ~10%, hard ceiling ≥ 0.30. Boundary handling:
- Add-back ratio exactly 0.30 → triggers (use ≥, not strict >).
- Zero deletions proposed → ratio is 0 by convention (vacuous, gate passes).
- Zero deletions accepted but proposals were made → ratio is 0 by convention; the proposing-but-not-accepting itself warrants user reflection.

### 3.3 Simplify

Look for redundant steps, dead branches, no-op transitions, beneficial re-orderings. Each simplification proposal accounts for visualization impact (does the diagram get cleaner?).

### 3.4 Parallelize

For each step or group: MECE? Shared state? Join points? Coordination cost vs. cycle-time gain?

### Step 3 exit gate

| Check | Type | Method |
|---|---|---|
| All deletion proposals explicitly accepted/rejected | Structural | Script |
| Metrics consequence named for each deletion | Cross-ref | Script |
| Every surviving step has named owner and failure mode | Cross-ref | Script |
| Add-back ratio ≤ 0.30 (or vacuous if no deletions) | Numerical | Script |

On fail: loop back. Soft fail on retry.

---

## Step 4: Metrics Design

Now the procedure is settled, design measurement.

### 4.1 Output Metrics

Restate the success criterion as a measurable metric. *"Output is correct"* is not a metric; *"output quality scored ≥4/5 by reviewer"* is.

Specifically include `post_handoff_clarification_rate` if the build target is an autonomous agent — % of build runs returning with spec questions, rolling 20-run window. **This is the headline output metric for any agent-built process.**

### 4.2 Controllable Input Metrics

For each controllable input, name dimensions worth tracking (quality, volume, source, recency). Instrument every controllable input even when uncertain which will matter — the point is to find out.

Ask: *"After 50 runs, what would let you rank controllable inputs by how much each affected output quality?"* If the answer is "nothing currently," design that capability in here.

Note to user: expect input metrics to evolve. The first version is rarely the right one. The Metrics Review Plan (Step 5, implemented via `dmaic`) is the mechanism by which they refine over time.

### 4.3 Agent Performance Metrics

Every step emits the standard set: latency, retry count, confidence/uncertainty, clarification requests, failures, unexpected paths. Mandatory.

For specific high-risk steps, additional signals beyond the standard set may be specified.

### 4.4 Process Health Metrics

Cycle time, cost per run, throughput, parallelization efficiency, mode-of-execution distribution (which fan-out modes ran).

### 4.5 Anecdote and Exception Capture

Where do specific case logs live for review beyond aggregate metrics? What conditions trigger detailed logging?

For this skill specifically: log every Step 2 Review reject, every Step 6 blocking-assertion failure, every post-handoff clarification, every session with ≥3 soft fails.

### Step 4 exit gate

| Check | Type | Method |
|---|---|---|
| All four metric categories have entries | Structural | Script |
| Every controllable input has ≥1 tracked dimension | Cross-ref | Script |
| Output metric is testable | Semantic | Agent |
| Anecdote/exception capture conditions named | Structural | Script |

On fail: loop back to the relevant sub-step. Soft fail on retry.

---

## Step 5: Review Cadence + DMAIC + Telemetry Destination

### 5.1 Cadence

How often does the metrics review run? Common patterns: monthly, on-accumulation-of-N-runs, on-rare-failure-event.

### 5.2 Quorum

Who reviews? At minimum, the process owner + one downstream user.

### 5.3 Trigger conditions

Beyond cadence, what fires an out-of-cycle review? E.g., a critical-severity finding repeating across two runs, post_handoff_clarification_rate exceeding threshold.

### 5.4 Telemetry destination

Where does session telemetry land? Default: `$PROCESS_DESIGN_LOG_DIR/<YYYY-MM-DD>-<process-slug>.jsonl`, falling back to `~/.claude/process-design-sessions/` when the env var is unset. The skill never hardcodes vault- or environment-specific paths.

### Step 5 exit gate

| Check | Type | Method |
|---|---|---|
| Cadence specified | Structural | Script |
| Trigger conditions named | Structural | Script |
| Telemetry destination specified or defaulted | Structural | Script |

---

## Step 6: Verify

Two layers, non-overlapping (see boundary table at top).

### 6.1 Structural — `verify_spec.py`

Run `python scripts/verify_spec.py --final <path-to-spec>`. The script runs every script-doable check from the verification suite and exits non-zero on any blocking failure.

**Exit codes:**
- `0` = verdict-ran-and-passed (all blocking assertions pass)
- `1` = verdict-ran-and-failed (one or more blocking assertions failed)
- `≥2` = uncaught exception or bad invocation (treat as **hard fail**, NOT pass)

**`image_freshness` assertion** — when an image file (`<process-slug>.flowchart.png` or `.svg`) exists alongside the spec, verify image mtime ≥ spec mtime. If the spec was edited after Step 2's render (e.g., during Step 3 pruning that altered the diagram), re-render before re-running other assertions. If no image is found, the assertion is vacuous-pass.

**Structured pass summary.** `verify_spec.py --final` prints `PASSED: N/N final blocking assertions` (or `FAILED: M/N` with the failed-assertion list) so the count is verifiable from output, not just inferred from the exit code. The eval suite asserts on this count line; paired drift between assertion count and eval expectations is a defect.

### 6.2 Adversarial / Semantic — `Skill(qa-agents)`

Step 6 catches what the structural layer cannot: untestable rules, ambiguous decisions, missing edge cases, internal contradictions in the prose, weak metric definitions.

#### Invocation contract

Invoke the bundled qa-agents skill via the Skill tool. Pass a single args string of the form:

```
artifact=<absolute-path-to-draft-spec.md> rubric=process-spec scope="semantic only — Step 6 structural layer covers structure, reachability, loops, and image freshness. Find: untestable decision rules, ambiguous criteria, missing edge cases, weak or vanity metrics, internal contradictions in the prose, unmotivated surviving steps, gaps the structure cannot see."
```

If qa-agents ships a `process-spec` rubric, it will use that; otherwise it falls back to its `document` rubric. The skill handles the finder/auditor/referee orchestration internally and returns a synthesized markdown report containing:

- A list of confirmed findings, each tagged with **finding type** (one of: `output`, `metric`, `step-deletion`, `edge-case`, `verification-check`, `drafting`, `unbounded-loop`, `internal-contradiction`, `metric-impact`, `other`)
- Severity (low / medium / critical, mapped from +1 / +5 / +10)
- Auditor's borderline-flag list (low-confidence accepted findings)
- A score line (Finder total, Auditor net, Referee net)

**Do not re-implement the three-agent pattern when qa-agents is available.**

#### When qa-agents is unreachable

Some runtimes lack the Skill tool or the Task subagent capability qa-agents requires. Simulate the three-agent pattern inline using the rubric in this SKILL.md. **The simulation is structurally similar but adversarially weaker** — the agent doing the finding, auditing, and refereeing shares context with the agent that drafted the spec, so isolation is partial. The skill must still complete and produce its spec. But:

- Telemetry: emit a `phase_complete` event with `phase: 6` and `detail.mode: inline_simulation` (real path: `skill_invocation`).
- Add an explicit line to the spec's Verification Record:

  > **Phase 7 simulation note:** qa-agents skill not reachable; finder/auditor/referee simulated inline. Adversarial isolation collapsed. Treat findings as lower-confidence than a real qa-agents pass; re-run from a runtime with subagent capability before treating the spec as production-grade.

A downstream reviewer reading the spec must be able to see this without trusting the session notes alone.

#### Routing real findings back into the design loop

For each confirmed finding, route by **finding type**:

| Finding type | Loop back to |
|---|---|
| `output` | Step 1A (Output anchored) |
| `metric` | Step 4 (Metrics design) |
| `metric-impact` (deletion's metrics consequence wrong/missing) | Step 3 (Final pruning) |
| `step-deletion` | Step 3 (Final pruning) |
| `edge-case` | Step 1 exit (Gap-probe) |
| `verification-check` | Step 1 (verification suite — re-derive in Step 1) |
| `drafting` (typo, broken ref) | Re-draft in place; no loop back |
| `unbounded-loop` (Gate escape) | Re-draft + open issue against `verify_spec.py` |
| `internal-contradiction` | Earlier of the two contradicting steps (treat the later as inheritor) |
| `other` | Surface to user — judgment call |

**Inline-simulation lowers confidence in routing.** Auditor disprovals become **advisory, not authoritative**. Borderline findings route to "Assumptions and Open Questions" with `inline_simulation_borderline: true`, not to upstream steps.

After a fix, always re-run the structural layer (`verify_spec.py`). Re-invoke qa-agents (full Step 6 adversarial pass) under any of these conditions:

1. The fix looped back to Step 1, 3, or 4 (substantive design content changed).
2. Two or more findings were confirmed in the prior qa-agents pass.
3. A single finding's fix touched more than one section of the spec.

The only case where qa-agents need not re-run: a single `drafting`-typed finding confined to one section.

### Step 6 exit gate (Verify complete)

| Check | Type | Method |
|---|---|---|
| `verify_spec.py --final` exits 0 | Structural | Script |
| Structured PASSED count line present in output | Structural | Script |
| qa-agents pass logged in Verification Record (or inline_simulation note + borderline list) | Structural | Script |
| All real (non-borderline) findings resolved or surfaced to Assumptions | Semantic | Agent |

### Promotion

After all real gaps are fixed (or logged as Assumptions on soft fail), update the spec frontmatter from `status: draft` to `status: verified` and proceed to Step 7.

**Soft-failed gaps and Step 7.** Step 7's Final Verification Assertions are blocking on a verified spec. If a soft-failed gap from any earlier step corresponds to a Step 7 blocking assertion, promotion to `verified` is **not** allowed; the spec stays at `status: draft` and surfaces to the user with the remaining-blockers list.

---

## Step 7: Handoff

Generate the prompt the user pastes into the build agent. **Implementation-agnostic** — describe architectural requirements, not implementation mechanisms. `scripts/render_handoff.py` produces this from the verified spec given a `--target` flag.

### Foregrounding (still applies)

The agent's response surfaces:
- Image path on its own line (carried over from Step 2)
- Spec path on its own line
- Build prompt or path-to-build-prompt on its own line

These three artifacts are the deliverables. Foreground them.

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
| `existing-skill-audit-and-dmaic-feed` | Audit existing skill against spec, surface drift, run DMAIC review next |

The skill names examples; the build agent picks. Prompt template:

> "Implement the process described in `<path-to-spec>`. Honor every decision rule, edge case, gate, and terminal state strictly. The Metrics Map specifies what gets measured at every step — implement deterministic capture using the mechanism appropriate to the build target. Capture must not depend on the executing system remembering to log. If telemetry storage is unreachable at runtime, the process completes with output and logs a degraded-mode warning — output correctness must not depend on telemetry working. Use judgment on implementation language, library choice, file structure, and capture mechanism. Before you start, summarize the spec back to me, including which gates run as scripts vs. agents vs. humans. Surface any ambiguity — don't paper over it."

### Final Verification Assertions

Run by `verify_spec.py --final` after Step 6 has promoted the spec to `status: verified`. **All assertions are blocking.** If any fails, the agent (a) demotes the frontmatter back to `status: draft`, (b) loops back per the table below, (c) re-runs the affected gate after the fix, and (d) re-promotes only on a clean re-run. Do not present the artifact as complete with status `verified` while any blocking assertion fails.

**Single canonical assertion → loop-back table.** Every blocking assertion is enumerated here with both its blocking property and its loop-back target. Adding a row to this table is the only way a new blocking check enters the spec.

| Assertion | Blocking | Loop back to on fail |
|---|---|---|
| Spec file written | Yes | Step 6 (drafting fix) |
| YAML frontmatter parses | Yes | Step 6 (drafting fix) |
| Mermaid block parses | Yes | Step 6 (drafting fix) |
| All step ID references resolve | Yes | Step 6 (drafting fix) |
| Every step has requirement owner | Yes | Step 6 (drafting fix) |
| Every step node displays owner annotation in diagram | Yes | Step 6 (drafting fix) |
| Every Procedure step ID appears in the diagram | Yes | Step 6 (drafting fix) |
| Every decision rule has a Criterion | Yes | Step 1 if rule missing; Step 6 if Criterion line missing |
| Every input has documented validation | Yes | Step 1 if validation missing; Step 6 if line missing |
| Metrics Map covers all four categories | Yes | Step 4 |
| Every controllable input has ≥1 tracked dimension | Yes | Step 4 |
| Every step references the standard performance metrics block | Yes | Step 6 (drafting fix) |
| Metrics Review Plan names cadence and triggers | Yes | Step 5 |
| Every Gate names a verification Method | Yes | Step 1 (verification suite) |
| At least one terminal state reachable | Yes | Step 6 + Gate escape (patch `verify_spec.py`) |
| No unreachable nodes | Yes | Step 6 (drafting fix) |
| No unbounded loops | Yes | Step 6 (drafting fix — add an exit edge) |
| **`image_freshness` (image mtime ≥ spec mtime when image present)** | Yes | Step 2 (re-render) |
| Edge Case section non-empty with content (not just placeholder rows) | Yes | Step 1 exit (gap-probe) |
| Build Notes section non-empty | Yes | Step 6 (drafting fix) |
| qa-agents verification logged in Verification Record (no placeholder) | Yes | Step 6 (re-run) |
| Step 1-exit fan-out mode named in Verification Record | Yes | Step 6 (drafting fix — add the mode line) |
| Step 6 mode named in Verification Record | Yes | Step 6 (drafting fix — add the mode line) |
| Step 6 inline_simulation: Simulation Note present | Yes (only if Step 6 mode = inline_simulation) | Step 6 (drafting fix — add the Simulation Note) |
| Inputs section parses into ≥1 input declaration when non-empty | Yes | Step 6 (drafting fix — bullet syntax must be `- **name**: …` at column 0) |

`verify_spec.py --final` is the executable definition of this table. **Paired drift discipline:** SKILL.md, `verify_spec.py --final`, AND the eval expectations naming the assertion count must change in the same commit. Drift between any of the three is a defect — it means the spec, the verifier, and the regression tests have desynchronized about what's actually blocking. (This is the same principle the skill applies internally between SKILL.md and the script; just extends it to evals.)

If a blocking assertion fails, do not present the artifact as complete. Fix and re-verify.

---

## Step 8: Reconcile *(conditional — only fires if step_0_fired)*

If Step 0 ingested an existing source description, the produced spec almost certainly diverges from the source in places. Surface drift before declaring the session complete.

### 8.1 Diff

Compare each section of the produced spec against the source description. Drift candidates:

- Procedure shape (steps added, removed, reordered)
- Inputs (added, removed, validation tightened/loosened)
- Failure modes
- Metric definitions
- Gate behavior

### 8.2 Surface drift

Present a drift table to the user — for each item: what the spec says, what the source says, severity.

### 8.3 User names canonical

For each drift item, the user names which is canonical:
- **Spec** (source needs to be rewritten to match)
- **Source** (spec is the one that needs revision — loop back to relevant earlier step)
- **Merge** (some hybrid, with user spelling out which parts come from which)

### 8.4 If user refuses to name canonical

A drift item where the user won't pick canonical is logged to "Assumptions and Open Questions" with `reconciliation: open`. The spec ships at `status: verified` (this is not a blocking assertion) but the reconciliation gap is captured for later DMAIC review.

### Step 8 exit gate

| Check | Type | Method |
|---|---|---|
| Drift items enumerated | Structural | Script |
| Each item has a canonical decision (or `reconciliation: open` log) | Decision | Human |
| Reconciliation table present in spec | Structural | Script |

---

## Telemetry (deterministic capture for the skill itself)

The skill captures its own session telemetry — gate fires, soft fails, qa-agents findings, phase loop-backs, user decisions, threshold surfacings, post-handoff clarifications. Telemetry is **best-effort**; if the destination is unreachable, the skill completes anyway with a degraded-mode warning. **Output correctness does not depend on telemetry working.**

**Default location:** `$PROCESS_DESIGN_LOG_DIR/<YYYY-MM-DD>-<process-slug>.jsonl`. If the env var is unset, default to `~/.claude/process-design-sessions/`. The skill never hardcodes vault- or environment-specific paths.

**Event taxonomy.** Every line is a single JSON object: `{ "ts": ISO8601, "phase": int|string, "event": <type>, "detail": {...} }`.

| Event | When | `detail` keys |
|---|---|---|
| `session_start` | Skill invocation | `process_slug`, `build_target`, `step_0_fired` |
| `phase_start` | Each step enters | `phase`, `phase_name` |
| `phase_complete` | Each step passes its gate | `phase`, `duration_ms`, `mode` (Step 1-exit: `task_fanout` \| `inline_simulation` \| `partial_<N>_of_4`; Step 6: `skill_invocation` \| `inline_simulation`) |
| `gate_hard_fail` | First failure of a gate check (before retry) | `phase`, `gate`, `check`, `detail` |
| `gate_soft_fail` | After one retry failed; gap logged to Assumptions | `phase`, `gate`, `check`, `detail` |
| `gate_pass` | Gate passes (after retry, if any) | `phase`, `gate` |
| `soft_fail_threshold_surfaced` | 4th, 7th, … soft fail about to log | `accumulated_count`, `unresolved_list` |
| `step_aborted` | User abandons mid-step (distinct from `step_failed`) | `phase`, `state_at_abort` |
| `user_decision` | User answers a surfacing or path question | `prompt`, `response_summary` |
| `loop_back` | Step 6 routes a finding to an earlier step | `from_phase`, `to_phase`, `finding_type`, `severity` |
| `qa_finding` | Single confirmed finding from qa-agents | `finding_type`, `severity` (low/medium/critical), `where`, `summary` |
| `step_2_review_outcome` | Hard gate decision | `outcome` (`confirm` \| `reject_named` \| `reject_silent`), `named_target` (if any), `time_to_decide_seconds` |
| **`post_handoff_clarification`** | Build agent returns asking for spec clarification (post-Step-7) | `spec_path`, `question_type`, `clarification_text`, `routed_to_step` (which step the question maps to) |
| `step_8_drift_item` | Reconciliation surfaces a drift item | `item`, `canonical` (`spec` \| `source` \| `merge` \| `open`) |
| `session_complete` | Step 7 final assertions passed | `outcome` (`verified` \| `draft-with-blockers`), `total_soft_fails` |

The `post_handoff_clarification` event is the **headline measurable signal** for whether the skill produced a complete spec. A high rate of these events indicates the spec is leaving ambiguities the build agent can't resolve. DMAIC reviews use this to drive improvements.

A telemetry consumer (e.g., a `dmaic` review session) can reconstruct the full session shape: clean runs, hard-failed-then-recovered runs, soft-failed-and-shipped runs, abandoned runs. The `mode` dimension on Step 1-exit / Step 6 events lets a consumer slice further — e.g., compare `inline_simulation` runs against `task_fanout` runs.

---

## What This Skill Does NOT Do

- **No implementation.** Spec only.
- **No telemetry storage decisions for the produced spec's process.** Spec names what to capture; build agent decides where for its own runtime.
- **No domain expertise.** The skill questions; it doesn't validate domain reasoning.
- **No silent deletion.** Every deletion proposed and confirmed, with metrics impact named.
- **No diagram-free output.** Diagram is mandatory AND foregrounded.
- **No vault-specific assumptions in the produced spec.** Portable.
- **No re-implementation of qa-agents internals.** Step 6 delegates.
- **No implementation prescriptions in handoff.** Architecture, not mechanism.
- **No silent skip of Step 2 Review.** The hard gate is mandatory.

---

## Worked Example: Approval Workflow

**Step 0:** No existing description supplied; skipped.

**Step 1A (Output):** approved/rejected request with reasoning. Distributed deletion: candidate "audit log entry" challenged — does the consumer (next reviewer) need it? Yes. Kept.

**Step 1B (Inputs):** request content, reviewer evaluation. Uncontrollable: reviewer availability, submission timing.

**Step 1C (Transitions):** trace test fails on "notify reviewer" and "notify submitter" — these don't move inputs toward output. Distributed deletion: marked 🚩 in-line.

**Step 1D (Failure modes):** reviewer-never-responds, submitter-resubmits-unchanged, ambiguous-criteria.

**Step 1 exit (Gap-probe):** four parallel `Task` invocations. Mode: `task_fanout`. All 4 returned valid. Notable additions: SLA + escalation gate, diff-required validation, validation gate before review.

**Step 2 (Render):** Mermaid generated, `mmdc` renders to `approval-workflow.flowchart.png`. Post-render validation passes. Image path foreground-surfaced in agent response.

**Step 2 Review (HARD GATE):** user replies `confirm`. Proceeds.

**Step 3 (Final pruning):** "notify reviewer" and "notify submitter" formally deleted (already 🚩'd in 1C). Add-back zero. Add-back ratio: 0 (vacuous).

**Step 4 (Metrics):** Output: % reaching terminal state, % approved, reasoning completeness score, **post_handoff_clarification_rate**. Controllable inputs: request.content.completeness, reviewer.evaluation.specificity. Standard performance metrics on every step. Process health: cycle time, % escalated, throughput per reviewer.

**Step 5 (Review cadence):** monthly DMAIC. Quorum: process owner + one reviewer. Trigger: critical-severity qa-agents finding repeating across 2+ runs OR `post_handoff_clarification_rate` > 15%. Telemetry destination: `~/.claude/process-design-sessions/`.

**Step 6 (Verify):**
- `verify_spec.py --final` exits 0. Output: `PASSED: 18/18 final blocking assertions`. (Includes new `image_freshness` — image is fresh, vacuous-pass branch not used.)
- `Skill(qa-agents)` invoked. Mode: `skill_invocation`. Finder identifies 4 issues. Auditor disproves 2. Referee confirms 2 — both `edge-case` findings → loop back to Step 1 exit (gap-probe). Re-run that step for those edges, spec updated, `verify_spec.py` re-run, qa-agents re-run: clean. Spec promoted to `status: verified`.

**Step 7 (Handoff):** `render_handoff.py --target python-script` generates the build prompt. Image path, spec path, and build-prompt path foreground-surfaced.

**Step 8:** Step 0 didn't fire; skipped.

The artifact is now (a) executable by an agent, code, or human, (b) auditable at-a-glance via the **rendered image** with visible gates, (c) measurable from day one with input metrics that will evolve, and (d) iteratively improvable through the metrics review loop (run `Skill(dmaic)` against it). That's the bar.
