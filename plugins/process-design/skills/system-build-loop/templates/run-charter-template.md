---
type: run-charter
system: "[[<system map note>]]" # name the note Phase 1 will create; may dangle until then
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
status: active # active | converged | budget-exhausted | blocked | ratified
current_phase: 0 # 0-6; update at every phase boundary
iteration: 1 # the iteration in progress or next to start (not iterations completed)
run_dir: "<folder holding this run's briefs/, specs/, reports/ — all artifact paths derive from it>"
---

# <System Name> — Build-Loop Run Charter

## System Goal (Working Backwards)

<What the whole system produces, for whom, verifiable how. One paragraph.>

## Definition of Done (this run)

<The finish line for THIS RUN, smaller than "perfect": converged map? N boxes
designed? box X built and tested?>

## Constraints & Do-Not-Touch

- <from the ramble>
- <standing guardrails: no money movement, no external sends/publishing, ...>

## Budget

- <wall-clock / iterations / tokens — default: three full iterations>

## Interrupt Log

<Questions asked of the user mid-run. Should be empty or nearly so — each entry
must cite interrupt condition 1 (goal unstatable) or 2 (blocked).>

- (none)

## Assumptions Ledger

| ID | Assumption | Confidence | Evidence | Status |
|---|---|---|---|---|
| A1 | <judgment call made autonomously> | <high \| medium \| low> | <source/reasoning> | pending |

Status values: `pending | ratified | rejected`. Confidence scale: high | medium
| low, derived from evidence strength with the derivation stated — never
invented.

## Degradations

- <capability that was unavailable and what was used instead — e.g., "no web
  search; rules layer sourced from vault only">

## Iteration Log

Append one row at each Phase 5 (reconcile ascent). Empty until then.

| # | Date | Phases run | Map deltas | Deletions | Notes |
|---|---|---|---|---|---|
| <n> | YYYY-MM-DD | <e.g. 2→5> | <count + one-liners> | <what got cut> | |
