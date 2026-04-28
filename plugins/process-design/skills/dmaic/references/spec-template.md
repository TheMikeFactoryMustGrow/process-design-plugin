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

> Three categories. Outputs confirm; inputs are the levers; external inputs bound what the levers can do. Cap **outputs** at 2–3 (more is noise). Controllable + external inputs scale with the process — name as many as actually drive the outputs.

### Output Metrics (terminal — confirm success)

#### Metric 1: [Name]
- **Definition:** [How it's calculated, including units (%, ms, $, count, etc.)]
- **Collection:** [How and how often]
- **Baseline:** [Current value, or "unknown — establish by YYYY-MM-DD"]
- **Target:** [Where it needs to land]

#### Metric 2: [Name]
- **Definition:**
- **Collection:**
- **Baseline:**
- **Target:**

### Controllable Input Metrics (the levers — owner can move these)

#### Metric C1: [Name]
- **Definition:** [How it's calculated, including units]
- **Collection:**
- **Baseline:**
- **Target:**

#### Metric C2: [Name]
- **Definition:**
- **Collection:**
- **Baseline:**
- **Target:**

### External Input Metrics (context — affect output, can't be moved)

#### Metric E1: [Name]
- **Definition:** [How it's calculated, including units]
- **Collection:**
- **Baseline:**
- **Target:** _N/A — track only_

---

## Analyze

### Causal Chain (which inputs drive which outputs)

For each output metric, name the controllable input(s) that move it. **If an output has no controllable input listed, the spec is incomplete — go back to Measure.** External inputs go in the third column to bound what the levers can plausibly do.

| Output Metric | Controllable Inputs | External Inputs (bounds) |
|---|---|---|
| [Output Metric 1] | [Controllable Input(s) — comma-separated] | [External Inputs that bound the relationship] |
| [Output Metric 2] | [Controllable Input(s)] | [External Inputs] |

### Per-output thresholds and playbooks

#### [Output Metric 1]
- **Threshold (red / yellow / green):** [e.g. red ≤ baseline, yellow ≤ midpoint, green ≥ target]
- **Known failure modes (3–5):** [named cause 1], [2], [3]
- **First action when threshold trips:** [action] — owned by [[Person]]
- **Time-to-resolve target:** [e.g. 24h, 1 week]

#### [Output Metric 2]
- **Threshold (red / yellow / green):**
- **Known failure modes:**
- **First action:** owned by [[Person]]
- **Time-to-resolve target:**

---

## Improve

> Every improvement attempt is an experiment. Frame it as one.

### Experiment 1 *(or "None in flight")*
- **Hypothesis:** "We believe [change] will [effect] because [reasoning]."
- **Test plan:** [What changes, on what scope, for how long]
- **Success criterion:** [Which metric moves, by how much]
- **Failure criterion:** [What result triggers a revert]
- **Owner:** [[Person]]
- **Start date:** YYYY-MM-DD
- **Decision date:** YYYY-MM-DD
- **Status:** proposed | running | succeeded | failed | reverted

> Add `### Experiment 2`, `### Experiment 3`, etc. as new ones launch. The template supports a portfolio, not a single in-flight experiment.

---

## Control

The regression guard. Don't let this section be empty.

### Monitoring
- **Metric watched:** [which output metric]
- **Cadence:** [e.g. weekly Monday review, real-time alert]
- **Watcher:** [[Person]]

### Alert
- **Trigger:** [threshold or condition]
- **Destination:** [Slack channel, pager, email]
- **Responder:** [[Person]]
- **Response SLA:** [e.g. 24 hours]

### Recurring spec review
- **Cadence:** [e.g. quarterly]
- **Reviewer:** [[Person]]
- **Trigger conditions for off-cycle review:** [e.g. output drift > 20%, 3 alerts in a week]

---

## Experiments Log

| Date | Hypothesis | Result | Decision |
|---|---|---|---|
| | | | |

---

## Notes

[Free-form context, links to related work, decisions, references.]
