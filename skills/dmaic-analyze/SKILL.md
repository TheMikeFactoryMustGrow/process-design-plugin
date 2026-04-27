---
name: dmaic-analyze
description: Run only the Analyze phase of the Six Sigma DMAIC cycle as a standalone building block — for each metric in a process spec, set thresholds (green/yellow/red bands or trigger values), enumerate the 3–5 most common failure modes, and define the first action plus owner when a threshold trips. Use when the user explicitly wants the Analyze step in isolation (e.g., "just help me set thresholds for these metrics", "build an investigation playbook for this process", "do the Analyze phase only"), OR when another skill (such as the `dmaic` orchestrator) calls this phase à la carte. If the user wants the full cycle, prefer the `dmaic` orchestrator instead. Output is an Analyze block ready to drop into a DMAIC spec. This is the phase that turns passive dashboards into actionable triggers.
---

# DMAIC — Analyze Phase

Connect each metric to action. Without this phase, you have dashboards nobody looks at.

---

## When to use

- "Set thresholds for [metric / process]"
- "What are the failure modes for [process]?"
- "What should I investigate when [metric] crosses a line?"
- "Build an investigation playbook for [process]"
- "DMAIC analyze for [process]"
- Called by `dmaic` orchestrator or any skill that needs Analyze in isolation

---

## What this skill produces

An Analyze block — for each metric, a threshold, a list of known failure modes, and a first-action playbook.

---

## Procedure

### 1. Confirm the metrics

If a Measure block was already produced, use those metrics. Otherwise ask the user to name them, or run `dmaic-measure` first. You can't analyze what hasn't been measured.

### 2. For each metric, set thresholds

Choose the threshold style that fits the metric:

- **Banded (most common):** Green / Yellow / Red. Define each band's range.
  - Green = process working. No action.
  - Yellow = drift. Investigate within [time].
  - Red = process broken. Investigate immediately.
- **Trigger value:** A single number that, when crossed in either direction, demands investigation. Use when the metric is binary in spirit ("is the door locked?").
- **Rate of change:** Sometimes the metric's level is fine but its trajectory isn't. Define a rate threshold (e.g., "if it drops by more than 10% week-over-week").

Make the thresholds **defensible**: tie them to the success/failure sentences from Define. If a metric stays Green but the failure sentence is true, the threshold is wrong.

### 3. Enumerate known failure modes

For each metric, list **3–5 most common reasons** it goes bad. Generate from:
- The user's prior experience with this or similar processes.
- Industry-known failure modes (data pipeline drops, seasonality, dependency outages, staffing changes, etc.).
- Recent incidents or near-misses, if relevant.

If the user has zero failure-mode knowledge yet (brand-new process), state that explicitly and note that failure modes will be added as incidents accumulate.

### 4. Define the first action

For each threshold breach, capture:
- **Who runs the investigation.** Single named owner. "The team" doesn't show up.
- **The first thing they do.** A concrete step, not a goal. "Open the dashboard and identify which segment is driving the drop" — not "investigate the cause."
- **Where they document findings.** A specific note, ticket, or file. If undefined, the investigation will not be visible to anyone else.
- **Escalation criterion.** When does the first responder hand off to someone else? Time-based ("if not resolved in 4 hours") or scope-based ("if more than one customer is affected").

### 5. Stress-test

Ask:
- **Could a Yellow band be ignored without consequence?** If yes, the band is too wide. Tighten it or remove it.
- **Is the first action small enough that the on-call person will actually do it within minutes?** If it requires a meeting, it's too big. Decompose.
- **Does any failure mode appear under multiple metrics?** That's a signal the metrics overlap — go back to Measure and reconsider.

---

## Output format

```markdown
## Analyze

### [Metric 1 Name]
- **Threshold:**
  - Green: [range]
  - Yellow: [range] — investigate within [time]
  - Red: [range] — investigate immediately
- **Known failure modes:**
  1. [Cause]
  2. [Cause]
  3. [Cause]
- **First action when it trips:**
  - Owner: [[Person]]
  - Step 1: [Concrete action]
  - Document in: [Location]
  - Escalation: [Trigger]

### [Metric 2 Name]
...

### [Metric 3 Name]
...
```

If running standalone, tell the user the next step is `dmaic-improve` (when there's something to fix) or `dmaic-control` (to design the regression guard for whatever's already working).

---

## Common mistakes

- **Thresholds untied to Define.** Bands set "because they look right" instead of derived from the success/failure sentences.
- **Action too vague.** "Investigate the issue" is not an action. "Open the latency dashboard, filter to the affected region, screenshot the spike" is an action.
- **No owner.** A first action with no named human is a first action that doesn't happen.
- **No documentation location.** Investigations that don't get written down don't compound. Future you won't remember.
- **Failure modes copied from a template.** If the user can't tell a story about each failure mode happening, it's not a real failure mode for this process. Cut it.
