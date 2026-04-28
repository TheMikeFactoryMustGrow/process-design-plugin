# Metrics Design Principles

This file is bundled with the `process-design` skill. It distills the design philosophy for instrumenting processes so they can be measured, learned from, and improved over time. It draws on Working Backwards Chapter 6 (Amazon's discipline of input metrics over output metrics) and DMAIC's five-phase improvement cycle.

The core claim: a process designed without metrics produces output but cannot be improved. A process designed with metrics produces output *and* generates learning. The cost of designing measurement upfront is much lower than the cost of retrofitting it later.

---

## 1. Manage Inputs, Not Outputs

The deepest principle in the Working Backwards Metrics chapter: most output metrics are *not directly controllable*. Share price, revenue, profit — these are lagging consequences of many actions. Trying to manage to them is like steering a car by watching the rearview mirror.

What's controllable is the inputs. For Amazon: selection, price, convenience, in-stock rate. For your processes: whatever inputs the executing agent or system can directly affect. Those are the levers. Output metrics confirm the levers are working; input metrics tell you which levers to pull harder.

**Test:** For every output metric named in your spec, can you trace it to at least one controllable input metric that, if improved, would move the output? If not, the output metric is detached from action.

## 2. Four Categories of Metrics

| Category | Question Answered | When Useful |
|---|---|---|
| Output metrics | "Is the process producing what we want?" | Always; lagging confirmation |
| Controllable input metrics | "Which inputs actually move the output?" | Always; the levers you manage to |
| Agent performance metrics | "Where is the executing agent struggling?" | Surfaces ambiguity in the spec |
| Process health metrics | "Is the process operating at expected scale?" | Cycle time, cost, throughput |

A well-designed process emits metrics in all four categories. Skipping any blinds you to a class of problems.

## 3. Input Metrics Evolve

The first input metric you choose is rarely the right one. The Amazon retail team's selection metric evolved over years:

- Number of detail pages → discovered: more pages didn't mean more sales
- Number of detail page *views* → discovered: views without stock didn't help customers
- % of detail page views *with item in stock* → discovered: in-stock alone wasn't enough
- % of detail page views with item in stock *and ready for two-day shipping* → "Fast Track In Stock" — the metric that actually moved the output

The lesson: instrument the controllable inputs you suspect matter, then *let the data tell you which actually do*. The metric will refine over time as you learn which dimensions of the input correlate with output movement.

This is why the Metrics Review Plan in the spec is mandatory — it's the mechanism by which input metrics evolve from rough first guesses to the actually-correlated drivers.

## 4. Output Metrics

Restate the success criterion from the Working Backwards anchor as a measurable metric. *"The output is correct"* is not a metric; *"output quality scored ≥4 out of 5 by reviewer"* or *"every required field populated"* is.

Output metrics are necessary but not sufficient. They tell you the process worked or didn't; they don't tell you why. That's what the other three categories are for.

## 5. Controllable Input Metrics — The Levers

For each controllable input identified during Working Backwards, name the dimensions worth tracking:

- **Quality**: Is the input well-formed, complete, recent?
- **Volume**: How much of this input was provided?
- **Source**: Where did this input come from?
- **Recency**: How fresh is the input?

Instrument every controllable input even when uncertain which will matter — the point of measurement is to find out. Over many runs, the data will reveal which inputs correlate with output quality. Inputs that don't move the output get deprioritized; inputs that do become managed levers.

## 6. Agent Performance Metrics — Per Step, Always

Every step in the process emits the standard agent performance set:

- Latency
- Retry count
- Confidence/uncertainty signal
- Clarification requests (and what they were about)
- Failure events
- Unexpected-path events

This is mandatory for every step, not just decision points. The aggregate data reveals where the spec itself is unclear — if 80% of executions pause at step 4 with the same clarifying question, step 4 needs spec refinement.

This category creates a self-improvement loop: execution data feeds back into spec refinement, which improves future execution, which generates better data.

## 7. Process Health Metrics

- **End-to-end cycle time**: From input received to output produced.
- **Cost per run**: API calls, compute, human time.
- **Throughput**: Runs per unit time at steady state.
- **Parallelization efficiency**: For fan-out steps, observed speedup vs. theoretical max.

These tell you whether the process scales the way you expect, independent of whether any single run produced the right output.

## 8. Anecdotes and Exception Reporting

Numerical metrics aren't enough on their own. Two complementary mechanisms surface what numbers miss:

**Anecdotes**: Specific stories that illustrate what the metric means in practice. A 0.5% drop in customer satisfaction is abstract; the customer who tried to buy a defective product and couldn't get help is concrete. Anecdotes prevent the team from optimizing metrics that have lost connection to the underlying reality.

**Exception reporting**: Surfacing individual cases that fall outside normal patterns. Not "average latency was 2.3s" but "these 7 executions took >30s — what happened?" Exceptions are where the most valuable diagnostic information lives, but they get averaged out of summary metrics.

The spec should name where anecdotes and exceptions are captured during execution — what the build agent should log so reviewers can dig into specific cases.

## 9. Designed In, Not Retrofitted

Every step gets metrics defined *before* it survives the algorithm phase's deletion review. This ordering matters because deletion can destroy measurement points — if step 4 is the only place where input X is observable, deleting step 4 silently kills your ability to learn whether input X matters.

The deletion check becomes: *"What metrics does this step emit, and where do they go if the step is deleted?"* If the answer is "nothing," delete cleanly. If the answer names a metric, either re-instrument elsewhere before deletion or document the loss.

## 10. Implementation: Deterministic Capture

Metrics specifications in the design phase are honored by the build agent through deterministic capture mechanisms — whatever fits the build target. The principle: the executing agent or system is unreliable as a source of operational telemetry; capture must be deterministic, not discretionary.

The spec specifies *what* to measure and *where in the flow*. The build agent decides *how*, based on the target environment. The spec stays implementation-agnostic.

## 11. Distinguish Signal from Noise

Variation in data is normal. Trying to attach meaning to variations within normal bounds is at best a waste of effort, at worst dangerously misleading.

The spec's Metrics Review Plan should specify:

- **Expected variation range** for each metric (when known)
- **What constitutes signal** versus normal noise
- **Trigger conditions** that warrant investigation

Without these, every weekly review devolves into chasing 0.1% movements.

## 12. Metrics Review as a First-Class Activity

A process spec without a metrics review plan is incomplete. The plan answers:

- **Cadence**: How often is execution data reviewed against the spec?
- **Trigger conditions**: What patterns force a spec revisit (sustained agent confusion at a step, controllable input found to be irrelevant, output quality drift)?
- **Decision rights**: Who reviews and who decides on spec changes?
- **Anecdote/exception sources**: Where do specific cases live for review beyond aggregate metrics?

This makes process design genuinely iterative: design with metrics → run → review with data → redesign. This is the Control phase of DMAIC, made explicit in the spec.

---

## What These Principles Are Not

- Not a measurement system. The spec describes what to measure, not where to store the data or how to dashboard it.
- Not a statistical mandate. You don't need DOE or hypothesis testing for every workflow. The metrics phase produces the *map* of what to measure; how rigorous the analysis becomes depends on operational criticality.
- Not a substitute for output verification. Metrics tell you about the process; they don't replace checking that the output is actually correct.
