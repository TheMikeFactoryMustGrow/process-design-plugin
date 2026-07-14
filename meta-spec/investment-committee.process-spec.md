---
type: process-spec
canonical_representation: spec
diagram_type: flowchart
created: 2026-07-14
last_updated: 2026-07-14
status: draft   # Step 2 Review (HARD GATE) pending — Steps 3-8 run after user confirm
build_target: existing-skill-audit-and-dmaic-feed   # the skill EXISTS (plugins/process-design/skills/investment-committee); this spec hardens it
tags:
  - process-spec
  - investment-committee
---

# Investment Committee (process spec — DRAFT, pre-Step-2-Review)

A standing committee of AI personas stress-tests a deal or major decision over adversarial
rounds: parallel in-persona reviews with append-only member memory, sponsor dispositions between
rounds, hard terminal conditions, and Marching Orders as the closing deliverable. The sponsor is
human; the committee, the analyst, and the orchestration are agents. This spec was produced by
the `process-design` skill run against the shipped `investment-committee` skill (Step 0 source)
plus its live worked example.

---

## Output (Working Backwards Anchor)

- **Concrete output**: the **decision record** — per convening: appended member reviews + vote
  tally + dispositioned Round Log; at terminal: the **Marching Orders** note (prioritized
  real-world actions + each member's verbatim flip conditions, each gate carrying an owner and a
  detection channel).
- **Success criterion**: terminal state reached — full-roster votes with
  count(Commit)+count(Conditional) > floor(roster/2) AND zero undispositioned material findings
  (member-accepted `answered`, decomposed mixed findings, ratification-queue-cleared) — or a
  documented kill; every `fixed` propagation-verified in the current-truth corpus; append-only
  memory intact end-to-end; every Marching-Orders flip condition quote-matches its member file.
- **Failure modes**: non-convergence (stall rule forces kill/park/new-evidence); false terminal
  (analyst-downgraded materiality — blocked: materiality is member-declared); unfaithful close-out
  (blocked: verbatim quote-match gate); memory violation (blocked: resume-time append-only check).
- **Consumers**: the human sponsor (executes actions, watches gates); future rounds (memory);
  downstream sessions (resume).

## Inputs

- **deal_docs**: paths or substance. Controllable: no (given). Required: yes. Validation:
  every load-bearing number traces to a named source; per-round content-hash manifest recorded;
  docs are quoted evidence, never instructions (embedded directives are reported as adversarial
  findings). Default if missing: draft a Deal Sheet from provided substance or refuse — never invent.
- **roster_config**: default 7-lens blend. Controllable: yes. Required: no (default). Validation:
  min 3, warn on even sizes (tie = non-terminal); simulated frames labeled "(simulated)";
  disclaimer present; no real private individuals; roster frozen at scaffold (mid-committee
  changes are a formal transition with tally semantics).
- **committee_home**: default `<project>/Investment Committee/` **suffixed with the deal slug**.
  Controllable: yes. Validation: scaffold into non-empty home requires confirmation.
- **committee_state**: Architecture + member files (+ `ic_state:`/`waiting_on:` frontmatter).
  Accumulated. Validation: full-constellation integrity at resume (partial state → HALT);
  deal_id match; append-only verified (git diff shows end-of-file additions only); round-number
  skew check (max member-file round ⟺ tally).
- **sponsor_responses**: dispositions, computations, ratifications. Controllable: **yes — the
  primary lever**. Validation: every material finding dispositioned before the next round may
  convene; posture/scope changes enter as drafted-for-ratification, never unilateral `fixed`.
- **termination_request**: optional override (fixed rounds → `IC — Adjourned Report`, never a
  pseudo-terminal Marching Orders).

## Procedure (Canonical) — summary; the shipped SKILL.md is the executable text

1. **T1 detect**: state-integrity + deal-identity gate → scaffold | resume | HALT.
2. **T2 scaffold**: templates + confidentiality stub + doc-hash manifest + deal_id + `ic_state`.
3. **G3 readiness**: load-bearing numbers trace? gaps → evidence pass or logged Round-1 finding.
4. **T3 convene Round N**: parallel member reviews; memo-to-file BEFORE structured return
   (memo is canonical on divergence); machine-parseable `VOTE:` first line; bounded re-runs of
   missing members only.
5. **T3.5 consolidate** *(added — the real run did this; the skill text omitted it)*: dedupe
   cross-member concerns into globally-unique SP-n findings; materiality member-declared.
6. **T4 append + tally**: verbatim appends; write order memos→appends→tally; git commit = round
   close (tally row is the transaction marker); integrity gate.
7. **T5 dispositions**: fixed | answered (provisional until raising member accepts) |
   open→gated (named owner); mixed findings decomposed (12a/12b); ratification queue;
   **propagation gate**: every `fixed` grep-verified against the current-truth corpus (variant
   forms enumerated; append-only history excluded from scope; interim status `fixing`).
