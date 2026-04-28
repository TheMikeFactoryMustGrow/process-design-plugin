# Process Design Session Notes — Weekly Review (iteration-2)

**Date**: 2026-04-27
**Skill**: `process-design` (with-skill arm of eval-1, iteration-2)
**Process slug**: `weekly-review`
**Build target**: `claude-code`
**Final status**: `verified` (Gate 6 32/0 first run with one hard-fail-fix retry; final --final 40/0)

---

## Phase outcomes

| Phase | Outcome | Mode | Notes |
|---|---|---|---|
| Phase 1 — Working Backwards | PASS | n/a | Output, success criterion, failure modes, six controllable + 1 non-controllable inputs, build target = claude-code |
| Phase 2 — Metrics Design | PASS | n/a | All 4 categories filled; 12 controllable input dimensions; per-step performance set + 5 step-specific additions |
| Phase 3 — Apply the Algorithm | PASS | n/a | Naive 12+ steps reduced to 7; deletion candidates: notify, format-output, separate-write, redundant-validation. Add-back ratio 0/4 = 0% |
| Phase 4 — Probe for Gaps | PASS | **inline_simulation** | Task tool unavailable in runtime (only TaskStop loadable). Sub-types 4.1-4.4 run sequentially in same context. 4.5 metrics-coverage integration with reduced confidence. |
| Phase 5 — Verification Suite | PASS | n/a | Diagram type = flowchart with explicit reasoning; 22 verification checks (15 structural script + 7 semantic agent), 3 process-specific |
| Gate 6 — verify_spec.py (first run) | 31/1 → fix → 32/0 | n/a | Hard fail on step-ID resolution (terminal.* and gate.* in Procedure successors). Fixed by referencing terminal states via the script's well-known token `Terminal` and rephrasing gate-as-successor edges. Not a soft fail. |
| Phase 7 — Adversarial QA | PASS | **inline_simulation** | qa-agents Skill loaded but Task subagent capability missing; simulated finder/auditor/referee inline. Run #1: 11 findings (F1-F11) → 7 confirmed (3 edge-case, 2 metric, 1 verification-check, 1 internal-contradiction). Run #2 post-fix: 1 new finding F12, disproved. Clean. |
| Phase 8 — Build Handoff | PASS | n/a | render_handoff.py produced build-handoff.md targeting claude-code. verify_spec.py --final 40/0. |

---

## Soft-fail count

**Total soft fails this session: 0.**

Gate 6 had one hard fail on first run (step-ID resolution for terminal.* / gate.* successors) which was fixed within one retry — by spec convention this is a hard-fail-fixed, not a soft fail. The 9 items in the spec's Assumptions and Open Questions (A1-A9) are design-time deferrals or runtime-environment notes (A8 documents the Phase 4 fallback), none are gate soft fails.

The soft-fail surfacing threshold of 4 was never approached.

---

## Phase 4 mode

**`inline_simulation`** — Task tool unavailable in this runtime (only TaskStop was loadable via ToolSearch; no Task launcher tool surfaced). Per process-design SKILL.md Phase 4 fallback ("If sub-agents are not available in the runtime, fall back to running 4.1–4.4 sequentially in this same conversation"), the four MECE probes were run sequentially in the same context. Adversarial isolation between sub-types is partial; treat 4.5 integration as lower-confidence than a true fan-out pass. Reflected in spec Verification Record.

Notable additions surfaced by sequential probing:
- 4.1 (input stress-test): added quarterly_priorities.staleness_days metric; added overflow handling for >100 TODOs; added quarterly priorities updated mid-week edge case.
- 4.2 (decision rule stress-test): added boundary tie-break rules to DR1 (≥0.78 = match), DR2 (=14d = NOT stuck), DR3, DR5.
- 4.3 (failure-mode probing): per-step degraded-mode behavior; partial commitment classification; bounded ratify cycle.
- 4.4 (missing-step probing): kill/defer disposition in stuck_list; subjective rationalization cross-check (DR4); per-todo history store for re-titled-TODO continuity.
- 4.5 (metrics coverage): added rationalization_flag, candidates_considered, trigger_type_distribution, rejection_count.

