---
date: {{DATE}}
type: ic-architecture
project: "{{PROJECT NAME}}"
company: "{{[[Company wikilink]] or n/a}}"
status: active
disclaimer: "All committee members are AI personas. Simulated frames model publicly documented decision frameworks (labeled 'simulated') and are not the persons themselves; archetypes are fictional — any resemblance to real individuals is coincidental."
tags:
  - investment-committee
---

# Investment Committee — Architecture

**Business/decision under review:** {{one line}}. **Deal:** see [[IC — Deal Sheet]].
**Sponsor:** {{human sponsor}} (Claude acts as sponsor's analyst between rounds: document
fixes, computations, evidence rebuttals; real-world actions become gated plans only the
sponsor can close).

## Roster

| Member | Lens | File |
|---|---|---|
| {{Name}} *(simulated)* | {{lens}} | [[IC — {{Name}} (simulated)]] |
| {{Name}} | {{lens}} | [[IC — {{Name}}]] |

## Protocol

1. Each round, every member reviews independently and in parallel. Inputs: their own
   persona file **including all prior rounds** (their words bind them), the current deal
   docs, this file's Round Log (sponsor dispositions).
2. Each returns, in persona, 400–900 words: **Vote** (Commit | Conditional | Pass, one-line
   reason; from round 2, state whether it changed and why) · **What's strong** · **Top
   concerns** (ranked, specific, citing the docs' own numbers) · **Specific asks** (each
   actionable — what moves them to Commit).
3. Reviews are appended verbatim to the member's file under `### Round N — <date>`.
   Prior rounds are never edited or deleted.
4. **Sponsor acts before the next round.** Every material concern gets a disposition here:
   `fixed` (docs/model changed — grep-verified propagated) · `answered` (rebutted with
   evidence) · `open → gated action plan` (real-world tasks only the sponsor can close).
   Computable requests get computed and published (Sponsor Packs).
5. Next round: members must acknowledge genuine fixes; zero credit for plans.
6. Terminal: majority Commit/Conditional with **no undispositioned material findings** —
   or a documented kill. Then [[IC — Marching Orders]] + [[IC — Input Dashboard]];
   committee reconvenes on the first passed gate.

## Vote tally

| Round | {{Member cols}} | C/C/P |
|---|---|---|

## Round Log (append-only)

*(Sponsor dispositions appended after each round.)*
