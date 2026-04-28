---
name: dmaic-improve
description: Run only the Improve phase of the Six Sigma DMAIC cycle as a standalone building block — frame a proposed change to a process as a falsifiable experiment, with hypothesis ("we believe X will Y because Z"), test plan, scope, success criterion, failure criterion, owner, and decision date baked in up front. Use when the user explicitly wants the Improve step in isolation (e.g., "design an experiment to test this fix", "frame this change as a hypothesis", "do the Improve phase only"), OR when another skill (such as the `dmaic` orchestrator) calls this phase à la carte. If the user wants the full cycle from problem framing through regression guard, prefer the `dmaic` orchestrator instead. Output is an Improve block ready to drop into a DMAIC spec. Failed experiments are data, not waste.
---

# DMAIC — Improve Phase

Frame every improvement attempt as a falsifiable experiment. Hypothesis, test plan, success criterion, failure criterion. Run it. Log the result. Decide.

> *"Failed experiments are data, not waste."*

---

## When to use

- "Test a fix for [process / metric]"
- "Hypothesize an improvement to [process]"
- "Design an experiment to improve [thing]"
- "DMAIC improve for [process]"
- Called by `dmaic` orchestrator or any skill that needs an Improve block

If the user is just spec'ing a process and has no improvement to test yet, return an empty Improve block (template only) and note that experiments will be added as they're proposed.

---

## What this skill produces

An Improve block — one experiment per proposed change, each with hypothesis, test plan, success/failure criteria, owner, and decision date.

---

## Procedure

### 1. Confirm the process and the metric being moved

The improvement must target a specific metric defined in Measure. Generic "make it better" experiments are not valid here. If the user is targeting something not yet measured, run `dmaic-measure` first.

### 2. State the hypothesis

Use this exact form: **"We believe [change] will [effect on metric] because [reasoning]."**

Examples:
- "We believe adding a guided checklist to the first-login email will increase 7-day activation rate by 5+ points because users currently fall off when they don't know what to do next."
- "We believe routing tier-2 tickets to a dedicated queue will reduce time-to-first-response by 30%+ because tier-1 currently triages each one twice."

If the user can't fill in the *because*, push back. A change with no reasoning isn't a hypothesis, it's a guess.

### 3. Define the test plan

Capture:
- **Scope.** What population, region, segment, or sample does the test apply to? (All users? 10% of new signups? One pilot region?)
- **Duration.** How long does the experiment run before a decision?
- **Variant.** What exactly changes for the test group, and what stays the same as the control?
- **Sample size / volume estimate.** Roughly how many events / users / cycles will the experiment touch? If the answer is "not enough to see a real signal," the experiment isn't worth running yet.

### 4. Define success and failure criteria

These are the falsifiable conditions that decide deploy vs. revert. Both required.

- **Success criterion.** Which metric moves, by how much, with what confidence. Be specific: "7-day activation rate moves from 45% to ≥50% on the test cohort."
- **Failure criterion.** What result triggers a revert. Often the absence of success — but sometimes there are *secondary* metrics that, if they degrade, force a revert even if the primary moved. Capture those too. ("Revert if activation moves but support ticket volume from the test cohort increases by >15%.")

If success and failure can both be true at once, sharpen the criteria.

### 5. Assign owner and decision date

- **Owner:** Single named human accountable for running the experiment to completion.
- **Start date:** When the change goes live for the test group.
- **Decision date:** When the owner makes deploy / revert / extend / redesign call. **Bake this in up front** — open-ended experiments rarely conclude.

### 6. Stress-test

- **Is the hypothesis falsifiable?** If no possible result would make the user say "we were wrong," it's not a hypothesis.
- **Is the experiment worth running?** Cost of running vs. value of learning. If the answer is the same regardless of result ("we'll keep doing it either way"), don't run it.
- **Are you measuring on the same metric you defined in Measure?** If you're inventing a new metric just for this experiment, that's a smell. Either the original metric is wrong (go fix Measure) or the new metric is convenient rather than terminal.

---

## Output format

```markdown
## Improve

### Experiment: [Short name]
- **Hypothesis:** "We believe [change] will [effect] because [reasoning]."
- **Test plan:**
  - Scope: [Population / segment]
  - Duration: [Time window]
  - Variant: [What changes]
  - Sample size: [Estimate]
- **Success criterion:** [Specific, measurable]
- **Failure criterion:** [Specific, measurable]
- **Owner:** [[Person]]
- **Start date:** YYYY-MM-DD
- **Decision date:** YYYY-MM-DD
```

If multiple experiments are in flight, list each separately.

If running standalone, tell the user the next step is to log the result in the Experiments Log (in the spec) once the decision date arrives, and then `dmaic-control` to lock in any gains.

---

## Common mistakes

- **No falsifiable failure criterion.** "We'll see if it helps" is not an experiment. Pin the failure condition.
- **Open-ended decision date.** "We'll keep an eye on it" means it never gets decided. Always pick a date.
- **Hypothesis without reasoning.** "Add this button → conversion goes up" — why? Without the *because*, you don't learn anything from the result.
- **Running too many experiments at once on the same metric.** When two experiments collide, you can't attribute the result to either. Sequence them or partition cleanly.
- **Skipping the log when the experiment fails.** Failed experiments are *more* valuable to log than successes — they prevent the team from re-running the same idea in 18 months. Always log.
