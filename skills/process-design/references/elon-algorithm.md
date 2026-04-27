# Elon's Operating Algorithm

> Source: Walter Isaacson's biography *Elon Musk* (2023). Elon calls this "the algorithm" and applies it religiously at SpaceX, Tesla, The Boring Company, and X. The order matters — most people instinctively start at step 3 or 4 and skip the steps that produce the biggest gains.

This file is bundled with the `process-design` skill so the skill works in any environment. Re-read it before each session, even if you think you remember it. The discipline is in the rigor of application, not in memorization.

---

## Step 1: Question Every Requirement

Make every requirement less dumb. Requirements come from smart people, and because they come from smart people, they are rarely questioned. But everyone is wrong some of the time. Every requirement should come attached to the name of the person who made it — not the name of a department. You should never accept a requirement from "legal" or "safety" — you need to know the specific person, because departments can't be held accountable, people can.

The requirement must make sense, and if it doesn't, it must be challenged regardless of who created it. The more senior or smart the person, the more dangerous their requirements are, because people are less likely to question them.

**Key test:** If you aren't occasionally adding back something you previously deleted, you aren't deleting enough.

## Step 2: Delete Any Part or Process You Can

If you're not adding back at least 10% of what you delete, you're not deleting enough. Every part, every step in a process should be assumed guilty until proven innocent. It's much easier to add something back than to resist the urge to include it in the first place.

People are naturally biased toward addition rather than subtraction. They want to add a step, add a check, add a sensor. The bias should be toward deletion. If you aren't sure, delete it. You can always add it back.

**Key test:** If a part or process step doesn't clearly serve the end goal, delete it. Don't keep it "just in case."

## Step 3: Simplify and Optimize

Only after you've questioned requirements and deleted what you can should you simplify and optimize what remains. The most common mistake in engineering is to optimize something that shouldn't exist. This is why steps 1 and 2 must come first.

> "Possibly the most common error of a smart engineer is to optimize a thing that should not exist."

## Step 4: Accelerate Cycle Time

Speed up every process. But only do this after you've completed steps 1–3. If you speed up a process that should have been deleted, you're just wasting resources faster. Once you've stripped down to what actually matters, then find every way to make it faster.

Move fast. Factory cycle time — from raw material to finished product — is one of the most important metrics. Every process can go faster than it's currently going.

## Step 5: Automate

This is the last step, not the first. Silicon Valley often starts here — automating processes before questioning whether they should exist. At Tesla, Elon learned this the hard way during the Model 3 "production hell" when over-automation of the Fremont factory nearly killed the company.

Only automate a process that has already been questioned, simplified, and accelerated. Automating waste just produces waste faster and makes it harder to fix.

---

## Corollaries

**All technical managers must have hands-on experience.** Managers of software teams must spend at least 20% of their time coding. Managers of any engineering team must be technically excellent. If they can't do the work, they can't manage the people doing the work.

**Comradery is dangerous.** It's natural to want to avoid challenging a colleague's work. But not questioning requirements (Step 1) because of social cohesion is how bad designs survive.

**It's OK to be wrong. It's not OK to be unconfident.** Move fast and break things applies to decision-making. Make the call, be wrong sometimes, iterate. Indecision is worse than a wrong decision.

**Never ask your troops to do something you wouldn't do.** When there's a problem on the factory floor, go to the factory floor. When there's a production crisis, sleep at the factory.

**The only rules are the ones dictated by physics. Everything else is a recommendation.**

---

## Application Notes for `process-design`

This skill is the place where comradery is most dangerous. Its job is to question the user's design, not draft what they already have in their head. If the agent finds itself nodding along and producing a spec that matches the initial description without challenging anything, it has failed the skill regardless of how clean the output looks.

Specifically:

- Step 1 is applied in Phase 2.1 of the skill (Question Requirements). Every step must be attached to a named person and a named failure mode.
- Step 2 is applied in Phase 2.2 (Delete). Track add-back ratio; aim for ~10%.
- Step 3 is applied in Phase 2.3 (Simplify). Resist the urge to simplify steps that should be deleted.
- Step 4 is applied in Phase 2.4 (Parallelize). Only after deletion and simplification.
- Step 5 (Automate) is what the *downstream* build agent does. The output of `process-design` is the spec the build agent automates from. Do not pre-automate inside the design skill.
