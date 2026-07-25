---
name: system-map
description: >-
  Design and maintain the system-altitude view of many interacting processes: a
  process inventory, the artifact contracts between processes (which output feeds
  which input), a derived wiring diagram, a deletion sweep at system altitude, and an
  explicit top-down/bottom-up reconciliation loop. process-design designs ONE process
  (its boxes are steps of one run); system-map holds MANY processes together (its
  boxes are whole processes, each with its own owner, its own runs, and eventually its
  own spec). Altitude test: if a box hides its own multi-step procedure, it is a
  process — use this skill; if the whole diagram executes in one run, use
  process-design. Use when the user says "map the system", "how do these processes
  fit together", "I keep losing the big picture", "design the <X>
  architecture/pipeline", "there are many workflows here", "zoom out", or describes a
  system like "building a car" with many parallel processes that come together. Also
  use when a process-design session discovers its steps are actually whole processes,
  and after any process-design or build-workflow run, to reconcile the map against
  what the detail work taught. Includes four stopping tests (control, decision,
  ownership, pain) that bound decomposition depth — a box must pass all four to
  earn another level down, which is how the map avoids descending from "eat the
  food" toward cellular metabolism.
compatibility: >-
  Pure markdown reasoning — runs in any environment, no special tools required.
version: 0.2.0
---

# system-map — hold the big picture while doing the detail work

Detail work loses the big picture; big-picture work without detail gets the details
wrong. This skill makes the oscillation between the two explicit, cheap, and logged —
so each descent into one process and each return to the system view compounds instead
of evaporating.

## Core model

- The unit of design and build stays the SINGLE process (`process-design` designs it,
  `build-workflow` makes it runnable). This skill never designs process internals.
- Processes compose through **artifacts, not calls**: process A writes a note, report,
  or queue entry; process B consumes it on its own trigger. Loose coupling is the
  default; direct invocation is the exception and needs a reason.
- The map is **canonical as tables** (Inventory + Contracts). The diagram is derived —
  regenerate it from the tables, never edit it independently. (Same rule as
  process-design: spec canonical, diagram derived.)
- The map is a **living note** (`type: system-map`, `status: living`). One home, no
  copies — a second copy of a living document rots (Linglepedia RCA 2026-07-12).

## Altitude triage (run first, in both directions)

- **Box test:** does each box have its own owner, its own runs, its own would-be
  spec? Then boxes are processes → this skill. Are the boxes actions inside one run
  with one owner? Then boxes are steps → `process-design`.
- **Smell:** a "step" that hides five or more steps of its own is a process in
  disguise. Go up a level.
- Discovering mid-flight that you are at the wrong altitude is normal. Hand off to
  the other skill and carry the material across — nothing is wasted.

## Stopping rules (how deep to go)

Decomposition is a cost. A box earns another level down only when it passes ALL
four tests. Fail any one and the box stays closed — model it as a contract, not
a design.

