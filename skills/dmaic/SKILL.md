---
name: dmaic
description: Measurement-and-improvement scaffold for any process the user wants to make better. Trigger whenever the user describes a process that's drifting, chaotic, or unmeasured — phrasings like "this is hit or miss", "we don't actually know if X is working", "I want to track [process]", "make this measurable", "design metrics for this", "create an improvement plan", or any time the user wants to tighten a fuzzy goal into named metrics with a regression guard, even when they never say "DMAIC" by name. Walks the five Six Sigma phases (Define → Measure → Analyze → Improve → Control) and writes a structured spec to the user's knowledge vault (Obsidian/Linglepedia) when present, otherwise to a markdown file. Defaults to this orchestrator over the per-phase skills (dmaic-define, dmaic-measure, dmaic-analyze, dmaic-improve, dmaic-control) unless the user is clearly asking for one phase in isolation, or another skill is calling a phase à la carte.
---

# DMAIC

Apply the full DMAIC cycle to a process or idea, then save a structured spec.

> **Order matters.** Define before you Measure. Measure before you Analyze. Analyze before you Improve. Improve before you Control. Most people start at Improve and wonder why nothing sticks.

---

## When to use this skill

Trigger on phrases like:

- "Run DMAIC on [process]"
- "Create metrics for [process / idea]"
- "Make [thing] measurable"
- "Design an improvement cycle for [thing]"
- "Spec [process] so we can improve it"
- "I want to track / improve / monitor [thing]"
- "Build a measurement plan for [thing]"

If the user only wants one phase (e.g., "just help me name the metrics"), invoke the phase skill directly: `dmaic-define`, `dmaic-measure`, `dmaic-analyze`, `dmaic-improve`, `dmaic-control`.

---

## Inputs to gather

Before running any phase, capture three things from the user. Ask only what's missing — don't ask if the request already answers it.

1. **The subject.** What process, system, or idea are we DMAIC-ing? Get a one-sentence description.
2. **The owner.** Who is accountable for this process? (Person, role, or team.)
3. **The output target.** Where should the final spec live? Default behavior:
   - If running in a session with a knowledge vault mounted (look for `CLAUDE.md`, an Obsidian vault root, or a `_schemas/` folder), propose saving as a structured note in the vault. Ask the user which folder.
   - If running in Linglepedia specifically, default to `Projects/` unless the subject clearly belongs in a domain folder (e.g., a GIX customer-onboarding process → `GIX/`).
   - Otherwise, write a markdown file to the working directory and tell the user the path.

Don't proceed until you have a subject. Owner and target can be filled in later if the user is exploring.

---

## The five phases

Two ways to run the phases — both are valid:

1. **Invoke the per-phase skills via the Skill tool.** Cleanest separation. Call `dmaic-define`, then `dmaic-measure`, then `dmaic-analyze`, then `dmaic-improve`, then `dmaic-control`, in that order. Each one returns its block.
2. **Apply the rules inline.** If invoking sub-skills isn't practical (e.g., they aren't installed, or the cost of the extra hops doesn't pay off for the task), follow the per-phase summaries below in the same order. The summaries are deliberately self-contained.

Either way, the order matters. Define before Measure, Measure before Analyze, Analyze before Improve, Improve before Control. Don't let the user start at Improve.

### Phase 1 — Define

Capture three sentences:
- **What is this process supposed to do?** State the purpose in one sentence. No jargon.
- **What does success look like?** A concrete, observable end state.
- **What does failure look like?** Equally concrete. Failure is the absence of success, but stating it explicitly forces clarity.

Stuck? The most common Define failure is fuzziness ("improve customer experience"). Push for "customers complete onboarding in under 5 minutes without contacting support." If the user can't write the failure sentence, the success sentence is too vague.

### Phase 2 — Measure

The user's biggest gap, almost always. Three categories, in order:

**Output Metrics (terminal — confirm success).** Cap at 2–3. These are the only metrics that count as "process is working." Reject vanity metrics (impressions, headcount, page views) unless they truly bind to outcome. *Rule: if the metric goes up but the world isn't better, it's the wrong metric.*

**Controllable Input Metrics (the levers — owner can move these).** As many as actually drive the outputs. These are what the operator changes when an output goes red. Without controllable inputs the spec produces dashboards with no actionable response.

