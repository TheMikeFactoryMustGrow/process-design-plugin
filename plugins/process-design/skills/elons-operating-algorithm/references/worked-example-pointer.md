# Worked example: Bean Counter Architecture Pressure Test

The canonical worked example for this skill lives in the Linglepedia vault at:

`VEGA/Architecture/Bean Counter - Architecture Pressure Test.md`

It was written by hand in March 2026 as a pressure test of the Bean Counter architecture note. It is the reason this skill exists — it demonstrated that disciplined application of the algorithm produces real, surprising compression (a 20-story roadmap → 8 stories, a months-long blocking prerequisite chain unblocked).

## Why study it before running this skill

If you're an agent invoking the skill for the first time in a session, **read the Bean Counter pressure test before generating output**. Specifically pay attention to:

1. **The fitness metric.** Bean Counter's was "time-to-reliable-monthly-close." Notice how every verdict in every table can be traced back to that metric. That's the discipline.
2. **The structure of section 1.2 ("Requirements That Need Harder Questioning").** Each row attaches the requirement to a named source (a doc, a person, a date), states a specific challenge, and lands a specific verdict. Vague rows don't appear.
3. **Section 2.1 ("Candidates for Deletion").** The verdicts use a small consistent vocabulary (DELETE, DEFER, DECOUPLE, SIMPLIFY) — that's the same vocabulary in `verdicts.md`.
4. **Section 1.3 ("The deepest question").** "Is this a build, or a configuration?" — a single reframe that recast the entire roadmap. Every pressure test should produce one of these.
5. **The "What survives deletion" list.** Concrete and numbered. The compressed deliverable, not a summary of changes.

## Patterns to copy

- Tables for verdicts; prose only for "the deepest question" and "what survives" framing.
- Pull-quotes at the top of each step, drawn from the algorithm.
- Surviving-component lists are numbered, not bulleted — they're the deliverable, not options.
- Add-back log lives at the end. The Bean Counter test doesn't have an explicit one (this skill formalizes that section), but the deletions-that-came-back are inline in the survivors list.

## Patterns NOT to copy mechanically

- The Bean Counter test runs ~412 lines. **Do not pad to length.** A pressure test of a one-paragraph idea should be one screen, not 412 lines. The discipline is consistency of structure, not consistency of size.
- The Bean Counter test was authored without a structured "Open questions" section; this skill adds one because pressure tests almost always surface things that need a real human follow-up. Always include it.
- The Bean Counter test's "method" line is `autoresearch-inspired pressure test`. New pressure tests use `Elon's Operating Algorithm pressure test` for searchability — the autoresearch framing was specific to that document.
