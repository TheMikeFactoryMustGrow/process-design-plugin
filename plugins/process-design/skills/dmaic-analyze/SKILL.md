---
name: dmaic-analyze
description: Run only the Analyze phase of the Six Sigma DMAIC cycle as a standalone building block — for each metric in a process spec, set thresholds (green/yellow/red bands or trigger values), enumerate the 3–5 most common failure modes, and define the first action plus owner when a threshold trips. Use when the user explicitly wants the Analyze step in isolation (e.g., "just help me set thresholds for these metrics", "build an investigation playbook for this process", "do the Analyze phase only"), OR when another skill (such as the `dmaic` orchestrator) calls this phase à la carte. If the user wants the full cycle, prefer the `dmaic` orchestrator instead. Output is an Analyze block ready to drop into a DMAIC spec. This is the phase that turns passive dashboards into actionable triggers.
---

# DMAIC — Analyze Phase

Two jobs, in order: (1) **Causal chain** — for every output metric, name the controllable input(s) that move it. (2) **Per-output thresholds + playbooks** — when an output goes red, what's the first action and who runs it. Without (1), you have dashboards no one can act on; without (2), you have action items no one runs.

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

An Analyze block with two parts: (1) a **causal-chain table** mapping each output metric to the controllable inputs that move it (and the external inputs that bound the relationship); (2) per-output **threshold + playbook** blocks.

---

## Procedure

### 1. Confirm Measure produced the three categories

If the Measure block has only outputs and no controllable input metrics, **stop**. Without controllable inputs the causal chain has no targets — go back to Measure and add the levers. Run `dmaic-measure` if needed.

### 2. Draw the causal chain

For each output metric, name:
- **Controllable inputs that move it** (1+ required — the spec is incomplete without). Drawn from the Controllable Input Metrics block in Measure.
- **External inputs that bound the relationship** (0+, but usually at least 1 — context that limits how much the lever can move the output).

Render as a table:

```markdown
| Output Metric | Controllable Inputs | External Inputs (bounds) |
|---|---|---|
| onboarding_completion_rate | step1_form_completion_rate, time_to_first_response | seasonal_signup_volume, product_uptime |
| revenue_retention | success_rep_touchpoints, renewal_discount_rate | macroeconomic_environment |
```

Run `dmaic.py check-causal-chain --file <spec> --strict` to verify every output has a traced lever. Exit non-zero blocks promotion.

### 3. For each output, set thresholds + playbook (parallelizable)

Per-output work is MECE — when Task fan-out is available, spawn one subagent per output for steps 3a–3c. Sequential fallback otherwise.

**3a. Threshold.** Pick the style that fits the metric:
- **Banded (most common):** red ≤ baseline / yellow ≤ midpoint / green ≥ target. Define ranges.
- **Trigger value:** a single number that demands investigation when crossed.
- **Rate of change:** the trajectory matters more than the level (e.g., "drops > 10% week-over-week").

Tie bands to Define: if green can coexist with the failure sentence being true, the threshold is wrong.

**3b. Known failure modes (3–5).** Drawn from the controllable + external inputs in the causal chain. The failure modes are *which input failed and how*, not generic "process drift." Examples: "step1_form_completion_rate dropped because we changed copy on Tuesday"; "macroeconomic_environment shifted; expected to recover when X". If the user has zero failure-mode knowledge yet (brand-new process), state that and note the modes will accumulate as incidents do.

**3c. First action when threshold trips.** Concrete, owned, time-bounded:
- **Owner:** single named person ([[Wikilink]]). "The team" doesn't show up — `dmaic.py validate-owner` rejects it.
- **First step:** a specific action ("open dashboard X, filter to segment Y, screenshot the spike"), not a goal ("investigate").
- **Document in:** specific note / ticket / file. Investigations not written down don't compound.
- **Time-to-resolve target:** e.g. 24h for red, 1 week for yellow.
- **Escalation:** time-based ("not resolved in 4h") or scope-based ("affects > 1 customer").

### 4. Stress-test

- **Causal coverage:** every output traces to ≥1 controllable input. (`check-causal-chain` enforces.)
- **Yellow with consequence:** a Yellow band you can ignore is too wide — tighten or remove.
- **Action small enough:** the first step the on-call person can do in minutes. If it needs a meeting, it's too big — decompose.
- **Failure-mode overlap:** if the same failure mode shows up under multiple outputs, the metrics overlap — go back to Measure.

---

## Output format

Use `dmaic.py scaffold --phase analyze --metrics N` to emit the causal-chain table + per-output threshold blocks. Agent fills the placeholders.

If running standalone, the next step is `dmaic-improve` (when there's something to fix) or `dmaic-control` (to design the regression guard).

---

## Common mistakes

- **No causal chain.** The headline failure mode. Spec lists outputs and thresholds, owner has to guess which input to move when red. Always draw the table first.
- **Output traces to no controllable input.** Spec is incomplete — go back to Measure and add the missing lever. `check-causal-chain --strict` catches this.
- **Thresholds untied to Define.** Bands set "because they look right" instead of derived from the success/failure sentences.
- **Action too vague.** "Investigate the issue" is not an action. "Open the latency dashboard, filter to the affected region, screenshot the spike" is an action.
- **No owner.** A first action with no named human is a first action that doesn't happen.
- **No time-to-resolve.** Without an SLA, "first action" stretches indefinitely.
- **Failure modes copied from a template.** If the user can't tell a story about each one happening to *this* process, it's not real. Cut it.
