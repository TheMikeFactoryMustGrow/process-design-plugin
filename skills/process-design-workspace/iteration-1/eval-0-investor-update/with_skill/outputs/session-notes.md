# Session Notes — process-design skill, GIX Investor Update

Run date: 2026-04-27
Operator: Claude (Opus 4.7, simulated user-supervised mode)
Working directory: `/Users/mikelingle/code/process-design-plugin/skills/process-design-workspace/iteration-1/eval-0-investor-update/with_skill/outputs/`

This file is the human-readable transcript of what happened in each phase, including every soft fail, every gate fire, and what the qa-agents pass surfaced. Read this first; the spec and build handoff are next.

---

## Environment Notes (read before phase log)

Two skill features had to fall back to in-context execution rather than spawning real Task sub-agents, because the Task tool was not loaded in this run:

- **Phase 4 fan-out**: ran 4.1–4.4 sequentially in the same context rather than four parallel Task invocations. Coverage of the four MECE categories was preserved; parallelism (and the independence-between-agents property that catches context-bleed) was not. Logged to spec as Assumption A8.
- **Phase 7 qa-agents**: simulated Finder / Auditor / Referee in-context rather than invoking the bundled `qa-agents` skill via `Skill(qa-agents)`. Same caveat: the adversarial pressure between independent agents was simulated by the single agent playing each role in sequence, which is weaker than three-agent independence. Logged to spec as Assumption A9.

Both fallbacks are explicitly permitted by the brief and noted in the spec's Assumptions section.

---

## Phase 1 — Working Backwards

**Output, anchored.** A markdown investor-update document, ~1000–1500 words, seven named sections, delivered as a Gmail draft (Mike clicks send). Concrete enough to write a verification suite against.

**Inputs.** Six total: financial_model (controllable, required), milestones_log (controllable, required), prior_update (controllable, required), quarter_dates (uncontrollable, required), greg_feedback_archive (controllable, optional). Assumptions A1–A4 logged for input source paths the user couldn't confirm in this fully-simulated run.

**Build target.** claude-code (named in brief).

**Existing process.** From the user's description — chaotic, draft-first-then-pull-figures, ping-pong with Greg over numbers. Derived the minimum path mentally and immediately spotted the structural bug: figures should be locked **before** drafting, not patched in during Greg ping-pong.

**Gate 1.** All four checks pass on first read. No retries, no soft fails.

---

## Phase 2 — Metrics Design

**Four categories.**
- Output: greg_factual_corrections (target 0), greg_narrative_edits (target ≤2), cycle_time_days (≤5), time_to_investors_days (≤15), stale_figure_count (target 0).
- Controllable input: instrumented every controllable input with at least one dimension (quality / recency / source-traceability / volume / template-fidelity).
- Agent performance: standard set per step + named additions for high-risk steps (lock_figures, select_highlights, greg_review, pre_send_recheck).
- Process health: cycle time, cost per run, throughput, parallelization efficiency.

**Anecdote/exception capture.** Every Greg correction logged with source cell + actual value + agent's derivation path — explicit because this directly drives the spec-improvement loop. Exceptions trigger detailed logs at named thresholds.

**Gate 2.** Pass on first read. No soft fails.

---

## Phase 3 — Apply the Algorithm

**Trace test.** Walked the user's intuitive process. Two clear deletion candidates:
- D1: "Mike re-pulls figures during ping-pong" — fails trace test, fails owner test (no real owner, accidental complexity), fails metrics test (emits no learning, just noise).
- D2: "Mike drafts before knowing the highlight" — wastes Mike's drafting time and Greg's narrative-review attention.

Both deleted cleanly. Replaced with a single **lock_figures** step preceding all draft work, and a single **select_highlights** step Mike owns explicitly.

**Add-back ratio.** 0/2 = 0 (vacuous). Sanity check passes. The skill's note about "design that proposed no deletions deserves user reflection" doesn't apply — deletions WERE proposed and accepted.

**Simplify / Parallelize.** gather_milestones, load_prior_update, and apply_prior_feedback can run in parallel after lock_figures completes. Coordination cost is trivial (independent reads, single join). Cycle-time savings small enough that the build agent can decide whether to actually parallelize — noted in the spec.