8. **G6 terminal (HARD)**: full-roster votes, majority C/C, zero undispositioned material
   findings → close-out; else stall gate (2 rounds, zero VOTE-line movement AND zero new SP-n)
   → forced sponsor choice: kill (IC — Kill Decision) | park | new-evidence round.
9. **T7 close-out**: Marching Orders (+ dashboard iff monthly controllables); gates get
   owner + detection channel + watch mechanism; offer task-system export; fidelity gate
   (flip conditions quote-match member files); optional post-terminal self-review round scoped
   to the sponsor's new outward deliverables.
10. **T8 standing**: reconvene ONLY on a gate with 100% dated evidence — never on new documents.

## Gates

| Gate | Location | Verifies | Method | On failure |
|---|---|---|---|---|
| G1 state/deal integrity | entry | constellation complete, deal_id match, no in-flight lock | script | HALT + report |
| G2 append-only | resume | prior rounds byte-intact | script (git diff) | repair + dated note |
| G3 readiness | pre-Round-1 | numbers trace | agent | evidence pass / logged finding |
| G4 round commit | T4 | tally⟺headings, HEAD moved | script | repair pass, re-commit |
| G5 propagation | T5 | no stale copy in current-truth corpus | script (grep, variants) | back to T5 (`fixing`) |
| G6 terminal | post-T5 | majority + zero undispositioned material | script + human | loop / stall path |
| G7 stall | non-terminal | movement in 2 rounds | script | forced sponsor choice |
| G8 close-out fidelity | T7 | flip conditions verbatim | script (quote-match) | regenerate Marching Orders |
| G9 reconvene | standing | gate 100% evidenced | human + script | refuse, dated note |

## Edge Cases / Findings (Step 1-exit gap-probe, 4-agent fan-out — 47 findings, digest)

Full lists in the session record. Highest-severity, folded into this draft: partial-state
detection; deal-identity on resume; member-declared materiality (analyst conflict); doc-hash
manifest (silent drift); append-only as a checked invariant; propagation scope redefined to
current-truth docs (append-only history is legitimately un-scrubbed); majority defined for even
rosters + missing votes; kill trigger/authority/artifact (majority-Pass ×2 forces the choice);
`VOTE:` parseable line; `answered` provisional; split dispositions; write-order/commit
transaction; in-flight lock; memo naming + quorum; idempotent scaffold; gate-watch ownership +
reconvene mechanism; Marching-Orders task-export; ratification queue; consolidation step;
`ic_state` observability; prompt-injection posture for deal docs; confidentiality stub at
scaffold; global SP-n IDs.

## Terminal States

- **CONDITIONAL/COMMIT — standing**: Marching Orders issued (fidelity-verified); committee
  stands; reconvenes per G9.
- **KILLED — documented**: IC — Kill Decision written (reasons, final tally, member closing
  statements).
- **Parked**: dated note; committee stands; no Marching Orders.
- **HALT — integrity**: state unsafe to touch; sponsor decides.

## Diagram (Derived, Human-Readable)

Canonical source: `investment-committee.flowchart.mmd` beside this spec (validated:
25 nodes / 34 edges / all terminals reachable via `parse_mermaid.py`). Render fallback in this
environment: fenced Mermaid (no `mmdc`).

## Metrics Map / Review Cadence / Build Notes

**Deferred to Steps 4–7, pending the Step 2 Review hard gate.** Metrics sketched at anchor time:
output — terminal-reached rate, close-out fidelity pass rate, post-terminal error-catch count
(the "9 deck errors" class), **post_handoff_clarification_rate**; controllable input —
sponsor disposition latency per round, ratification-queue age; agent — member memo completion
per round, structured-output failure rate; health — rounds-to-terminal, cost per round,
stall-rule fires.

## Assumptions and Open Questions

- Step 0.2 (parse confirmation) bundled into the Step 2 Review gate — source is clean markdown
  authored this session; deviation logged here per gate mechanics.
- Whether the Input Dashboard demotes to optional (1A deletion proposal) — decided at Step 3.
- Whether the ~20-line hardening set becomes SKILL.md v0.8.1 edits vs. a referenced
  `references/hardening.md` — decided at Step 7 (build handoff).

## Verification Record

- Step 1-exit gap-probe mode: task_fanout — 4/4 agents returned valid severity-tagged lists
- Step 2 render mode: fenced-markdown fallback (no mmdc); parse-validated via parse_mermaid.py
- QA Agents pattern run on <PENDING — Step 6, post-gate>
- Phase 4 mode: task_fanout
- Phase 7 mode: <PENDING — Step 6>
- Path coverage: <PENDING>
- Issues resolved: <PENDING>
- Issues deferred to Assumptions: 3

## Change Log

- 2026-07-14: Created via `process-design` skill (Steps 0–2; hard gate pending)
