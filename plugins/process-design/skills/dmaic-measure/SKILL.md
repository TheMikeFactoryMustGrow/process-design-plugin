---
name: dmaic-measure
description: Run only the Measure phase of the Six Sigma DMAIC cycle as a standalone building block — design metrics across three categories (output / controllable input / external input) for a process or idea, with name, calculation, units, collection plan, baseline, and target. Cap **outputs** at 2–3; controllable inputs and external inputs scale with the process. Use when the user explicitly wants the metric design step in isolation and not the full DMAIC cycle (e.g., "just help me name the metrics", "I already defined this, now do the metrics", "do the Measure phase only"), OR when another skill (such as the `dmaic` orchestrator) calls this phase à la carte. If the user is asking for metrics on a fresh process and hasn't done Define yet, prefer the `dmaic` orchestrator instead — running Measure without Define produces untethered metrics. Output is a Measure block ready to drop into a DMAIC spec. Pushes back on vanity metrics and on output-only thinking that omits the controllable levers.
---

# DMAIC — Measure Phase

Design metrics across three categories. **Outputs** confirm whether the process is working. **Controllable inputs** are the levers the owner can move when an output goes red. **External inputs** are context that affects the output but the owner can't move — track them so you can tell drift from noise.

> *Outputs confirm; inputs are the levers. A spec with outputs but no controllable inputs produces dashboards no one can act on.*

---

## When to use

- "Design metrics for [process]"
- "What should I measure for [thing]?"
- "Create metrics for [idea]"
- "Help me name the metrics for [process]"
- "Establish a baseline for [thing]"
- "DMAIC measure for [process]"
- Called by `dmaic` orchestrator or any other skill that needs metric design

---

## What this skill produces

A Measure block organized into three sub-sections — Output Metrics (2–3), Controllable Input Metrics (as many as drive the outputs), External Input Metrics (context). Ready to drop into a DMAIC spec.

---

## Procedure

### 1. Confirm Define is settled

If a Define block exists, use it. If not, ask the success/failure sentences first — metrics without those are untethered.

### 2. Pick output metrics first (cap 2–3)

These are the terminal measures: if they're good, the process is good. For each candidate, ask:
- **Is it terminal or intermediate?** Terminal = if it's good, the process is good. Intermediate = diagnostic only — those are inputs, not outputs.
- **Outcome or activity?** Outcomes (conversion, retention, latency, error rate) beat activity (calls made, tickets opened) almost always.
- **Could it go up while the world gets worse?** If yes, it's a vanity metric. Cut.

If the user insists on a 4th output, push back: "Adding a fourth output usually means none of them get attention. Which is weakest? That's the cut."

### 3. Identify controllable input metrics — the levers

For each output, name the controllable inputs that move it. These are the things the owner can change in response to a red threshold. Examples (very domain-specific):
- For "customer onboarding completion rate" (output): step-1-form-completion-rate, time-to-first-response, in-product-help-clicks (controllable inputs).
- For "revenue retention" (output): success-rep-touchpoint-count, renewal-pricing-discount-rate, product-uptime (controllable inputs).

Track as many controllable inputs as actually drive the outputs. There is no cap — but each one has to demonstrably move at least one output (or it's noise).

### 4. Identify external input metrics — context

What affects the output that the owner can't change? Macroeconomic factors, seasonality, competitor moves, upstream-vendor health. Track these so an output dip can be diagnosed: was it a lever failure or external noise?

External inputs have **no Target** — Target is N/A. They're tracked, not optimized.

### 5. Specify each metric (all three categories)

- **Name.** Short, unambiguous. Avoid acronyms unless universal.
- **Definition.** Calculation + **units** (always include units: %, ms, $, count, ratio).
- **Collection.** Source system + cadence + collection owner.
- **Baseline.** Current value, or `"unknown — establish by YYYY-MM-DD"`.
- **Target.** For outputs + controllable inputs only; N/A for externals.

### 6. Stress-test the set

- **Symmetry test:** Could good outputs coexist with the failure sentence from Define being true? If yes, re-pick the outputs.
- **Goodhart test:** If a team optimized this output to the exclusion of all else, would the process actually be better? If only the metric, redesign.
- **Lever-coverage test:** Does every output have at least one controllable input traceable to it? If not, the spec is incomplete — Analyze's causal chain check will fail.
- **Collection feasibility:** If a metric needs data that doesn't exist yet, either build the plumbing or pick differently.

---

## Output format

Use `dmaic.py scaffold --phase measure --metrics N` to emit the three-category template. The agent fills in the angle-bracket placeholders. Per-output work is MECE — when Task fan-out is available, spawn one subagent per output for the metric-design work.

If running standalone (no script available), follow the same three-category structure as `references/spec-template.md`. Tell the user the next step is `dmaic-analyze` to draw the causal chain and set thresholds.

---

## Common mistakes

- **Outputs only, no levers.** The biggest failure mode. The spec lists outputs and stops, leaving the owner with a dashboard and no actionable response. Always name the controllable inputs.
- **Inputs misclassified as outputs.** Activity counts ("calls made", "tickets opened") are usually controllable inputs, not outputs. The output is the *result* of the activity (calls converted, tickets resolved within SLA).
- **External inputs missing.** Without external-input tracking, output drift looks like lever failure when it might be macro noise. Always identify the 1–2 biggest external factors.
- **Vanity metrics in any category.** Impressions, page views, headcount, "engagement" — push for outcomes.
- **No baseline.** "Unknown" is fine if you commit to a date to establish it. Bare "unknown" is a Measure failure.
- **No units.** "Latency" without units (ms? s? p50? p99?) is ambiguous. Always specify.
- **Metric without a collection owner.** Numbers nobody owns are numbers that drift.
- **Decoupling metrics from Define.** If good outputs could coexist with the failure sentence being true, the outputs are wrong.

---

## Principle

*"You can't improve what you can't measure."* — But also: a bad metric is worse than no metric, because it directs effort at the wrong target. Spend the time to get this right.