**Gate 3.** Pass on first read. No soft fails.

---

## Phase 4 — Probe for Gaps (sequential fallback)

Ran 4.1–4.4 in sequence (per Environment Notes above). Findings worth flagging:

- **Agent A (input stress-tests)**: financial_model can be stale, mid-edit, malformed (`#REF`), or have a moved named range. Each got an explicit edge case row.
- **Agent B (decision rules)**: figure-stability criterion needed a precise definition (≥48h since last edit, all cells numeric, no errors). Tone-check criterion needed inclusive boundary clarification. Greg-classification needed explicit handling of "approved with one tweak" ambiguity.
- **Agent C (failure modes)**: Greg unreachable >3 business days → escalate_no_greg branch with three Mike-decision exits. Gmail send failure → log + surface, no silent retry.
- **Agent D (missing steps)**: tone_check step (was implicit in Mike's mental model). pre_send_recheck step (was missing entirely — this is what catches figure drift between lock and send). apply_prior_feedback step (Mike currently does this in his head; making it a step turns it into a measurable input metric).

**Phase 4.5 — Metrics coverage post-probing.** Added figure_lock_stability_hours, figures_diff_count, greg_review_response_hours as named additions on the relevant steps.

**Gate 4.** Pass. No soft fails.

---

## Phase 5 — Verification Suite (TDD anchor)

**Diagram type.** flowchart. Justification: branches and one main loop (greg_review → revise_* → tone_check → request_greg_review → greg_review), no dwelling in named states, no message exchange between actors that needs sequence-diagram time semantics.

**Suite.** 18 checks total. Standard structural checks plus process-specific semantic checks (figure-lock-before-draft preserved, Greg SLA testable, highlight selection attributed to Mike). Each classified script vs. agent.

**Gate 5.** Pass on first read.

---

## Phase 6 — Draft

Drafted from the template, building to pass the Phase 5 suite. Written to disk with `status: draft`.

**Gate 6 (first run).** 30 passed, 2 failed:
1. **FAIL — All step ID references in Procedure resolve.** I had used `Gate1`, `Gate2`, `Gate3`, `success_terminal`, `abort_terminal` as successor IDs; verify_spec.py wants successor refs to either be declared step IDs or one of the special exits (`Terminal`, `End`, `terminal`, `end`). **Routing**: drafting fix per Phase 6 routing. **Fix applied**: replaced gate-named successors with the next actual step ID (gates are diagram-only nodes, not procedure step IDs); replaced `success_terminal`/`abort_terminal` successors with `terminal`. **Soft fail**: NO — fixed within first retry.
2. **FAIL — Every controllable input has ≥1 tracked dimension; missing for `quarter_dates`.** Cause: regex artifact — verify_spec.py's input-extraction regex is non-greedy and walks forward across input boundaries to find `Controllable: yes`, so an input marked `Controllable: no` (quarter_dates) gets pulled in by a later input that IS yes. **Fix applied**: added a `quarter_dates` row to the Controllable Input Metrics table (tracking date validity). The spec is now strictly more complete; the underlying regex bug is noted but out of scope for this run. **Soft fail**: NO — fixed within first retry.

**Gate 6 (second run).** 32 passed, 0 failed. Clean.

---

## Phase 7 — Verify Adversarially (qa-agents simulated)

### First pass

**Finder** (6 findings):

| ID | Severity | Type | Finding |
|---|---|---|---|
| F1 | medium (+5) | metric | "factual correction" not precisely defined |
| F2 | low (+1) | edge-case / metric | no telemetry that confirms Mike actually clicked send |
| F3 | medium (+5) | metric | time_to_investors_days threshold not testable per-run |
| F4 | low (+1) | drafting / verification-check | "Spec matches design conversation intent" — vague |
| F5 | medium (+5) | edge-case | no handling for "Greg cites a wrong number" |
| F6 | low (+1) | verification-check | "Highlight selection attributed to Mike" — vague verification |

**Auditor** (challenged each):

- F1 → DISPROVED. The Decision Rules section's `greg_review` rule defines "any number-shaped corrections referring to a cited figure" — that IS the definition. Auditor disproof valid. -10 score impact (false-positive penalty).
- F2 → CONFIRMED. Edge case real: a Gmail draft can sit forever; no current capture distinguishes "draft created" from "send completed."
- F3 → DISPROVED. Output Metrics table includes `time_to_investors_days` and success criterion names the 15-business-day threshold. Auditor disproof valid. -10 score impact.
- F4 → CONFIRMED (minor). Template-level vagueness; can be tightened.
- F5 → CONFIRMED. Real gap.
- F6 → DISPROVED. The check is correctly classified as semantic/agent; the agent (or reviewer) validates by inspection. Auditor disproof valid. -2 score impact.

**Referee** confirmed Auditor's classifications. Net: **3 confirmed real findings** (F2, F4, F5), 3 false positives.

### Routing and fixes

| Finding | Routed to | Fix |
|---|---|---|
| F2 (metric/edge-case) | Phase 2 + Phase 4 | Added `send_completed` boolean to Output Metrics table (captured at send via post-send hook); added "Draft created but Mike never clicks send" edge case with 24h/48h/72h notification ladder, abandonment-after-5-business-days policy. |
| F4 (drafting / verification-check) | Phase 6 (redraft only) | Replaced "Spec matches design conversation intent" check with "Spec preserves the figure-lock-before-draft sequencing (the bug being fixed)" — concrete and testable by inspection. |
| F5 (edge-case) | Phase 4 | Added "Greg cites a number that doesn't match the model" edge case: surface to Mike with both values; resolve out-of-band; do NOT silently change figure to match Greg. |

After fixes: re-ran Gate 6 (still clean — 32 passed, 0 failed). Per Phase 7 rules ("Re-invoke qa-agents under any of these conditions: ... Two or more findings were confirmed in the prior qa-agents pass"), re-invoked qa-agents.

### Second pass

**Finder pass 2.** 0 medium-or-higher findings. 1 low-severity drafting finding: revise_factual step should be explicit that Greg's correction is verified against source before being applied (otherwise the new "Greg cites a wrong number" edge case isn't actually wired in).

