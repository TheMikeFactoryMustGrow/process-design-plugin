---
name: system-build-loop
description: >-
  Autonomous system design-and-build loop: the user rambles an idea; the loop
  returns hours or days later with a researched system map (a goal per box),
  designed subsystems, built-and-tested workflows where warranted, and ONE
  batched decision review of every assumption made along the way. Orchestrates
  the sibling skills over many iterations — system-map (the board), per-box
  research fan-out (first-principles floor → rules layer → prior art/creative
  layer), process-design in soft-fail autonomous mode (assumptions logged, not
  asked), selective build-workflow builds, then bottom-up reconciliation — and
  repeats until the map converges, the budget runs out, or the run is genuinely
  blocked. Use when the user says "run the build loop", "autonomous mode", "work
  on this for a few hours/days", "go build this system", "take this idea and run
  with it", "come back with something I can review", or rambles a business /
  engineering system and wants deep, researched, first-principles work without
  being asked questions along the way. Do NOT use for a single process
  (process-design), a quick map (system-map alone), or when the user wants to
  collaborate interactively step by step.
compatibility: >-
  Orchestrates sibling skills: system-map, process-design, build-workflow,
  qa-agents. Research layers use web search when available and degrade to
  vault/repo sources with the gap logged. Multi-day runs need a scheduler
  (Routines / cron) or resumable sessions; all loop state lives in notes, so any
  session can resume from the charter.
version: 0.1.0
---

# system-build-loop — ramble in, ratified system out

> **Multi-runtime (Claude Code · Grok Skills · Grok Build):** Claude-native steps in this skill stay as-is on Claude Code. On Grok or other Agent Skills hosts, map tools via `references/agent-runtimes.md` (same procedure — only tool names differ).

The contract: the user gives a ramble and goes away. The loop comes back with
thoughtful, well-reviewed, well-researched work — and one batch of decisions.
It does not ask questions along the way, except at the two defined stuck points.

## Operating mode

- **Autonomous by default.** Every judgment call becomes a logged assumption
  with a confidence (high | medium | low — derived from evidence strength,
  derivation stated, never invented) and an evidence line — never a question.
  Soft-fail everywhere (inherited from process-design): one honest iteration
  attempt, then log the gap and proceed.
- **Interrupt rule — the only two reasons to contact the user mid-run:**
  1. **Phase 0 fails** — the system goal cannot be stated after honest effort.
  2. **Blocked** — the run cannot usefully continue without one answer: more
     than half of the remaining open boxes in the definition of done hang on
     it (when the definition of done has no box count, judge blocked as: the
     next full iteration cannot run without the answer). Human-reserved
     decisions (money movement, outward commitments, publishing, scope
     changes) follow the same test: when one blocks the run, interrupt; when
     it does not, ledger it as PENDING-RATIFICATION for the Phase 6 batch. Doing the reserved action autonomously is never an option,
     ask or no ask.
  Everything below that bar: assume, log, proceed. While waiting on an
  interrupt answer, keep working everything that does not hang on it and park
  the rest.
- **Autonomy widens work, never permissions.** Research is read-only. Builds
  run tested and isolated. Nothing publishes, sends, or spends externally.
  Guardrails are inherited from the project, not renegotiated by this skill.

## State (what makes multi-day runs possible)

All loop state lives in notes, so any session — including a scheduled wake-up —
can resume:

- **Run charter** (`templates/run-charter-template.md`): goal, definition of
  done for this run, constraints, budget, assumptions ledger, iteration log.
- **The system map** (system-map skill) is the shared board; research briefs,
  specs, and test reports link from it.

On resume: read the charter → read the map → continue at the recorded phase.
Update the charter at every phase boundary — a run that dies mid-phase must
lose at most one phase of work.

## Durable memory, compaction, and idempotency

Long runs WILL have their conversation context compressed. Design for it:

- **Durable notes are the only memory.** Anything not written to the charter,
  the map, or a linked artifact is lost by design. Never rely on conversation
  context for state. Re-read the charter and the map at every phase boundary,
  even when memory feels fresh — after compaction it lies.
- **Deterministic artifact homes.** Every artifact has one predictable path
  derived from stable slugs inside the charter's `run_dir` (for example
  `<run_dir>/briefs/<box-slug>.md`, `<run_dir>/specs/<box-slug>.md`). Before
  creating any artifact, check the path: extend or update in place, never
  write a second copy (the no-divergent-copies rule).
- **Stable IDs, never renumbered.** Ledger assumption IDs (A1, A2, …), box
  slugs, and iteration numbers are append-only identifiers. A re-run reuses
  them; it never renumbers or forks them.
- **Idempotent phase re-entry.** Re-running any phase after an interruption
  must converge to the same state: detect completed work by READING artifacts
  (does the brief exist? does the spec verify?), never by remembering. A phase
  that finds its outputs already present records "verified present" in the
  charter and moves on instead of regenerating.
