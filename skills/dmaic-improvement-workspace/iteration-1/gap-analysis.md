# Gap Analysis — Verified Spec vs. Current dmaic SKILL.md

**Comparing:**
- **Verified spec** at `iteration-1/dmaic-orchestrator.process-spec.md` (produced this session via `process-design`)
- **Current implementation** at `~/code/process-design-plugin/skills/dmaic/SKILL.md` (242 lines)

For each gap: what side it's on, which of Mike's four goals it addresses (G1 = minimize tokens, G2 = MECE parallelism, G3 = scripts over agents, G4 = controllable-vs-external metrics with causal chains), and whether the gap should drive an iter-1 fix or be deferred.

---

## A. In the verified spec but missing from current dmaic

### A1. **Explicit External Input Metrics category** (G4 — headline)
The spec adds a fifth metric category — External Input Metrics — alongside Output, Controllable Input, Agent Performance, and Process Health. Current dmaic has no such concept. It talks about "terminal metrics" (which conflates output) and reaches for inputs in Analyze without distinguishing controllable from uncontrollable.
**Why it matters:** without this, a reader of a current dmaic spec cannot answer "if I want to move output X, which input do I move?" — they have to infer which named cause is actually a lever vs. a context factor.
**Recommended fix in iter-1:** add the External Input Metrics category to the Linglepedia `_schemas/dmaic-spec.md` schema (separate vault PR), then add it to the per-phase Measure block guidance in the redesigned SKILL.md.

### A2. **Causal-chain block in Analyze with script enforcement** (G4 — headline)
The spec mandates that for every output metric, the Analyze block names ≥1 controllable input that moves it. A new `dmaic.py check-causal-chain` subcommand enforces `causal_chain_completeness == 1.0` at gate g4_causal_chain. Current dmaic has nothing like this — it lists "known failure modes" qualitatively but doesn't force the metric→input mapping.
**Why it matters:** this is the difference between "we know what could go wrong" (current) and "we know which lever moves which output" (target).
**Recommended fix in iter-1:** implement `dmaic.py check-causal-chain` and add the gate to the orchestrator. **This is the single most impactful change.**

### A3. **MECE parallel fan-out in Measure and Analyze** (G2)
The spec specifies that per-metric work in s2_measure and s3_analyze (and per-experiment work in s4_improve) fans out via Task subagents when available, with sequential fallback. Current dmaic walks D→M→A→I→C strictly sequentially, and within Measure/Analyze, walks each metric one at a time.
**Why it matters:** for a 3-metric Measure phase, parallel fan-out is a 3x latency win — important when the orchestrator runs in interactive sessions.
**Recommended fix in iter-1:** add the fan-out instruction to the redesigned SKILL.md and a `parallel_fanout_used` telemetry dimension. The actual Task-tool dispatch is mechanical.

### A4. **Owner-is-a-department denylist** (G3-ish — script enforces)
The spec requires owner validation against a small denylist of department-shaped names ("the team", "operations", etc.) and rejects them unless the user explicitly opts in. Current dmaic accepts any string for owner.
**Why it matters:** Elon's algorithm — departments can't be held accountable, people can. A "the team" owner means no one is accountable.
**Recommended fix in iter-1:** small denylist as a `dmaic.py validate-owner` script call OR inline in the orchestrator. Trivial.

### A5. **No-silent-overwrite rule for spec output** (G3 — script enforces)
The spec mandates that if a file with the same slug already exists at the resolved output path, the orchestrator surfaces the conflict and offers (a) resume, (b) suffix, (c) different path. Current dmaic doesn't address this — silently overwriting is the implicit behavior.
**Recommended fix in iter-1:** add the check to `dmaic.py compose` (existing subcommand can grow a `--no-overwrite` default).

### A6. **Mid-session checkpoint** (G3 — script enforces)
The spec mandates partial-block checkpointing to `/tmp/<slug>-spec.json.partial` after each phase, with resume on next invocation. Current dmaic loses everything on session abandonment.
**Recommended fix in iter-1:** small. The checkpoint file format is just the dict the script already accepts.

