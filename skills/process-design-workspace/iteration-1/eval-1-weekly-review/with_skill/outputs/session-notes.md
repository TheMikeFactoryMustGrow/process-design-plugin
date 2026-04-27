# Process Design Session Notes — Weekly Review

**Date**: 2026-04-27
**Skill**: `process-design` (with-skill arm of eval-1)
**Process slug**: `weekly-review`
**Build target**: `claude-code` (manual-with-agent-supported-drafting)
**Final status**: `verified` (Gate 6 32/0, Phase 8 final 40/0)

---

## Phase-by-phase

### Phase 1 — Working Backwards
- **Output**: `weekly-review-YYYY-Www.md` markdown artifact with four sections (Shipped, Stuck, Drift Signals, Next-Week Focus) plus metadata.
- **Success criterion**: produced ≤45 min (cap 75), every prior commitment resolved, 3-5 next-week commitments with leading indicators, drift signals trigger-backed (not vibes).
- **Inputs**: completed_items, todos, prior_review, quarterly_priorities, subjective_state, calendar (the only non-controllable; placed last in the Inputs list to avoid the lazy-match bug in `verify_spec.py`'s controllable-input check — see Gate 6 soft-fail #1 below).
- **Build target rationale**: Claude Code skill (manual-with-agent-supported-drafting). Pure script would lose the judgment (what's drift, what should next week's focus be). Pure manual would lose the consistency. Hybrid is correct.
- **Gate 1**: PASS (no soft fails).

### Phase 2 — Metrics Design
- **Output metrics**: review_completed, commitments_carried_forward_pct, commitments_partial_count, drift_signals_flagged_count, next_week_focus_count, review_cycle_time_min.
- **Controllable input metrics**: dimensions for completed_items, todos, prior_review, quarterly_priorities, subjective_state.
- **Agent performance**: standard set per step + step-specific additions (probe.drift.candidates_considered, score.commitments.match_method, ratify.and.write.edits_count).
- **Process health**: cycle time, cost, throughput, parallelization efficiency.
- **Anecdote/exception**: weekly artifacts are the anecdote corpus; exception triggers on cycle>75min, zero carry-forward, drift>5, week-skipped, ratify edits>20.
- **Gate 2**: PASS.

### Phase 3 — Apply the Algorithm
Initial intuitive list: 15 steps. After question/delete/simplify:
- D1: deleted "notify" (Mike is the executor).
- D2: deleted "write.artifact" as standalone (folded into ratify.and.write).
- Simplification: merged 4 draft.* steps into single draft.review.
- **Add-back ratio**: 0/2 = 0% (well under 30% ceiling).
- Final 7 steps: gather.inputs (parallel) → score.commitments → identify.stuck → ask.subjective → probe.drift → draft.review → ratify.and.write.
- **Gate 3**: PASS.

### Phase 4 — Probe for Gaps (sequential simulation, Task tool unavailable)
**Fallback note**: SKILL.md prescribes parallel `Task` invocations for the four MECE sub-agents. The Task tool was not reachable in this runtime. Per SKILL.md Phase 4 fallback guidance ("If sub-agents are not available in the runtime, fall back to running 4.1–4.4 sequentially in this same conversation"), the four probes were run sequentially in the same context. This is a documented fallback, not a defect — but it may have allowed context-bleed between probes; logged as A8 in the spec's Assumptions and Open Questions.

Notable additions from the probes:
- 4.1 (input stress-test): added quarterly_priorities.staleness_days metric; added overflow handling for >100 TODOs; added subjective rationalization cross-check.
- 4.2 (decision rule stress-test): added "tie goes to not flagged" tie-breaking on DR2 boundary thresholds; added "exactly 14 days = not stuck" tie on DR3.
- 4.3 (failure-mode probing): per-step degraded behavior named; partial commitment bucketing.
- 4.4 (missing-step probing): added kill/defer mechanism in ratify; surfaced quarterly priorities as a separate dependency.
- 4.5 (metrics coverage): added commitments_partial_count and quarterly_priorities.staleness_days.
- **Gate 4**: PASS.

### Phase 5 — Verification Suite
- **Diagram type**: flowchart (procedure with branches and degraded-mode paths, no dwelling states, no multi-actor messaging). Reasoning explicit.
- **Process-specific checks added**: every step's degraded-mode behavior named; ≥3 numeric thresholds explicitly stated in DR2; output metric computability from inputs alone.
- **Gate 5**: PASS.

### Phase 6 — Draft + Gate 6
- Draft written to disk with `status: draft`.
- **Gate 6 first run**: 30 PASS / 2 FAIL.
  - FAIL #1: `terminal.abandoned`/`terminal.shipped` flagged as unresolved successor IDs. Fix: changed successor refs in step 7 to `End` (script accepts `End`, `Terminal`, `terminal`, `end` as well-known terminals); kept the diagram stadium nodes. (Hard fail → fix → re-run, not a soft fail.)
  - FAIL #2: `calendar` flagged as a controllable input with no tracked dimension, despite being marked `Controllable: no`. Root cause: the regex in `verify_spec.py` is lazy-matched and finds the *next* `Controllable: yes` line in the *next* input. Fix on the spec side: moved `calendar` to the bottom of the Inputs list so no later `Controllable: yes` line exists. (Hard fail → fix → re-run.) **This is a script defect that warrants a bug filed against verify_spec.py — the spec author shouldn't have to reorder inputs to dodge a regex flaw.**
- **Gate 6 re-run**: 32 PASS / 0 FAIL. Pass.
- **No soft fails** in Gate 6.

### Phase 7 — Adversarial QA (qa-agents simulation, Task tool unavailable)
**Fallback note**: qa-agents requires Task subagents. Per SKILL.md ("If qa-agents isn't reachable, simulate the three-agent pattern with Task agents per the scoring rubric in SKILL.md"), the three-agent pattern was simulated inline using the qa-agents scoring rubric (+1/+5/+10 for Finder, ±2× for Auditor disproofs, ±1 for Referee).

#### Run #1 — initial verification
- **Finder**: 12 findings, total severity 49.
- **Auditor**: 4 valid disproofs (F3, F8, F9, F11) → +8 net. Zero false disproofs.
- **Referee**: 12 correct judgments → +12 net.
- **Confirmed real findings**: F1 (DR1 fuzzy threshold opaque), F2 (DR2 "tracked hours" undefined), F4 (TODO-rewrite history store unspecified), F5 (Gate 2 retry not bounded — downgraded by Auditor from unbounded-loop to edge-case after re-checking the structural layer; Gate 6 had not actually escaped), F6 (todos contradiction: `Required: yes` vs. degraded-mode skip), F7 (DR4 degraded-mode + Next-Week Focus 3-5 composition), F10 (verification-check misclassified semantic vs. structural), F12 (cycle-time wallclock during human wait undefined).
- **Routing per Phase 7 table**:
  - F1, F2 → Phase 6 re-draft (drafting)
  - F4, F5, F7, F12 → Phase 4 (edge-case re-spec)
  - F6 → Phase 1 (input definition contradiction)
  - F10 → Phase 5 (verification-check reclassification)
- **Fixes applied to spec**:
  - DR1: named the embedding model and threshold convention; allowed build-agent override with required record.
  - DR2: defined `tracked_hours_for_thread()` formula explicitly with calendar+completed_items composition and a degraded-fallback rule.
  - Edge case "TODO secretly rewritten": specified per-TODO history store at `$WEEKLY_REVIEW_LOG_DIR/todo-history.jsonl`.
  - Gate g.draft_ratifiable: bounded retry to exactly 1, with `incomplete_draft=true` flag escape; diagram updated with explicit retry counter edges.
  - todos input: changed from `Required: yes` to `Required: no` with explicit note linking to F6.
  - DR4: degraded-mode source priority chain for Next-Week Focus items (4 fallback sources).
  - Edge cases: added explicit "Mike walks away mid-ask.subjective" handling (20-min auto-fill); cycle-time exception clarified to use orchestrator wallclock independent of agent activity.
  - Verification Suite: F10 reclassified as structural (script-extension-doable).

#### Run #2 — post-fix re-validation (per SKILL.md re-invoke conditions: 8 fixes touching 5 phases)
- **Finder**: 1 new low-severity nit (F13: `.draft.md` filename collision between abandoned and timeout terminal cases).
- **Auditor**: disproved F13 — the cases are mutually exclusive states; reusing the path is intentional for resume behavior.
- **Referee**: +1 (correct disprove).
- **Net**: clean. No further re-routes.

### Phase 7 → Promotion
- All real gaps fixed in spec text and diagram.
- No soft-failed gaps correspond to Phase 8 blocking assertions (the 8 deferred items in Assumptions are all open-question or scope items, not blocking-assertion gaps).
- Spec promoted: `status: draft` → `status: verified`.

### Phase 8 — Build Handoff
- **Final assertions** (`verify_spec.py --final`): 40/0 PASS. All blocking assertions satisfied.
- **Handoff** rendered via `render_handoff.py --target claude-code` and saved to `outputs/build-handoff.md`. Capture mechanism examples named: hooks (`PreToolUse`, `PostToolUse`, `Stop`), MCP servers, structured tool result parsing.

---

## Soft-fail accounting

**Total soft fails this session: 0.**

All gate failures during Gate 6 were hard fails fixed within one retry (the script-side bug-dodge for calendar input ordering, and the terminal-ID resolution). No fail logged as an open question.

The 8 items in the spec's Assumptions and Open Questions (A1–A8) are:
- A1–A2: design-time assumptions about user intent
- A3: parameter starting values flagged for Metrics Review evolution
- A4: scoping assumption about the runtime
- A5–A7: open questions deferred to v2
- A8: documented Phase 4 sub-agent fallback (not a soft fail; a runtime-environment note)

None of these are gate soft fails, so the soft-fail counter never approached the 4-fail surfacing threshold.

---

## qa-agents findings summary

| ID | Type | Severity | Disposition | Loop-back |
|---|---|---|---|---|
| F1 | drafting | +5 | confirmed | Phase 6 |
| F2 | drafting | +5 | confirmed | Phase 6 |
| F3 | metric | +5 | disproved (Auditor +5) | none |
| F4 | edge-case | +5 | confirmed | Phase 4 |
| F5 | edge-case (was unbounded-loop) | +5 (downgraded) | confirmed | Phase 4 |
| F6 | internal-contradiction | +5 | confirmed | Phase 1 |
| F7 | edge-case | +5 | confirmed | Phase 4 |
| F8 | drafting | +1 | disproved (Auditor +1) | none |
| F9 | drafting | +1 | disproved (Auditor +1) | none |
| F10 | verification-check | +1 | confirmed | Phase 5 |
| F11 | drafting | +1 | disproved (Auditor +1) | none |
| F12 | edge-case | +5 | confirmed | Phase 4 |
| F13 (run 2) | drafting | +1 | disproved | none |

**Score line**: Finder 49 + 1 = 50 across both runs; Auditor net +8 + +1 = +9; Referee net +12 + +1 = +13.

---

## Skill-improvement notes (telemetry-style)

1. **`verify_spec.py` controllable-input regex bug**: lazy-match `[\s\S]*?Controllable:\s*yes` finds the wrong input's controllable flag. Spec authors should not have to reorder inputs to satisfy the script. Suggested fix: anchor the search to a per-input substring (between consecutive `^- \*\*` lines) and restrict the lookup to that substring. Filed as a skill-improvement candidate; the workaround in this spec is a comment in the Inputs section explaining the ordering.

2. **Phase 4 fallback exercised**: this session ran the sequential fallback. Worth comparing parallel-Task fan-out vs. sequential output on a controlled run to confirm the fallback surfaces equivalent gaps (i.e., that context-bleed isn't actually weakening the probe).

3. **qa-agents simulation**: the inline simulation followed the scoring rubric, but the adversarial-isolation premise of qa-agents (independent contexts) collapses without subagents. Findings here may underrepresent issues a fresh-context Auditor would surface (because the same agent that drafted F1–F12 also disproved them). Treat the run-2 clean result with appropriate caution; a real-Task qa-agents pass would be stronger evidence.

4. **No soft fails**: the spec was rich enough at Phase 5 that no Gate 6 check needed soft-fail logging. This is the desired outcome but worth tracking — if many sessions soft-fail nothing, the Gate 6 checks may be too easy or the threshold of 3 is too lenient.

---

## Files produced

- `/Users/mikelingle/code/process-design-plugin/skills/process-design-workspace/iteration-1/eval-1-weekly-review/with_skill/outputs/weekly-review.process-spec.md` — verified spec
- `/Users/mikelingle/code/process-design-plugin/skills/process-design-workspace/iteration-1/eval-1-weekly-review/with_skill/outputs/build-handoff.md` — Phase 8 handoff prompt for Claude Code
- `/Users/mikelingle/code/process-design-plugin/skills/process-design-workspace/iteration-1/eval-1-weekly-review/with_skill/outputs/session-notes.md` — this file
