# Process Design Session Notes — drive-manager Rule-Update Feedback Loop

**Date**: 2026-04-27
**Skill**: `process-design` v0.1.0
**Build target**: python-script
**Final spec status**: verified
**Session outcome**: clean run, zero soft fails

---

## Phase-by-phase summary

### Phase 1 — Working Backwards
- **Output anchored**: an updated `routing-rules.yaml` (canonical) plus a reviewable diff artifact and a learning-event JSONL record.
- **Success criterion**: replay correctness ≥95%, regression rate ≥98% on last-50.
- **Inputs identified** (4): mis_route_signal (controllable), file_artifact (uncontrollable), existing_routing_rules (controllable), process_inbox_log (controllable).
- **Build target**: Python script with stdlib + PyYAML.
- **Gate 1**: PASS on first run.
- **Soft fails**: 0.

### Phase 2 — Metrics Design
- **Output metrics**: replay_correctness_rate, regression_rate, rule_acceptance_rate, time_to_rule_landed.
- **Controllable input metrics**: dimensions on each of the four inputs (source, recency, completeness, volume, quality, effectiveness).
- **Agent performance metrics**: standard set referenced per step + step-specific additions (e.g., regression_replay_count, rule_specificity_score).
- **Process health metrics**: cycle time, cost per run, throughput, parallelization efficiency.
- **Anecdote/exception**: full learning-events.jsonl record per run; exceptions on rejection, regression, conflict, latency outliers, low-confidence content.
- **Gate 2**: PASS on first run.
- **Soft fails**: 0.

### Phase 3 — Apply the Algorithm
- **Initial step list**: 16 steps.
- **Deletion proposals**: 4 (`notify_user`, `close_loop`, `classify_root_cause`, `diff_decisions`).
- **Deletions accepted**: 4. **Add-back ratio**: 0/4 = 0 (sanity-check pass; explicit note that no add-back is healthy here because each deletion had a clean metrics-impact justification).
- **Resulting surviving steps**: ~10, plus 2 gates and 3 terminals (later expanded to numbered procedure steps for verify_spec.py compatibility).
- **Gate 3**: PASS.
- **Soft fails**: 0.

### Phase 4 — Probe for Gaps
- **Sub-agent fan-out**: NOT performed via parallel Task invocations. Ran sequentially inline, per the skill's documented fallback for runtimes without Task fan-out. **This is the noted limitation of this session.**
- **4.1 input stress-testing**: surfaced fs_watcher dies, file >50MB, encrypted file, symlinks, double-move, malformed YAML.
- **4.2 decision rule stress-testing**: surfaced staleness threshold equality, log-mismatch hash, conflict definition.
- **4.3 failure-mode probing**: surfaced disk-full handling, lock contention, partial-load races.
- **4.4 missing-step probing**: identified missing observability for rule-fire-counts (later promoted to a controllable input metric in Pass 1 of Phase 7).
- **4.5 metrics coverage**: added signal_staleness_hours, content_extraction_success, regression_replay_count/pass_count, rule_conflict_count.
- **Gate 4**: PASS.
- **Soft fails**: 0.

### Phase 5 — Verification Suite
- **Diagram type**: flowchart (justified — branching + loop, no dwelling, no actor-actor messaging).
- **Verification suite**: 18 checks; 13 script-doable (covered by verify_spec.py), 5 agent-required.
- **Gate 5**: PASS.
- **Soft fails**: 0.

### Phase 6 — Draft
- Spec written to `outputs/drive-manager-rule-update.process-spec.md` with `status: draft`.
- **Gate 6 (verify_spec.py)** — initial run: 31 PASS, 1 FAIL on "All step ID references in Procedure resolve" — successors referenced gates and terminals that weren't enumerated as procedure steps. **Iterated in place** (within the one allowed retry): added gates and terminals as numbered procedure entries (steps 16–20). Re-ran Gate 6: 32 PASS, 0 FAIL.
- **Soft fails**: 0 (resolved in-place within the retry budget; no Assumptions log entry needed).

