---
name: dmaic-define
description: Run only the Define phase of the Six Sigma DMAIC cycle as a standalone building block — pin down what a process is supposed to do, what success looks like, and what failure looks like, in three concrete sentences. Use when the user explicitly wants the Define step in isolation and not the full DMAIC cycle (e.g., "just help me write the success and failure sentences", "do the Define phase only"), OR when another skill (such as the `dmaic` orchestrator) calls this phase à la carte. If the user wants the full cycle from problem framing through regression guard, prefer the `dmaic` orchestrator instead. Output is a Define block ready to drop into a DMAIC spec.
---

# DMAIC — Define Phase

Pin down purpose, success, and failure in three concrete sentences. Everything downstream depends on this.

---

## When to use

- "Define this process for me"
- "What does success look like for [process]?"
- "Help me spec out [thing] before I start measuring it"
- "DMAIC define for [process]"
- Called by `dmaic` orchestrator or any other skill that needs a Define block

---

## What this skill produces

A Define block — three sentences plus the process name and owner — formatted to drop into a DMAIC spec note (see the `dmaic` orchestrator for the full spec template).

```
**What this process is supposed to do:** [one sentence]
**What success looks like:** [observable end state]
**What failure looks like:** [equally observable]
```

---

## Procedure

### 1. Get the subject

Ask only if not already specified: "What process, system, or idea are we defining?"

### 2. Get the owner

"Who is accountable for this?" Person, role, or team. If unknown, mark as `TBD` and flag that an owner needs to be named — a process without an owner is a process nobody will improve.

### 3. Draft the purpose sentence

> **What is this process supposed to do?**

One sentence. Concrete. No marketing language. No adjectives doing heavy lifting ("seamless", "world-class", "best-in-class" — banned).

Bad: *"Deliver a world-class onboarding experience to new customers."*
Good: *"Get a new customer from contract signature to first successful login in under 7 days."*

### 4. Draft the success sentence

> **What does success look like?**

A future scene, not an adjective. If you read this in six months, you should be able to look at the world and say "yes, this is happening" or "no, it isn't."

Bad: *"Customers are happy."*
Good: *"95% of new customers complete their first successful login within 7 days of contract signature, without contacting support."*

### 5. Draft the failure sentence

> **What does failure look like?**

The most diagnostic sentence in Define. If you can't write it, your success sentence is too vague — push back to step 4.

Bad: *"Customers are unhappy."*
Good: *"More than 10% of new customers either fail to log in within 30 days or open a support ticket during onboarding."*

### 6. Stress-test the three sentences

Ask:
- Could two reasonable people read these and disagree about whether the process is working? If yes, sharpen them.
- Are success and failure phrased symmetrically? They should describe the same axis from opposite ends.
- Is the time horizon explicit? ("Within 7 days," "within a quarter," "per month.") Vague time horizons make every metric ambiguous.

---

## Output format

Return a Define block in this shape, ready for the DMAIC spec:

```markdown
## Define

**Process:** [Name]
**Owner:** [[Person or Role]]

**What this process is supposed to do:**
[Sentence]

**What success looks like:**
[Sentence]

**What failure looks like:**
[Sentence]
```

If running standalone (not invoked by the orchestrator), tell the user this is the Define block and that the next step is `dmaic-measure` to design the metrics.

---

## Common mistakes

- **Starting too abstract.** "Improve customer experience" is a wish, not a process. Push for the most specific scope the user is actually accountable for.
- **Conflating purpose and metric.** "Increase NPS by 10 points" is a target, not a purpose. Purpose is what the process does in the world; metric is how you know.
- **Skipping failure.** Most people resist writing failure explicitly. Don't let them — failure is what makes success measurable.
- **Owner = "the team".** A team doesn't have a calendar reminder. Push for a single accountable person, even if execution is shared.
