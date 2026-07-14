---
name: investment-committee
description: >-
  Convene or resume a standing multi-persona AI investment committee on any
  deal, plan, or major decision — parallel adversarial persona reviews with
  append-only memory, sponsor dispositions between rounds, hard terminal
  conditions, and Marching Orders as the closing deliverable. Battle-tested on
  a real infrastructure investment decision: three adversarial rounds to a
  unanimous conditional commit, with the committee catching nine real errors in
  the sponsor's own rebuilt materials. Use when the user says "run the
  investment committee", "IC review", "convene the committee", "stress-test
  this deal/plan/decision", "run this by the committee", or wants adversarial
  multi-persona review of a proposal before committing money or strategy.
---

# Investment Committee

Run a **standing committee of AI personas** against a deal or decision, over as many
adversarial rounds as it takes to reach a defensible terminal state. This is not a
one-shot critique: members have **permanent, append-only memory**; the sponsor must
**disposition every material concern between rounds**; and plans earn **zero credit**
until they become paper or actions.

Where `qa-agents` stress-tests an *artifact* once, this skill stress-tests a *decision*
over time — the committee persists, remembers, and reconvenes on passed gates.
Templates: `templates/` beside this file.

## Inputs (ask only for what you cannot infer)

1. **The deal/decision docs** — paths to existing documents, or enough substance to
   draft a Deal Sheet from (never invent deal facts; every number must trace to a
   source doc).
2. **Committee home** — default `<project folder>/Investment Committee/`; confirm the
   project folder if ambiguous.
3. **Roster** — default is the 7-lens blend below; the user may override size or lenses.
4. **Termination request** — default: run rounds until terminal (see §Terminal).

## Default roster (7 lenses)

Two *simulated public decision frames*, ALWAYS labeled **"(simulated)"** in the file
name and frontmatter — e.g., a working-backwards/one-way-doors frame and a
question→delete→simplify/idiot-index frame — plus five *fictional archetypes*:

| Lens | Archetype |
|---|---|
| Customer obsession · working backwards · one-way vs two-way doors | simulated frame 1 |
| Question → delete → simplify · idiot index · physics first | simulated frame 2 |
| Operator who ran this exact business through a full cycle and made its mistakes | fictional |
| Sector private capital — underwriting, structure, downside, exit | fictional |
| The customer — the person who would actually sign the contract | fictional |
| Brand & growth — GTM, narrative, pricing posture | fictional |
| Contrarian cost engineer — idiot-indexes every capex/opex line | fictional |

The Architecture file's frontmatter MUST carry the disclaimer: *"All committee members
are AI personas. Simulated frames model publicly documented decision frameworks and are
not the persons themselves; archetypes are fictional — any resemblance to real
individuals is coincidental."* Never cast a real private individual as a member.

## Scaffold vs. resume (check FIRST)

Look for `IC — Architecture.md` in the committee home:

- **Absent → SCAFFOLD** from `templates/`: Architecture (roster, protocol, empty vote
  tally, Round Log), Deal Sheet (from the deal docs — cite, don't invent), one member
  file per persona. Commit the scaffold before Round 1.
- **Present → RESUME.** Read the Architecture vote tally + Round Log to find the last
  round N and its dispositions; read EVERY member file end-to-end (their prior words
  bind them — quote flip conditions back verbatim). Convene Round N+1. **Never edit or
  delete prior-round content anywhere** — corrections enter as dated notes only.

## Round protocol

1. Every member reviews **independently and in parallel** (orchestrate with parallel
   subagents — a workflow/agent-spawning tool with one agent per member and a
   structured-output schema per review where available). Inputs per member: their full
   persona file including all prior rounds, the current deal docs, and the Architecture
   Round Log (sponsor dispositions).
2. Each returns, **in persona, 400–900 words**: **Vote** (Commit | Conditional | Pass,
   one-line reason; from Round 2 onward, state whether it changed and why) · **What's
   strong** · **Top concerns** (ranked, specific, citing the docs' own numbers) ·
   **Specific asks** (each actionable — what moves them to Commit).
3. Append each review **verbatim** to the member's file under `### Round N — <date>`.
4. Update the Architecture vote tally. Commit the round (if in a git repo).

**Orchestration hardening (learned the hard way):** have each agent ALSO write its memo
to a file before returning structured output — when structured output fails on infra
limits, the memo on disk is truth. On agent/infra failure, resume the orchestration
rather than re-running completed members.

## Sponsor disposition pass (between every pair of rounds)

Acting as the sponsor's analyst: every material concern gets exactly one disposition in
the Architecture Round Log — **`fixed`** (docs/model actually changed), **`answered`**
(rebutted with evidence), or **`open → gated action plan`** (real-world tasks only the
human sponsor can close, with named owners). Computable asks get computed and published
as numbered **Sponsor Packs** (`IC — Sponsor Pack R<N>.md`).

**Binding defect rules** (each caused real damage in the field):

1. **Grep-verified propagation:** a disposition may be marked `fixed` ONLY after a
   corpus-wide search proves no stale copy of the corrected figure/claim survives in any
   deal doc (per-item FOUND checks). *Claimed-fixed-but-not-propagated was caught three
   times in the original deployment.*
2. **One-convention rules:** one discount rate, one break-even phrasing, one canonical
   figure per quantity, everywhere. Committee members WILL catch convention drift.
3. **Zero credit for plans:** a well-designed gate is paper until passed. Members must
   acknowledge genuine fixes; still-open items split into *document work possible now*
   vs *closable only by doing*.
4. **Append-only discipline is load-bearing:** dated correction notes, never silent
   edits — it is what makes "their words bind them" credible by Round 3.

## Terminal

**Majority Commit/Conditional with NO undispositioned material findings — or a
documented kill.** On terminal: write **`IC — Marching Orders.md`** (prioritized
real-world actions + each member's verbatim-precise flip conditions) and a standing
**`IC — Input Dashboard.md`** (monthly controllable inputs, one row per period). The
committee then stands and reconvenes on the **first passed gate — not on new documents**.

A stable post-terminal round attacking the sponsor's own new deliverables is high-value
(in the original deployment, that round found nine real errors in the sponsor's rebuilt
pitch materials).

## Guardrails

- Personas per the roster rules above; disclaimer always present.
- The committee **cites the deal docs' own numbers** — it never invents deal facts; where
  evidence doesn't exist, absence-of-evidence is itself a finding.
- Committee files inherit the **project's confidentiality tier** — counterparty names on
  unsigned interest stay internal; check for a project confidentiality note before
  excerpting anything outward.
- Follow the host project's note conventions (frontmatter, link style); commit after
  every round if in a git repo.
- Composes with siblings: `qa-agents` for single-artifact adversarial review inside a
  round; `elons-operating-algorithm` to pressure-test the deal's own structure before
  Round 1.
