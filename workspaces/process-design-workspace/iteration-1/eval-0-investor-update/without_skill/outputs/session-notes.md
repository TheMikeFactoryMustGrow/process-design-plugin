# Session notes — eval-0-investor-update / without_skill

## What the user asked for
Help designing a process for the GIX quarterly investor update so that next
quarter, a Claude Code agent can do most of the work without starting from
scratch. The user described the current state as chaotic — drafting, Greg
review, back-and-forth on numbers, pulling figures from the financial model,
quality varies a lot run to run.

## My approach
I treated this as a process-design exercise where the deliverable is a
durable spec, not a one-time draft of an update. The spec has to do four
things:

1. **Codify what success looks like** so quality stops varying. → §1 of
   the runbook (success / failure criteria) and the metrics in §6.
2. **Make the chaotic bit deterministic.** The user named "pulling figures
   from the financial model" and "back-and-forth on numbers" as the
   chaos. → A figures-table step in the agent prompt (Phase C), plus a
   structured response sheet in the review loop. Both target the same
   failure mode: numerical errors leaking into Greg's review.
3. **Keep Mike's voice and judgment in the loop** without forcing him to
   start from scratch. → Mike-pass and manual-send steps, and tone
   rules in the agent prompt.
4. **Get sharper every quarter** instead of decaying. → 4-question
   post-mortem, with explicit hooks back into the spec.

I also wrote what I deliberately left out (`assumptions.md`) since I
couldn't ask the user clarifying questions.

## What I produced
Seven files in this folder:
- `00_README.md` — orientation, file map, how-to-use-next-quarter.
- `01_process-runbook.md` — the spec proper (definition, roles, inputs,
  process steps, metrics, out-of-scope).
- `02_agent-prompt.md` — paste-ready prompt for the agent next quarter,
  with eight phases and explicit gates between them.
- `03_update-template.md` — stable structure for the update doc itself,
  with eleven numbered sections.
- `04_inputs-checklist.md` — the field-level extraction list (financial
  model + ops dashboard + last quarter + Mike's notes + asks log).
- `05_review-loop.md` — structured Mike↔Greg protocol with response sheet.
- `assumptions.md` — what I assumed in lieu of being able to ask.

## Key design decisions worth flagging to a reviewer
- **The figures table is the most load-bearing piece.** It's the structural
  fix to the "back-and-forth on numbers" pain. Everything else is
  organizing tissue around that one mechanism.
- **Manual send by Mike is preserved on purpose.** Auto-send was never
  asked for and the trust cost of getting it wrong once is enormous.
- **Post-mortem is 4 questions, 10 minutes.** If it's heavier, it gets
  skipped, and the spec rots within ~2 quarters.
- **No standing skill or framework was used.** The user's prompt was
  "design a process," not "run DMAIC" or "run contract-writer," so I
  produced a process artifact directly. A DMAIC-shaped version of this
  would map cleanly: Define = §1, Measure = §6, Analyze = the metric
  bands and review-loop "what to watch for," Improve = the figures
  table + response sheet, Control = the post-mortem. The user can run
  the dmaic skill against this spec next time if they want that lens.

## Time spent
~25 min: ~5 min reading the brief and shaping the artifact set, ~15 min
writing, ~5 min wiring it together with the README and the assumptions
file.