**External Input Metrics (context — affect output, can't be moved).** Track them so you can tell whether an output dip was a lever failure or external noise. Target is N/A; the field exists to bound what the levers can plausibly do.

For every metric in every category, capture: **Name** (short, unambiguous), **Definition** (calculation + units), **Collection** (how + how often), **Baseline** (current value, or `unknown — establish by YYYY-MM-DD`), **Target** (where it needs to land; N/A for external).

**Parallelization.** Per-metric work is MECE — when fan-out is available, spawn one Task subagent per output metric for the metric-design work, then integrate. Sequential fallback when Task isn't available.

To avoid hand-rolling the structure: `dmaic.py scaffold --phase measure --metrics N` emits the three-category template the agent fills in.

### Phase 3 — Analyze

**Causal chain first.** For every output metric, name the controllable input(s) that move it. If an output has no controllable input listed, the spec is incomplete — go back to Measure and add the missing lever. External inputs go in a third column to bound what the lever can plausibly do.

The causal chain is enforced: `dmaic.py check-causal-chain --file <spec> --strict` exits non-zero if any output lacks a traced lever. Run it before promoting `status: draft → active`.

**Per-output thresholds and playbooks.** For each output metric:
- **Threshold (red/yellow/green):** explicit bands or trigger values (e.g. red ≤ baseline, green ≥ target).
- **Known failure modes (3–5):** named causes drawn from the controllable + external inputs identified above.
- **First action when threshold trips:** concrete step + named owner + time-to-resolve target. "Owner investigates" is not a first action.

**Parallelization.** Per-output threshold work is MECE — fan out one Task subagent per output metric, integrate after.

`dmaic.py scaffold --phase analyze --metrics N` emits the causal-chain table + per-output blocks.

### Phase 4 — Improve

Frame every improvement attempt as an experiment. Real DMAIC cycles run **multiple concurrent experiments**, not one at a time — Improve is a portfolio.

For each experiment in flight, capture: **Hypothesis** ("we believe X will Y because Z"), **Test plan** (what changes, scope, duration), **Success criterion** (which metric moves, by how much), **Failure criterion** (what triggers revert), **Owner** (named person), **Decision date**, **Status** (proposed | running | succeeded | failed | reverted).

If no improvements are in flight yet, leave this section noting "experiments logged here as they launch." The Experiments Log table at the bottom of the spec records every attempt — *failed experiments are data, not waste*.

`dmaic.py scaffold --phase improve --experiments N` emits N pre-formatted experiment blocks.

### Phase 5 — Control

Design the regression guard. Most fixes regress because nobody designed one.

- **Monitoring:** which output metric, what cadence, named watcher.
- **Alert:** trigger condition, destination, named responder, response SLA.
- **Recurring spec review:** cadence (e.g. quarterly), named reviewer, off-cycle trigger conditions.

`dmaic.py scaffold --phase control` emits the structured template.

---

## Composing the output

`scripts/dmaic.py` owns every deterministic operation — vault detection, frontmatter assembly, slug, routing, per-phase scaffolds, validation, causal-chain check. The agent reasons about content; the script formats. The flow is four calls:

```bash
SCRIPT=<plugin-root>/skills/dmaic/scripts/dmaic.py

# 1. Vault detection (returns vault_root + Linglepedia domain hints)
python3 $SCRIPT detect-vault --cwd .

# 2. Skeleton spec.json (agent fills the phase-block content)
python3 $SCRIPT prefill --process "X" --owner "Y" --tags gix,operations \
  --summary "..." > /tmp/dmaic-spec.json

# 3. Per-phase scaffolds (one call per phase the agent populates)
python3 $SCRIPT scaffold --phase measure --metrics 3
python3 $SCRIPT scaffold --phase analyze --metrics 3
python3 $SCRIPT scaffold --phase improve --experiments 1
python3 $SCRIPT scaffold --phase control

# 4. Compose + validate (refuses to overwrite without --force)
python3 $SCRIPT compose --input /tmp/dmaic-spec.json \
  --output <vault_root>/<domain>/dmaic-<slug>.md --validate-after
python3 $SCRIPT check-causal-chain --file <path> --strict
```

**Routing rules** (live in the script's `detect-vault` output, not the agent's head): GIX process → `GIX/`, WE → `WE/`, personal → `Projects/`, default `Projects/`. Slug is `dmaic-<kebab-process-name>.md`. If no vault is detected, write to cwd.

**Schema cross-check.** If a `_schemas/dmaic-spec.md` exists in the vault, read it once at the start — extra required fields you find pass through `prefill` via additional `--tags` / spec.json keys; `compose` preserves any unknown fields.

**Owner.** Run `validate-owner --owner "X"` first — the script rejects department-shaped names ("the team", "operations") so the spec doesn't ship with no accountable individual.

**No silent overwrites.** `compose` refuses to overwrite an existing file unless `--force`. If a spec already exists at the target path, surface the conflict and offer (a) resume, (b) write to a sibling path, (c) different name.

---

## Common mistakes to flag

When the user is working through a phase, watch for these and push back gently:

- **Starting at Improve.** "Let me suggest we Define first — what does this process even do?"
- **Skipping Control.** Don't let the spec ship without a Control section, even if it's "TBD — needs designing in week 2."
- **Measuring everything OR confusing categories.** Cap **outputs** at 2–3. Controllable inputs scale with the process. Without the three-category split (output / controllable / external), specs produce dashboards no one can act on.
- **Vanity metrics.** Push for outcomes, not activity.
- **Treating it as a one-time spec.** Set `last_reviewed` and tell the user the spec needs a quarterly re-read.

---

## References

- `references/spec-template.md` — exact markdown template for the output note
- `references/dmaic-reference.md` — the canonical DMAIC theory (excerpt of `[[DMAIC]]` from the Linglepedia vault)

---

## Principles (from `[[DMAIC]]`)

1. **Mechanisms over philosophy.** "Get better every day" is a wish. A DMAIC cycle with named metrics and regression detection is a mechanism.
2. **Measure before you improve.** Establish a baseline first, even if the numbers are embarrassing.
3. **Control is not optional.** Every improvement without a regression guard is temporary.
4. **Outputs confirm; inputs are the levers.** Cap output metrics at 2–3 (those tell you whether the process is working). Track as many controllable input metrics as actually drive the outputs (those tell you which knob to turn). External inputs go in their own bucket so you can tell drift from noise. The Analyze causal chain forces this distinction to be drawn explicitly — a spec where outputs trace to no controllable inputs is incomplete.
5. **Failed experiments are data.** Log every attempt.
6. **Agents own their own DMAIC.** Each owner inventories their own processes and builds their own cycles.
7. **Evolve the framework.** Propose improvements as you learn what works.