1. **Control** — can you or your org change what happens inside the box? If not
   (digestion, a customer's procurement committee, the weather), mark it
   `external` and model only its contract: what goes in, what comes out, and how
   you detect when it misbehaves.
2. **Decision** — would the next level of detail change an action, an owner, a
   contract, or a buy/build/delete call? If nothing you would DO changes, the
   detail is trivia. Stop.
3. **Ownership** — will a named person or agent in your world ever own the box's
   internals? No owner, ever → `external`, contract only.
4. **Pain** — is variance inside the box hurting an output metric now, or
   blocking the system goal? Depth is pulled by observed failure, not pushed by
   completeness. A box that works stays closed, even when it fascinates.

What "closed" means depends on which test failed:

- **Control or Ownership failed** → mark the box `external`: contract only
  (inputs, outputs, misbehavior detection), no owner in the inventory.
- **Decision failed** → the box is a primitive (send an email, write a file):
  one atomic step inside its parent process. Never decompose a primitive, and
  give it no inventory row of its own.
- **Only Pain failed** → the box stays closed but KEEPS its owner and its
  metrics in the inventory — it earns descent later, when the data says so.

Corollaries:

- Boxes beneath a closed box do not exist on the map. Rule on a box only when
  its parent is open — "cellular metabolism" never gets a ruling, because
  "digest the food" already closed.
- When the pain sits inside an uncontrollable box, the detection lives at the
  contract edge (stall timers, freshness checks, SLA alarms) and the response
  belongs to the nearest controllable box upstream or downstream.
- Elon's algorithm applies vertically: every LEVEL is a requirement that must
  justify itself, exactly like every step. Depth bloat is still bloat.
- Healthy systems bottom out at two to three levels (map → processes → steps).
  A fourth level is a smell: either a mid-level box is missing, or you are
  designing something you cannot control.
- Record every ruling in the map's Depth Log — "opened (passed all four)" or
  "kept closed (failed <test>)". Rulings are cheap to revisit when the Pain
  test flips.

## Phase 1 — Anchor (Working Backwards at system altitude)

One paragraph: what the SYSTEM as a whole produces, for whom, and how you can tell
it works. If this paragraph cannot be written, the system boundary is wrong — fix
that before inventorying anything.

## Phase 2 — Inventory

One row per member process:

| Process | Purpose (one line) | Owner | Status | Spec |

Status values: `not-designed | spec-draft | spec-verified | implemented | human-run |
external | deleted`. Include human-run and external processes — the map covers the
whole system, not only what agents run. A box may stay `human-run` forever; the
contracts do not care who is on either end.

## Phase 3 — Contracts

Contracts are the load-bearing part. One row per edge:

| Artifact | Producer | Consumer(s) | Home | Freshness | If missing/stale |

- The artifact is a NOUN (a note, a report, a table, a queue entry) with a named
  home (vault path, note type, or store). An edge with no named artifact is a wish,
  not a connection.
- Freshness states the consumer's expectation (e.g., "daily", "before each quote").
- "If missing/stale" states what the consumer does — block, degrade, or alert.

## Phase 4 — Derive the diagram

Mermaid flowchart at process granularity: nodes are processes (annotated with
status, linked to specs), edge labels are artifacts. Regenerate from the tables on
every change.

## Phase 5 — Deletion sweep (Elon's algorithm on boxes, not steps)

Run this on every pass, not once:

- **Orphan output** — an artifact no process consumes → deletion candidate.
- **Phantom input** — an artifact no process produces → a missing process or an
  implicit manual step. Make it explicit, or delete the dependency.
- **Two producers of one artifact** → merge the processes or pick one (RCA
  2026-07-12: second homes rot).
- **Adjacent artifacts that could collapse into one** → simplify the contract.

Log every deletion and simplification in the Deletion Log with the date and the
reasoning. Add-back is cheap; the 10% rule applies — if nothing ever comes back,
the sweep is not cutting deep enough.

## Phase 6 — Reconciliation loop (the oscillation)

Two directions. Run whichever matches where the new information is:

- **Top-down (map → detail):** pick the highest-leverage `not-designed` box —
  apply the Stopping rules before descending; log the ruling — then run
  `process-design` on it → come back to the map: do the detailed spec's real Inputs
  and Output/Consumers match the contract the map assumed? Fix whichever is wrong —
  sometimes the spec reveals the map was naive, sometimes the map reveals the spec
  drifted off-purpose. Log the delta.
- **Bottom-up (detail → map):** a spec changed, or `build-workflow` shipped one →
  re-read its Inputs and Output/Consumers sections → update the Inventory and
  Contracts → re-run the deletion sweep (new orphans and phantoms surface here).
- **Convergence test:** a full pass in either direction that produces zero deltas.
  Until then, keep oscillating. Deltas are the learning, not rework — log them,
  never smooth them over.

Reconciliation Log entry format: date, direction (↓ top-down / ↑ bottom-up), what
changed, what got deleted or simplified as a result.

## Phase 7 — Cadence

- Reconcile after EVERY process-design or build-workflow run that touches a member
  process. It is one table row — keep it cheap enough to be automatic.
- Set a periodic full-pass cadence in the map. Once the system is live and emitting
  metrics, hand the periodic review to `dmaic` (Control phase).

## Relationship to sibling skills

| Skill | Altitude | Job |
|---|---|---|
| system-map | system | Hold the boxes together; contracts; reconciliation |
| process-design | one process | Design one box in detail |
| build-workflow | one process | Make one box runnable and tested |
| qa-agents | any artifact | Adversarial review of a spec — or of this map |
| dmaic | running system | Periodic metrics review and regression guard |

Template: `templates/system-map-template.md`.
