---
name: dmaic-control
description: Run only the Control phase of the Six Sigma DMAIC cycle as a standalone building block — design the regression guard that keeps a fix fixed, with monitoring (which metric, what cadence, who watches), an alert (trigger, destination, named responder, response SLA), and a recurring spec review. Use when the user explicitly wants the Control step in isolation (e.g., "we just shipped this fix, lock it in", "design a regression guard for this", "set up monitoring for this process", "do the Control phase only"), OR when another skill (such as the `dmaic` orchestrator) calls this phase à la carte. If the user wants the full cycle, prefer the `dmaic` orchestrator instead. Output is a Control block ready to drop into a DMAIC spec. Trigger this proactively whenever a user describes shipping a fix or improvement — the regression guard is the phase most people skip, and most improvements are temporary as a result.
---

# DMAIC — Control Phase

Design the regression guard. The phase most people skip — and the reason most fixes are temporary.

> *"Control is not optional. Every improvement without a regression guard is temporary."*

---

## When to use

- "Prevent regression for [process / fix]"
- "Lock in the gain on [thing]"
- "Design a regression guard for [process]"
- "Set up monitoring for [process]"
- "DMAIC control for [process]"
- Called by `dmaic` orchestrator or any skill that needs Control in isolation

---

## What this skill produces

A Control block — monitoring plan, alert configuration, and recurring review schedule — ready to drop into a DMAIC spec.

---

## Procedure

### 1. Confirm what's being controlled

The Control phase locks in the gains from a successful Improve experiment, OR maintains the baseline of a process that's already working. Ask the user which: "Are we controlling a recently shipped fix, or maintaining a steady-state process?"

### 2. Pick the metric(s) to watch

From the Measure block, identify the metric(s) most at risk of regression. Often this is the primary metric the Improve experiment moved. If the user already has a working process and you're at Control without a recent Improve, the watched metric is the one whose value the user most fears losing.

Default: **watch all the terminal metrics.** Cap at 3, same as Measure.

### 3. Specify the monitoring

For each watched metric, capture:

- **Source.** Where the live value is read from. Same source as the Measure plan — if the source is different, that's a smell.
- **Cadence.** How often it's checked. Real-time? Daily? Weekly? Monthly? Match the cadence to how fast the metric can drift to bad. A daily check on a metric that can collapse in an hour is theater.
- **Watcher.** Single named human responsible for the metric being looked at on cadence. Tools don't watch — people do, with tools as instruments.
- **Where the value is visible.** Dashboard URL, report, scheduled email, weekly review doc. If the value isn't visible somewhere persistent, it's not being monitored.

### 4. Specify the alert

The watching cadence will miss fast-moving regressions. Alerts catch what the human eye doesn't.

- **Trigger.** Threshold from the Analyze phase, OR a tighter version for early warning. Reuse Analyze thresholds where possible to avoid drift between phases.
- **Where the alert goes.** Slack channel, email distribution, PagerDuty, a person's phone. Alerts that go nowhere or to a dead distribution list are worse than no alerts (they create false confidence).
- **Who responds.** Single named owner. If multiple people are on the alert, name the responder-of-record explicitly.
- **Response SLA.** "Acknowledge within X, action within Y." If there's no SLA, the alert will fire and be ignored.

### 5. Specify the recurring spec review

The DMAIC spec itself drifts. Metrics that mattered six months ago may not anymore. Thresholds set on stale baselines stop being meaningful.

- **Review cadence.** Quarterly is the default. Monthly for high-velocity processes, semi-annually for slow-moving ones.
- **Reviewer.** Usually the process owner. The job of the review: re-read the spec, update `last_reviewed`, decide if any phase needs to be re-run.
- **Trigger conditions for off-cycle review.** When does the spec get re-examined ahead of schedule? Examples: "Any time a Red threshold trips," "Any time a successful Improve experiment ships," "Any time the process owner changes."

### 6. Stress-test

- **Would the regression actually be caught?** Walk through a hypothetical failure: how does the watcher (or the alert) find out, how fast, and what do they do? If the answer is "they wouldn't notice for weeks," tighten the cadence or add an alert.
- **Is the alert routed somewhere live?** Check the destination. A Slack channel nobody reads is a worse outcome than no alert, because it creates the illusion of monitoring.
- **Does the review cadence match the process velocity?** A weekly process being reviewed annually is undermonitored. A yearly process being reviewed weekly is a waste of attention.

---

## Output format

```markdown
## Control

### Monitoring
- **Watched metric(s):** [List]
- **Source:** [Same as Measure: dashboard / system / report]
- **Cadence:** [Real-time / daily / weekly / monthly]
- **Watcher:** [[Person]]
- **Visible at:** [URL / location]

### Alert
- **Trigger:** [Threshold or condition]
- **Goes to:** [Channel / person / system]
- **Responder:** [[Person]]
- **Response SLA:** [Acknowledge in X, action in Y]

### Recurring spec review
- **Cadence:** [Quarterly / monthly / semi-annually]
- **Reviewer:** [[Person — usually the process owner]]
- **Off-cycle review triggers:**
  - [Condition 1]
  - [Condition 2]
```

If running standalone, tell the user the spec is now complete. The next step is to make sure `last_reviewed` is set and a calendar reminder exists for the next review.

---

## Common mistakes

- **No Control phase at all.** The most common — the team ships the fix, declares victory, moves on. The fix regresses within a quarter and nobody notices until the failure mode resurfaces.
- **Alerts going to a dead channel.** Verify the channel is monitored, by humans, who will respond. A muted Slack channel is worse than no alert.
- **No SLA on alert response.** "Someone will look at it" is not a response plan.
- **No spec review cadence.** Without periodic re-reads, the spec rots. Stale specs are spec-shaped lies.
- **Watcher = "the team".** Same problem as everywhere else in DMAIC. Pick a single human.
- **Reusing the Analyze threshold without checking.** Analyze thresholds were set to demand investigation. Control thresholds may want to be tighter (early warning) or looser (only fire on actual regression). Decide deliberately.
