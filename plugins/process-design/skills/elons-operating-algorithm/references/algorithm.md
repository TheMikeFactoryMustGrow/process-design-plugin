# Elon's Operating Algorithm

> Source: Walter Isaacson, *Elon Musk* (2023). The canonical vault note is `Values and Mechanisms/Elon's Operating Algorithm.md`. This file is bundled with the `elon-pressure-test` skill so the skill works in any environment, and so the algorithm survives even if the vault note is unavailable.
>
> **Re-read this file at the start of every pressure test, even if you think you remember the steps.** The discipline lives in the rigor of application, not in memorization. Most failures of this skill come from agents skipping ahead to step 3 because steps 1 and 2 felt like they'd already been done.

---

## Step 1: Question Every Requirement

Make every requirement less dumb. Requirements come from smart people, and *because* they come from smart people, they are rarely questioned. But everyone is wrong some of the time. Every requirement should come attached to the name of the person who made it — not the name of a department. You should never accept a requirement from "legal" or "safety" or "the team" — you need to know the specific person, because departments can't be held accountable, people can.

The requirement must make sense, and if it doesn't, it must be challenged regardless of who created it. The more senior or smart the person, the more dangerous their requirements are, because people are less likely to question them.

**Test:** If you aren't occasionally adding back something you previously deleted, you aren't deleting enough.

**Failure mode this catches:** Inherited assumptions that nobody is willing to own.

## Step 2: Delete Any Part or Process

If you're not adding back at least 10% of what you delete, you're not deleting enough. Every part, every step in a process, every story on a roadmap, every box on an architecture diagram should be assumed guilty until proven innocent. It is far easier to add something back than to resist the urge to include it in the first place.

People are biased toward addition rather than subtraction. They want to add a step, add a check, add a sensor, add a safeguard. The bias should run the other way. If you aren't sure, delete it. You can always add it back.

**Test:** Does this part / step / story clearly serve the fitness metric? If not, delete. Don't keep it "just in case." Don't keep it because it's already in the doc. Don't keep it because someone smart wrote it down.

**Failure mode this catches:** Keeping work because it exists, not because it's needed.

## Step 3: Simplify and Optimize

Only after you've questioned requirements and deleted what you can should you simplify and optimize what remains. The most common engineering failure is to optimize something that shouldn't exist. This is why steps 1 and 2 must come first.

> "Possibly the most common error of a smart engineer is to optimize a thing that should not exist."

**Failure mode this catches:** Beautiful, fast, well-tested implementations of things that should have been deleted in step 2.

## Step 4: Accelerate Cycle Time

Speed up every process. But only do this after you've completed steps 1–3. If you speed up a process that should have been deleted, you're just wasting resources faster. Once you've stripped down to what actually matters, find every way to make it faster.

Move fast. Factory cycle time — from raw material to finished product — is one of the most important metrics. Every process can go faster than it's currently going.

**Failure mode this catches:** Premature optimization for throughput before the throughput question has been settled.

## Step 5: Automate

This is the last step, not the first. Silicon Valley often starts here — automating processes before questioning whether they should exist. At Tesla, Elon learned this the hard way during the Model 3 "production hell" when over-automation of the Fremont factory nearly killed the company.

Only automate a process that has already been questioned, simplified, and accelerated. Automating waste produces waste faster and makes it harder to fix.

**Failure mode this catches:** Building robust automation around a process that, in retrospect, should have been deleted.

---

## Corollaries

These aren't part of the 5-step algorithm but Elon names them as load-bearing companion principles. They show up most often in the *meta-question* phase of a pressure test — the moment when you ask whether the artifact's framing itself is wrong.

**All technical managers must have hands-on experience.** Managers of software teams must spend at least 20% of their time coding. Managers of any engineering team must be technically excellent. If they can't do the work, they can't manage the people doing the work.

**Comradery is dangerous.** It's natural to want to avoid challenging a colleague's work. But not questioning requirements (Step 1) because of social cohesion is how bad designs survive. **This is why this skill exists** — an LLM agent has no comradery to defend, so it can question things a human teammate would let slide.

**It's OK to be wrong. It's not OK to be unconfident.** Make the call, be wrong sometimes, iterate. Indecision is worse than a wrong decision. Pressure tests should produce decisive verdicts, not equivocal "consider whether"s.

**Never ask your troops to do something you wouldn't do.** When there's a problem on the factory floor, go to the factory floor.

**The only rules are the ones dictated by physics. Everything else is a recommendation.**

---

## Application notes for `elon-pressure-test`

This skill is the place where comradery is most dangerous. Its job is to question the user's artifact, not to validate the user's existing intent. If the agent finds itself nodding along — "yes, this roadmap looks reasonable, here are some minor optimizations" — it has failed the skill regardless of how clean the output looks.

Specifically:

- **Phase 0 — Fitness metric.** Without one, deletions are aesthetic. Refuse to enter Step 1 until the metric is named.
- **Step 1.** Every surviving requirement must trace to a named person. "The team", "operations", "legal" → loop back. Track which requirements were promoted from "needs harder questioning" back to "survives" — that's your add-back log feeder.
- **Step 2.** Track add-back ratio. Aim for ~10%. Zero deletions = under-deleted; loop back. 100% deletion = you didn't read the artifact carefully.
- **Step 3.** The most common failure is simplifying something that should have been deleted. Before each simplification, restate why this thing survived Step 2.
- **Step 4.** Don't accelerate what wasn't simplified.
- **Step 5.** Automation is downstream — flag where automation should *eventually* live, but don't recommend automating in the same pressure test that just survived its first deletion pass.