---

## Phase 7 mode

**`inline_simulation`** — qa-agents skill *was* reachable via Skill tool and its operating manual loaded, but the skill's core mechanism is three isolated Task subagents. Since the Task launcher is unavailable in this runtime, qa-agents itself could not actually fan-out the three roles. Per process-design SKILL.md Phase 7 fallback, finder/auditor/referee were simulated inline by this same agent using the document rubric (no `process-spec` rubric exists in qa-agents references). Reflected in spec Verification Record with the required simulation note.

### Run #1 — initial verification (inline simulation)
- **Finder**: 11 findings, total severity +47 (1×L+10×severity 5 = 47 across 11 = mix of 1s and 5s; concretely: 8×5 + 3×1 = 43... let me recount. Actually: F1-F5 each 5, F6 1, F7 5, F8 5, F9 1, F10 5, F11 1 = 5×7 + 1×4 wait: F1=5, F2=5, F3=5, F4=5, F5=5, F6=1, F7=5, F8=5, F9=1, F10=5, F11=1 = 5×8 + 1×3 = 43.)

Correction: total severity +43 across 11 findings.

- **Auditor**: 4 disproves attempted (F5 conf 7, F6 conf 6, F9 conf 8, F11 conf 5). All 4 disproves valid per Referee → Auditor +12 net (5+1+1+1 = +8 actually — F5 was severity 5, F6 severity 1, F9 severity 1, F11 severity 1, so +5+1+1+1 = +8). Zero false disproofs.
- **Weakest accepted**: F3 (partial-commitment counting in commitments_kept_pct), F8 (under-3-priorities ledger redundancy with Inputs validation).
- **Referee**: 4 disprove rulings + 2 weak-flag rulings. F3 weak-flag → WEAK (concern fair, fix needed in metric definition). F8 weak-flag → WEAK initially, but per fix decision the ledger row is added. All 4 disprove rulings UPHOLD-DISPROOF. Referee +6 net.
- **Confirmed real findings**: F1, F2, F3, F4, F7, F8, F10 (7).
- **Routing per Phase 7 table**:
  - F1, F4, F8 → Phase 4 (edge-case) — added 3 rows to Edge Cases ledger (prior_review unparseable, re-run resume mode, quarterly_priorities under-specified)
  - F2 → Phase 1 + Phase 6 (internal-contradiction) — fixed DR2 by removing the multi-prior-review condition that no input pulls
  - F3 → Phase 2 (metric) — clarified `commitments_kept_pct` partial counting (partial = 0.5)
  - F7 → Phase 2 (metric) — clarified Streak metric (degraded_filed counts; abandoned breaks)
  - F10 → Phase 5 (verification-check) — re-worded "decision rules resolve on input alone or escalate to named evaluator"

### Run #2 — post-fix re-validation (per SKILL.md re-invoke conditions: 7 fixes touching 4 phases)
- **Finder**: 1 new low-severity nit (F12: "under-3-priorities" edge case row duplicates Inputs-section validation rule).
- **Auditor**: DISPROVE F12 (conf 8) — the duplication is intentional. Edge Cases ledger is the canonical user-readable enumeration; per-input validation rule is the per-input operational rule; both should name the case.
- **Referee**: UPHOLD-DISPROOF.
- **Net**: clean. No further re-routes. Spec promoted to `status: verified`.

### Adversarial confidence note
Inline-simulated findings are structurally weaker than three real isolated subagents because the same agent that drafted the spec also did the finding/auditing/refereeing. The 4 disproves I found were "good catches" — but a fresh-context Auditor might have surfaced different concerns I anchored away from. Worth re-running Phase 7 against this verified spec from a runtime with subagent capability before treating it as production-grade. Reflected in the spec's Verification Record simulation note.

---

## qa-agents findings summary (run #1 + run #2)