- **Charter as write-ahead log.** `current_phase`, `iteration`, and
  `last_updated` change at every boundary; commit and push durable notes at
  phase boundaries too, so a dead container loses nothing that was finished.

## Phase 0 — Charter (once per run)

Extract from the ramble:

1. **System goal** (Working Backwards anchor): what the whole system produces,
   for whom, verifiable how.
2. **Definition of done for THIS RUN** — converged map? N boxes designed? box X
   built? The loop needs a finish line smaller than "perfect". When the ramble
   has no finish line ("see how far you get"), choose one sized to the budget
   and log it as a ledger assumption — never ask.
3. **Constraints and do-not-touch list** — explicit, from the ramble plus
   standing guardrails.
4. **Budget** — wall-clock, iterations, or tokens. A vague budget ("maybe a
   weekend") is still a given budget: interpret it and log the interpretation
   as a ledger assumption. The default — three full iterations — applies only
   when the ramble gives no budget at all.

Write the charter note, naming the system-map note that Phase 1 will create
(the link may dangle for one phase). If the goal cannot be stated after honest
effort, this is the one allowed up-front question — ask it, wait for the
answer, then charter and proceed.

## Phase 1 — Map (system-map skill)

Build or update the system map: inventory, contracts, wiring diagram — plus a
**goal for every box**: what the box must produce for the system goal to hold.
Apply system-map's Stopping rules to every box; record the Depth Log rulings.
Boxes that fail a stopping test get contracts, not designs — that is the depth
limiter for the whole run.

## Phase 2 — Research fan-out (per open box, parallel)

Three layers per box, cheapest truth first. Run boxes in parallel where the
environment allows; each layer produces citations, not vibes.

1. **First-principles floor** — what do physics, math, and unit economics say
   is possible, and what are the real constraints? Build up from the floor. No
   analogy-to-competitors allowed at this layer.
2. **Rules layer** — what is legal, what is gray, what is regulatory-blocked
   but physically possible. A physics-possible / regulation-blocked finding is
   a candidate "work with the regulators" box, not a wall.
3. **Prior art + creative layer** — how others solve it, where they are
   cargo-culting, and what a 10x version looks like.

Output: one cited research brief per box, linked from the map. When internet
research is unavailable, use vault and repo sources and log the degradation in
the charter.

## Phase 3 — Design descent (process-design, autonomous)

For each open box, run process-design in soft-fail mode: judgment calls become
ledger assumptions (id, confidence, evidence, status `pending`), human gates
become PENDING-RATIFICATION entries instead of stops (the interrupt rule still
applies when one blocks the run). Adversarial verification
(qa-agents) still runs — it is cheap relative to being wrong for two days.

## Phase 4 — Build (build-workflow, selective)

Build a box only when ALL hold: the spec is verified; the build target is
claude-code-workflow; and building it now either teaches the system something
(a contract gets exercised for real) or delivers standalone value. Every build
gets the full test pass (happy path + seeded fail per gate). Building
everything is NOT the goal of an iteration — learning is.

## Phase 5 — Reconcile ascent (system-map, bottom-up)

Feed deltas from the specs and builds back into the map. Then ask the system
questions: merge boxes? split one? parallelize a sequential chain (throughput
and cycle time)? did the detail work reveal a missing box? Re-run the deletion
sweep and the stopping rules. Record the iteration in the charter log.

## Loop control

Repeat Phases 2→5. Stop at the FIRST of:

- **Converged** — a full pass produces zero map deltas and no new assumptions.
- **Budget** — the charter budget is spent. Report progress honestly; never
  rush the last iteration to fake convergence.
- **Blocked** — interrupt rule condition 2.

Prefer finishing one full 2→5 cycle over starting a wider descent: the ascent
is where consolidation and parallelization insights live, and the user's
"go down, come back up, reconcile, repeat" rhythm is the whole point.

## Phase 6 — Return (the deliverable)

One package, foregrounded:

1. The updated system map (diagram surfaced, not buried).
2. Per-box research briefs and specs; built workflows with their test reports.
3. The run charter with its iteration history — the story of what changed and
   what got deleted.
4. **The decision review** — every ledger assumption and pending ratification,
   batched into ONE review: strong-vs-judgment marker, one-line recommendation,
   derived (never invented) confidence, evidence line. Use the decision-list
   widget where the surface supports it; otherwise a single numbered list
   answerable in one reply. Never serial questions.

After ratification: execute approvals, walk each discuss/comment, and fold
rejections back into the map as deltas — they usually trigger one more
reconcile pass.

## Relationship to siblings

| Skill | Role in the loop |
|---|---|
| system-map | The board: inventory, contracts, stopping rules, reconciliation |
| process-design | Designs one box (run here in soft-fail autonomous mode) |
| build-workflow | Makes one box runnable and tested |
| qa-agents | Adversarial verification inside the descent |
| dmaic | Takes over the review cadence once the system is live |

This skill adds only the loop that drives them, the interrupt contract, and
the batched return.