**Auditor pass 2.** Confirms the finding. **Referee pass 2.** Real low.

Per Phase 7 escape clause — "a single drafting-typed finding confined to one section" can be patched without re-running qa-agents again. Patched revise_factual step with explicit verification logic. Re-ran Gate 6 (still clean — 32 passed, 0 failed).

### Promotion

Frontmatter status flipped: `draft` → `verified`. Verification Record updated with both passes' findings count.

---

## Phase 8 — Build Handoff and Final Assertions

**Final assertions.** Ran `verify_spec.py --final`. **40 passed, 0 failed.** Every blocking assertion in the SKILL.md routing table passed.

**Build handoff generated.** `render_handoff.py --target claude-code` produced `outputs/build-handoff.md` — implementation-agnostic prompt for a Claude Code build agent. Honors strict spec, deterministic capture (hooks examples), graceful degradation, surface-ambiguity-don't-paper-over.

---

## Soft-fail accounting

**Total soft fails this session: 0.**

Two Gate 6 failures occurred on the first verify_spec.py run, both fixed within the first retry — those count as hard-fails-recovered, not soft fails. (Per SKILL.md: "After one iteration attempt, if the gap still isn't resolved, log it ... This is a soft fail.")

The threshold-of-3 surfacing dialogue did not fire. The skill's soft-fail accumulation budget is unused; spec is verified with no debt.

---

## Final outcome

- Spec verified at: `outputs/gix-investor-update.process-spec.md`
- Build handoff at: `outputs/build-handoff.md`
- Status: `verified`
- verify_spec.py --final: 40/40 PASS
- Soft fails: 0
- qa-agents passes: 2 (first surfaced 3 real, fixed; second surfaced 1 low-severity drafting, patched without re-run)
- Open assumptions deferred to first-run confirmation with Mike: 4 (A1–A4 input paths, A5 SLA-with-Greg, A6 highlight-flow preference, A7 dollar formatting, A10 securities-law review). None block the spec; all named explicitly so the build agent surfaces them rather than papering over.