| ID | Type | Severity | Disposition | Loop-back |
|---|---|---|---|---|
| F1 | edge-case | +5 | confirmed | Phase 4 |
| F2 | internal-contradiction | +5 | confirmed | Phase 1 + 6 (DR2 wording) |
| F3 | metric | +5 | confirmed (weak-flag → WEAK) | Phase 2 |
| F4 | edge-case | +5 | confirmed | Phase 4 |
| F5 | drafting | +5 | disproved (Auditor +5) | none |
| F6 | drafting | +1 | disproved (Auditor +1) | none |
| F7 | metric | +5 | confirmed | Phase 2 |
| F8 | edge-case | +5 | confirmed (weak-flag → WEAK initially, fix added anyway) | Phase 4 |
| F9 | drafting | +1 | disproved (Auditor +1) | none |
| F10 | verification-check | +5 | confirmed | Phase 5 |
| F11 | drafting | +1 | disproved (Auditor +1) | none |
| F12 (run 2) | drafting | +1 | disproved | none |

**Score line**: Finder 43 + 1 = 44 across both runs; Auditor +8 + +1 = +9 net; Referee +6 + +1 = +7 net.

---

## Final verify_spec.py result

**`verify_spec.py --final`: 40 passed, 0 failed.** All blocking assertions for Phase 8 promotion satisfied.

`verify_spec.py` (Gate 6, non-final): also clean at 32/0 on the final spec text.

---

## Skill-improvement notes (telemetry-style)

1. **Phase 4 / Phase 7 fallback exercised**: this session ran both fallbacks. The qa-agents skill's outer Skill-tool surface IS reachable, but its inner Task-subagent mechanism is the load-bearing one — the skill is effectively non-functional without Task. Worth marking this in qa-agents' SKILL.md as a hard prerequisite check before phase 1 (and refusing to proceed in inline mode at all, perhaps, since the inline simulation is structurally weaker).

2. **Iter-1's `verify_spec.py` controllable-input regex bug appears fixed in iter-2**: my Inputs section places the non-controllable `calendar` last (matching iter-1's workaround) but I also wrote it that way to preserve the natural ordering, not to dodge the bug. With the per-input grouping in `_parse_inputs`, the script correctly attributed `Controllable: no` to calendar even when adjacent. Confirmed clean.

3. **Step-ID-in-successors fix is the same hard-fail iter-1 hit**: the script's allowlist of well-known terminal tokens (`Terminal`, `End`, `terminal`, `end`) is restrictive — it forces spec authors to either use those exact tokens OR declare terminal states as procedure steps. The `Terminal (terminal.foo)` workaround keeps the human-readable terminal ID visible while satisfying the script. This is a minor friction; could be eased by extending the regex to accept any `terminal.*` or `end.*` ID.

4. **No process-spec rubric in qa-agents**: the bundled rubrics.md is rich but doesn't have a process-spec rubric. The closest fit is "document". A process-spec rubric would distinguish drafting-only nits from semantic-design defects, edge-case gaps, metric-vanity, and unmotivated-step issues — close to the `finding type` taxonomy in process-design SKILL.md Phase 7.

5. **Inline qa-agents simulation produced fewer findings than iter-1**: 11 vs. iter-1's 12 in run #1 (by the count visible in iter-1 session-notes). Comparable order of magnitude. The single-agent context limitation likely caps the variety of "lenses" applied — a real fan-out would surface findings I anchored away from.

---

## Files produced

- `/Users/mikelingle/code/process-design-plugin/skills/process-design-workspace/iteration-2/eval-1-weekly-review/with_skill/outputs/weekly-review.process-spec.md` — verified spec (status: verified)
- `/Users/mikelingle/code/process-design-plugin/skills/process-design-workspace/iteration-2/eval-1-weekly-review/with_skill/outputs/build-handoff.md` — Phase 8 handoff prompt for Claude Code
- `/Users/mikelingle/code/process-design-plugin/skills/process-design-workspace/iteration-2/eval-1-weekly-review/with_skill/outputs/session-notes.md` — this file
