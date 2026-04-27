---
name: dmaic-measure
description: Run only the Measure phase of the Six Sigma DMAIC cycle as a standalone building block — design 2–3 terminal metrics for a process or idea, with name, calculation, units, collection plan, baseline, and target. Use when the user explicitly wants the metric design step in isolation and not the full DMAIC cycle (e.g., "just help me name the metrics", "I already defined this, now do the metrics", "do the Measure phase only"), OR when another skill (such as the `dmaic` orchestrator, a feature-spec skill, or a metrics-tracking skill) calls this phase à la carte. If the user is asking for metrics on a fresh process and hasn't done Define yet, prefer the `dmaic` orchestrator instead — running Measure without Define produces untethered metrics. Output is a Measure block ready to drop into a DMAIC spec. Capped at 3 metrics. Pushes back on vanity metrics.
---

# DMAIC — Measure Phase

Design 2–3 **terminal** metrics that tell you whether the process is working. Reject vanity metrics. Push for outcomes, not activity.

> *"Terminal metrics are the only ones that matter. Intermediate metrics are for diagnosis, not justification."*

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

A Measure block — 2–3 metrics, each with name, definition, collection plan, baseline, and target — ready to drop into a DMAIC spec.

---

## Procedure

### 1. Confirm the process and the success/failure sentences

If a Define block was already produced (by `dmaic-define` or the orchestrator), use it. Otherwise ask: "Before we name metrics, what does success look like for this process? What does failure look like?" Without those, the metrics will be untethered.

### 2. Identify candidate metrics

Brainstorm 5–10 candidates. Then ruthlessly cut.

For each candidate, ask:
- **Is it terminal or intermediate?** Terminal = if it's good, the process is good. Intermediate = useful for diagnosis but doesn't tell you whether the process succeeded.
- **Is it an outcome or an activity?** Outcomes (conversion, retention, latency, error rate, dollars retained) beat activity (calls made, tickets opened, posts published) almost always.
- **Could it go up while the world gets worse?** If yes, it's a vanity metric. Cut.

### 3. Cap the list at 3

Pick the 2–3 strongest. More is noise. If the user insists on more, push back: "Adding a fourth metric usually means none of them get attention. Which is the weakest of the four — that's the one to cut."

### 4. Specify each metric

For each surviving metric, capture:

- **Name.** Short, unambiguous. Avoid acronyms unless they're universal in the user's org.
- **Definition.** How it's calculated. Include **units** explicitly. ("Net Revenue Retention = (Starting ARR + Expansion − Contraction − Churn) / Starting ARR, expressed as a percentage.")
- **Collection.** How and how often:
  - Source system (Salesforce, billing system, support tool, manual log, etc.)
  - Cadence (per-event, daily, weekly, monthly, quarterly)
  - Owner of the collection (who's responsible for the number being right)
- **Baseline.** Current value. If unknown, say so explicitly: `"unknown — establish by [date]"`. The baseline being embarrassing is fine. The baseline being unknown is a Measure-phase failure.
- **Target.** Where it needs to land for the process to count as working. Tie this back to the success sentence from Define.

### 5. Stress-test the set

Ask:
- **Symmetry test:** Could success on these metrics coexist with the failure sentence from Define being true? If yes, the metrics don't measure what we said we cared about — re-pick.
- **Goodhart test:** If every team member optimized this metric to the exclusion of all else, would the process actually be better, or just the metric? If the metric, redesign it.
- **Collection feasibility:** If collecting this metric requires data the user doesn't have, either fix the data plumbing or pick a different metric.

---

## Output format

```markdown
## Measure

> Pick 2–3 terminal metrics. More is noise.

### Metric 1: [Name]
- **Definition:** [Calculation, units]
- **Collection:** [Source system; cadence; owner]
- **Baseline:** [Current value, or "unknown — establish by [date]"]
- **Target:** [Where it needs to land]

### Metric 2: [Name]
...

### Metric 3: [Name] *(optional)*
...
```

If running standalone, tell the user this is the Measure block and that the next step is `dmaic-analyze` to set thresholds and known failure modes.

---

## Common mistakes

- **Vanity metrics.** Impressions, page views, headcount, "engagement" — push for outcomes.
- **Activity instead of outcome.** "Calls made" is activity. "Calls converted" is closer to outcome. "Revenue retained from those calls" is the outcome.
- **No baseline.** Without a baseline you can't tell if anything improved. Establish the baseline even if the number is bad.
- **More than three metrics.** Cap is enforced for a reason — attention is the scarce resource.
- **No units.** "Latency" without units (ms? s? p50? p99?) is ambiguous. Always specify.
- **Metric without a collection owner.** Numbers nobody owns are numbers that drift.
- **Decoupling metric from success sentence.** If the metric being good doesn't imply the success sentence is true, the metric is wrong.

---

## Principle

*"You can't improve what you can't measure."* — But also: a bad metric is worse than no metric, because it directs effort at the wrong target. Spend the time to get this right.
