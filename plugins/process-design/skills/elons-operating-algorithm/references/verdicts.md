# Verdict Vocabulary

These are the standard verdicts used in the pressure-test tables. Use them consistently — readers learn the vocabulary once and can scan the output fast. If you find yourself wanting a 7th verdict, you probably mean one of these in disguise.

| Verdict | When to use | Effect on the artifact |
|---|---|---|
| **KEEP** | Requirement / part / step clearly serves the fitness metric and traces to a named person. Survived hard questioning. | Stays in the compressed deliverable as-is. |
| **QUESTION** | The thing might be needed, but the *justification* on file is weak, vague, or department-attributed. Not deleted yet — but the burden is now on whoever wants to keep it to attach a person and a justification. | Stays for now. Re-evaluate in the next pressure test. Owner must reply by a named date. |
| **DECOUPLE** | The thing is real, but it's been wired up as a *prerequisite* for something else when it shouldn't be. Most common: integration with a not-yet-built system listed as blocking the build of an independent thing. | Stays — but the dependency edge gets removed. Build proceeds without it. |
| **DEFER** | Justified eventually, but not in the current scope. Often a future-tense capability ("multi-tenant", "ML categorization", "intercompany elimination") that's been written into Phase 1 when it belongs in Phase 3. | Removed from current scope. Lands in a Future Considerations section with a trigger condition for revisiting (e.g. "when volume > N", "when X exists"). |
| **DELETE** | No clear path from this thing to the fitness metric. Or the thing optimizes something that shouldn't exist. Or it's automation of a process that hasn't been simplified yet. | Removed entirely. Goes into the Add-back Log only if it gets reinstated later in this same pressure test. |
| **SIMPLIFY** | The thing is needed but is overspecified — too many tiers, too many phases, too many trust levels, too many config options for a v1. | Stays in compressed form. Note the simpler shape explicitly (e.g. "5-level trust model → 2-level"). |

## Decision rules

- A row that trips two verdicts (e.g. could be DEFER or DELETE) takes the *more aggressive* of the two. The whole point of the algorithm is the bias toward subtraction. Add it back if you regret it.
- KEEP without an attached named person → not actually KEEP. Loop back to Step 1.
- DEFER must come with a trigger condition. "Defer indefinitely" = DELETE.
- DECOUPLE must come with the specific edge being removed. "Decouple from the rest of the system" is too vague.
- SIMPLIFY must name the simpler shape explicitly. "Simplify the trust model" is not a verdict; "Reduce trust model from 5 levels to 2" is.

## Anti-patterns to refuse

- **"Refactor"** — too vague to be a pressure-test verdict. Pick SIMPLIFY (with the new shape) or DELETE.
- **"Investigate"** — also too vague. Investigation is fine elsewhere; in a pressure test, it means you didn't make the call. Either ask a real question with a deadline (QUESTION) or pick a verdict.
- **"Maybe"** — Elon's corollary: it's OK to be wrong, not OK to be unconfident. Pick a verdict; you can always be wrong.
- **"It depends"** — fine in a footnote, not as a verdict. State the dependency as a QUESTION addressed to the named person.
