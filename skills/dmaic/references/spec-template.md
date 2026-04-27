---
type: dmaic-spec
process: "[Process Name]"
owner: "[[Person or Role]]"
status: draft
created: YYYY-MM-DD
last_reviewed: YYYY-MM-DD
truth_score: 0.5
tags:
  - dmaic
  - "[domain-tag]"
related:
  - "[[DMAIC]]"
---

# DMAIC — [Process Name]

> One-sentence summary of what this process is and why we're DMAIC-ing it.

---

## Define

**What this process is supposed to do:**
[One sentence. Concrete. No jargon.]

**What success looks like:**
[Observable end state. A future scene, not an adjective.]

**What failure looks like:**
[Equally observable. The absence of success, stated explicitly.]

---

## Measure

> Pick 2–3 terminal metrics. More is noise.

### Metric 1: [Name]
- **Definition:** [How it's calculated, including units]
- **Collection:** [How and how often]
- **Baseline:** [Current value, or "unknown — establish by [date]"]
- **Target:** [Where it needs to land]

### Metric 2: [Name]
- **Definition:**
- **Collection:**
- **Baseline:**
- **Target:**

### Metric 3: [Name] *(optional)*
- **Definition:**
- **Collection:**
- **Baseline:**
- **Target:**

---

## Analyze

For each metric, define what to do when it goes bad.

### [Metric 1 Name]
- **Threshold:** [Green / Yellow / Red bands or trigger value]
- **Known failure modes:**
  1. [Cause]
  2. [Cause]
  3. [Cause]
- **First action when it trips:** [Concrete step + who runs it]

### [Metric 2 Name]
- **Threshold:**
- **Known failure modes:**
- **First action:**

### [Metric 3 Name]
- **Threshold:**
- **Known failure modes:**
- **First action:**

---

## Improve

> Every improvement attempt is an experiment. Frame it as one.

### Current experiment *(or "None in flight")*
- **Hypothesis:** "We believe [change] will [effect] because [reasoning]."
- **Test plan:** [What changes, on what scope, for how long]
- **Success criterion:** [Which metric moves, by how much]
- **Failure criterion:** [What result triggers a revert]
- **Owner:** [[Person]]
- **Start date:**
- **Decision date:**

---

## Control

The regression guard. Don't let this section be empty.

- **Monitoring:** [Which metric, watched on what cadence, by whom]
- **Alert:** [What trips it, where it goes, who responds]
- **Recurring review:** [When and how often the spec itself gets re-examined]

---

## Experiments Log

| Date | Hypothesis | Result | Decision |
|---|---|---|---|
| | | | |

---

## Notes

[Free-form context, links to related work, decisions, references.]