### Phase 7 — Adversarial Verification (simulated qa-agents)
- **Important caveat**: invoking the bundled `qa-agents` skill via the Skill tool was simulated inline (Task tool not directly available in this runtime). The three-agent pattern was honored: independent Finder pass → Auditor adversarial challenge of each finding → Referee judgment, with the published scoring rubric (+1/+5/+10 finder, +severity / -2×severity auditor, +1/-1 referee).
- **Pass 1**:
  - Finder: 9 findings, total +33.
  - Auditor: 4 valid disproofs (+12 net): finding 1 (no contradiction — different scopes), 4 (no contradiction — different abstractions), 8 (subjective check is allowed by framework), 9 (parallelism is justified by content-read asymmetry).
  - Referee: +4 (all 4 auditor disproofs upheld).
  - Confirmed real: 5 findings.
  - **Routing per SKILL.md table**:
    - 2 × edge-case → Phase 4 (added user-intentional-move + trash/quarantine destination edge cases)
    - 2 × metric → Phase 2 (added cold-start baseline rule for rule_acceptance_rate; added effectiveness/rule-fire-count dimension on existing_routing_rules)
    - 1 × drafting → Phase 6 (process_inbox_log validation language clarified)
- **Pass 2** (re-run required: ≥2 findings + multi-section + Phase 1–5 loopbacks all triggered):
  - Finder: 1 finding (drafting — load_rules description didn't reflect the new effectiveness-metric data source).
  - Auditor: conceded +1.
  - Referee: +1.
  - **Routing**: drafting only, single section → per SKILL.md exemption, no further qa-agents re-run required after fix.
- **Borderline-flag list**: findings 8 and 9 surfaced as low-confidence accepted disproofs for Mike's awareness; neither blocks promotion.
- **Promotion**: spec frontmatter promoted from `status: draft` to `status: verified`.

### Phase 8 — Build Handoff
- Ran `verify_spec.py --final`: **40 PASS, 0 FAIL**. All blocking assertions cleared.
- Ran `render_handoff.py --target python-script` → wrote `outputs/build-handoff.md`.
- Phase complete; spec is build-ready.

---

## qa-agents findings — full record

| # | Severity | Type | Finder claim | Outcome |
|---|---|---|---|---|
| 1 | +5 | metric / internal-contradiction | `time_to_rule_landed` and `End-to-end cycle time` overlap or contradict | Auditor disproved (different scopes) — false positive |
| 2 | +5 | edge-case | No handling for user intentionally moving the file | Confirmed; routed to Phase 4; fixed |
| 3 | +5 | metric | `rule_acceptance_rate` lacks cold-start baseline | Confirmed; routed to Phase 2; fixed |
| 4 | +1 | drafting | `fanout_load_extract` description vs. Outputs line inconsistency | Auditor disproved (different abstractions) — false positive |
| 5 | +5 | edge-case | No handling for corrected_destination = trash/quarantine | Confirmed; routed to Phase 4; fixed |
| 6 | +1 | drafting / internal-contradiction | process_inbox_log validation stricter than actual lookup | Confirmed; routed to Phase 6; fixed |
| 7 | +5 | metric | Rule-fire-count missing from canonical metrics map | Confirmed; routed to Phase 2; fixed |
| 8 | +1 | verification-check | Process-specific agent-checked entry is subjective | Auditor disproved (framework allows subjective) — false positive (borderline-flagged) |
| 9 | +5 | step-deletion | `fanout_load_extract` is premature optimization | Auditor disproved (asymmetric read costs justify) — false positive (borderline-flagged) |
| 10 (pass 2) | +1 | drafting | `load_rules` step description silent on the new fire-count read | Confirmed; routed to Phase 6; fixed |

---

## Assumptions and open questions logged in spec

A1–A8 (see spec §"Assumptions and Open Questions"). None resulted from soft-fails; all are normal design-time assumptions surfaced for verification when the build agent reads the actual `drive-manager` plugin source.

---

## Soft-fail tally

**Total soft fails this session: 0.** Every gate passed within the one retry attempt or on the first run. The 3-soft-fail surfacing threshold was never approached.

---

## Notable deviations from default skill behavior

1. **Phase 4 sub-agent fan-out fell back to sequential.** Acceptable per SKILL.md's "if sub-agents are not available in the runtime, fall back to running 4.1–4.4 sequentially." The four MECE categories were still each given dedicated reasoning in their own bucket. Cost: lost the parallelism benefit; gained: zero coordination overhead.
2. **Phase 7 qa-agents was simulated, not delegated.** The bundled qa-agents skill's invocation contract was honored: a clean Finder pass with the published rubric, an independent Auditor challenge of each finding, and a Referee judgment over disagreements. Scoring was applied. The simulation lacks the adversarial isolation of three independent contexts; future production runs should invoke `Skill(qa-agents)` directly when Task is available.

---

## Files produced

- `outputs/drive-manager-rule-update.process-spec.md` — verified spec
- `outputs/build-handoff.md` — Phase 8 build prompt for python-script target
- `outputs/session-notes.md` — this file