### A7. **Telemetry section** (G3)
The spec specifies a telemetry section with default location, event taxonomy, and graceful degradation rule. Current dmaic has zero telemetry — it can't be improved with data because it doesn't generate any.
**Recommended fix in iter-1:** new `dmaic.py log-event` subcommand; orchestrator calls it per phase. Without this, there's no way to feed iter-2 with empirical evidence.

### A8. **`iterate` vs. `fresh` mode fork** (mode discovery)
The spec mandates an explicit `existing_spec_path` input that gates iterate vs. fresh mode. Current dmaic only mentions "validate any spec, anytime" — there's no integrated path for "re-DMAIC this prior spec."
**Recommended fix in iter-1:** orchestrator-level routing; minor.

### A9. **Verification suite as pre-conditions** (TDD principle, missing in current)
The spec defines what makes a finished `dmaic-spec` complete BEFORE drafting it. Current dmaic relies on `dmaic.py validate` post-hoc. The TDD framing is healthier — the writer aims at a known target.
**Recommended fix in iter-2:** the redesigned SKILL.md should explicitly state the verification suite as a Phase 0 step, mirroring `process-design`'s Phase 5.

### A10. **Recursive metrics review plan that calls dmaic on itself** (closes the loop)
The spec's Metrics Review Plan calls for running `Skill(dmaic)` recursively against the dmaic orchestrator's own telemetry — this closes the improvement loop and is the mechanism by which iter-2, iter-3 land. Current dmaic has principles 5–7 ("evolve the framework") as prose, not as a mechanism.

---

## B. In current dmaic but missing from (or excised by) the verified spec

### B1. **The two-ways-to-run-the-phases explanation** (lines 47-52 of current)
Current dmaic explains both "invoke per-phase sub-skills" and "apply rules inline" as user-facing concepts. The spec collapses this into a single decision rule (phase_invocation_mode) the orchestrator handles internally.
**Verdict:** EXCESS in current. The user shouldn't have to know about it. Hiding it in the orchestrator is a G1 win.

### B2. **The inline JSON example for spec.json** (lines 139-153 of current)
Current dmaic shows the full spec.json shape inline. The spec deletes this in favor of a `dmaic.py compose --from-stdin` mode (new) where the agent emits structured markdown blocks separated by sentinels.
**Verdict:** EXCESS in current — but the deletion is conditional on the new script subcommand existing. Build pass must implement `--from-stdin` first or the deletion creates a usability gap.

### B3. **The "Principles" section** (lines 233-241 of current)
Duplicates `references/dmaic-reference.md`. Spec deletes from SKILL.md; reference is still loaded.
**Verdict:** EXCESS in current. G1 win.

### B4. **The `Vault-aware behavior` section** (lines 200-210 of current)
Mostly duplicates what `dmaic.py detect-vault` returns. Spec trims to one sentence: "the orchestrator runs `dmaic.py kickoff` which handles vault detection AND capability probing in one call."
**Verdict:** EXCESS in current. G1 + G3 win.

### B5. **The "Stuck?" coaching prose throughout the per-phase summaries** (current ~30 lines)
Current dmaic has rich coaching text ("The most common Define failure is fuzziness…" etc.). The spec moves this to a new `references/dmaic-coaching.md` to be loaded only when needed.
**Verdict:** STRENGTH in current that the spec moves rather than deletes. The coaching is valuable; the placement is wasteful (it loads on every invocation). G1 win.

### B6. **Mike's principles 1–7 from `[[DMAIC]]`** (lines 233-241 of current)
The current SKILL.md restates them. The spec relies on the reference file being read as part of "Before You Start."
**Verdict:** EXCESS duplication. G1 win, but watch: if the reference doesn't get read in practice, removing the inline copy is a regression.

