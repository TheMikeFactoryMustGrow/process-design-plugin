# Session notes — weekly-review process design

## Approach

The user asked for a measurable, consistent weekly review. They explicitly named the failure modes: uneven quality, intuitive (= unrepeatable), can't spot drift. That's a process-design problem with a clear shape: turn a fuzzy ritual into a spec with metrics, an agenda, and a regression guard.

I leaned on the user's existing context (visible in MEMORY.md):
- They already use DMAIC, so I framed the deliverable as DMAIC-compatible (Define / Measure / Analyze / Control all show up explicitly in §10 and the metric structure).
- They already run QA agents on changes — referenced as the regression check on quarterly spec edits.
- They already use Linglepedia — the review file is a vault note with an MOC.
- They have a real workstream list (GiX, WE, Linglepedia, plugins, Beancount, tracked-presentation, personal) — I baked those into §2 rather than leaving generic placeholders.

## Key design decisions and assumptions

1. **Three metrics, not seven.** Hit rate (planning vs. execution), stuck-item age (portfolio drift), hygiene self-score (process drift). Each catches a distinct failure mode. The hygiene meta-metric is the load-bearing piece for "spot when I'm drifting" — it isolates process failure from outcome failure.

2. **45-minute hard stop, not 30–60.** A range is what produced uneven quality in the first place. Picked 45 as the midpoint and made it a hygiene criterion. The user can move it after a quarter if data says otherwise.

3. **Friday afternoon assumed but flagged.** User said Friday; I kept Friday but called out moving earlier in the day as the only allowed adjustment if energy data argues for it. Did not assume a specific time other than 3:00 PM as a reasonable default.

4. **Top-3, exactly three.** Not "3–5". The hit-rate metric only works if the denominator is fixed. Caps planning sprawl.

5. **Onboarding plan (§9) explicit.** Most weekly-review processes die in week 2 because users compare week 1 to a fictional gold standard. The four-week ramp tells them not to.

6. **Quarterly lock.** Spec edits queue to a quarterly review. This is the regression guard — without it, the user will tweak the template every Friday and never run a stable process. Calls out "process porn" as an anti-pattern by name.

7. **What to automate vs. leave manual.** Inputs are automated (saves 10 min/week, removes the activation-energy excuse to skip). Drift-check, top-3 selection, and hygiene grading are deliberately manual — they're where the cognitive work lives.

## What I produced

- `weekly-review-process.md` — the spec itself, ~10 sections, ready to live in the vault
- `weekly-review-template.md` — the fillable Friday-afternoon form, derived from the spec
- `weekly-review-metrics.csv` — single-row schema for trending the three metrics over time
- `session-notes.md` — this file

## What I did not do (and why)

- Did not build the `weekly-review-prep.sh` automation. It's referenced in §8 as future work; user can build it once the process is running and the inputs stabilize. Building it now would over-fit to a process that hasn't been validated.
- Did not set up the Obsidian MOC, scheduled task, or calendar event. Those are environmental setup the user will do once they decide to commit. The artifacts are designed so they can.
- Did not run a QA-agents pass on the spec. It's the user's tool; they should run it themselves on first quarterly revision per their own pattern.