### B7. **The "When to use this skill" trigger phrasing** (lines 14-26 of current)
Heavy overlap with the description in frontmatter. The spec keeps it tight (the description in the new SKILL.md frontmatter still drives Claude's skill matcher).
**Verdict:** EXCESS in current — but it's load-bearing for skill-matcher accuracy. Trim cautiously, don't delete.

### B8. **The "Don't proceed until you have a subject" warning prose** (line 41 of current)
Current dmaic has this as prose. Spec encodes it as g1_kickoff with a script check.
**Verdict:** Code over prose. G3 win.

### B9. **The principles cross-cut throughout phase prose** (e.g., "Failed experiments are data, not waste" inline in Phase 4)
Repeated in multiple places. Spec relies on `dmaic-reference.md` for the canonical statement and removes the inline echoes.
**Verdict:** EXCESS. G1 win, conditional on reference reading.

---

## C. Gaps that are genuine current-dmaic STRENGTHS the spec under-emphasizes

### C1. **The "Common mistakes to flag" section** (lines 214-222 of current)
Current dmaic lists 5 concrete antipatterns (starting at Improve, skipping Control, measuring everything, vanity metrics, treating it as a one-time spec). The spec encodes "vanity metrics" and "skipping Control" as gates but omits the "treating it as a one-time spec" antipattern as an in-prose reminder.
**Verdict:** worth keeping as a brief block in the redesigned SKILL.md — antipatterns are a learning artifact for the agent itself, not just the user.

### C2. **The Linglepedia routing-by-domain conventions** (lines 168-178 of current — GIX→GIX/, WE→WE/, etc.)
Current dmaic encodes specific Linglepedia knowledge. The spec abstracts this into "vault_context" and assumes `dmaic.py kickoff` returns a routing hint.
**Verdict:** the script must absorb this knowledge; otherwise the spec produces vault-naive routing. Verify in build pass.

### C3. **The explicit `truth_score` and `last_reviewed` frontmatter fields** (line 9 of current's references/spec-template.md)
Current dmaic carries vault-specific metadata. The spec mentions it parenthetically in the schema-PR sub-task but doesn't encode it as a hard requirement.
**Verdict:** minor — the existing `dmaic.py compose` script handles these fields; the spec doesn't need to restate.

---

## D. Mike-goal coverage scorecard

| Goal | Verified spec addresses how? | Coverage strength |
|---|---|---|
| **G1** (minimize tokens) | A4, A5, A6, A8, B1, B3, B4, B5, B6, B7, B9 — collectively ~80–100 lines deletable from current SKILL.md if executed | High — clear path to a ≤130-line redesigned SKILL.md |
| **G2** (MECE parallelism) | A3 (s2/s3 fan-out), partial s4 fan-out per Parallelization section | Medium-high — the design supports it; the build pass needs to implement Task dispatch with sequential fallback |
| **G3** (scripts over agents) | A2 (check-causal-chain), A4 (validate-owner), A5 (no-silent-overwrite), A6 (checkpoint), A7 (log-event), A8 (iterate-mode), B8 — five new/expanded script subcommands | High — most of the agentic prose in current dmaic moves into deterministic script calls |
| **G4** (controllable vs external + causal chains) | A1 (External Input Metrics), A2 (causal_chain block + script enforcement), spec's own Metrics Map demonstrates the pattern in five-category form | High — this is the headline change; the design and the script enforcement are both specified |

---

## E. Top 3 gaps that should drive iter-1 fixes to dmaic

1. **A2 — Causal-chain block in Analyze with `dmaic.py check-causal-chain` script enforcement.** This is the headline G4 change. Without it, "controllable vs external" is just nomenclature; with it, every produced spec is forced to draw the input→output edges. Highest leverage, smallest implementation effort.

2. **A1 — External Input Metrics category in both the SKILL.md guidance AND the Linglepedia `_schemas/dmaic-spec.md` schema.** Pre-requisite for A2 to feel coherent. The schema PR can land in parallel with the SKILL.md rewrite. Without this, A2's enforcement script fires against a structure the schema doesn't recognize.

3. **A3 + A7 — MECE parallel fan-out in Measure/Analyze (G2) AND telemetry events (G3).** Bundle these because they reinforce each other: parallelism without telemetry can't be measured against the sequential baseline (no parallelization_efficiency metric); telemetry without parallelism still lets us measure the rest of the redesign empirically. Together they make iter-2 data-driven instead of narrative.

The remaining gaps (A4–A10, B1–B9, C1–C3) are all worth doing but are secondary to these three.
