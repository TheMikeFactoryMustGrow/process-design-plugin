# Review loop — Mike ↔ Greg

The historical pain in this process is the back-and-forth on numbers between
Mike and Greg. The fix has two parts. Part 1 is upstream: the figure
extraction in Phase C of the agent prompt, which kills most numerical
errors before they reach Greg. Part 2 is the review protocol below, which
keeps the rounds bounded.

## The protocol

### Round 1 — Mike sends to Greg
- Subject: `GIX Q[N] [YEAR] update — draft for your review`
- Body: 4 sentences max. Link to the Google Doc. Note the target send
  date. Ask Greg for comments by a specific date (default: 5 business days).
- The doc has a "Methodology" comment thread pinned at the top, with a
  link to the figures table. Greg can click any number to see its source.
  This is the single biggest quality lever — Greg can verify a number in
  10 seconds instead of asking Mike.

### Greg's pass
Greg leaves comments. Mike does not respond inline. The agent collects
comments into a single response sheet at the bottom of the doc, with three
columns: Greg's comment, Mike's resolution, status (Accepted / Discussed /
Declined with reason).

### Round 2 — Mike's response
Mike reviews the response sheet, edits in bulk, sends Greg a single message:
"Updated. Response sheet at the bottom of the doc shows how I handled each
comment. OK to send?"

This is the structural change. Previously the back-and-forth was
unstructured — every comment was its own thread, and a single misread
caused a third or fourth round. With a single response sheet, Greg sees all
resolutions at once and signs off (or doesn't) in one pass.

### Round 3 — Greg signs off (or not)
If Greg signs off, Mike moves to distribution. If Greg pushes back on a
specific resolution, Mike either accepts the push-back or records his
override in the response sheet with a one-sentence reason. The override is
a feature, not a bug — Mike is the CEO, Greg is one investor. But every
override is logged, so a pattern of overrides on the same topic surfaces.

## What to watch for

- **>2 rounds with Greg, two quarters running** → the inputs checklist is
  wrong, or the template is missing a section Greg cares about. Update the
  spec, don't keep grinding.
- **Greg flags a number as wrong after Mike's spot-check passed** → the
  spot-check sample is too small. Increase from 3 to 5 figures next
  quarter.
- **Greg's comments are mostly stylistic** → fine. The agent prompt's tone
  rules can be tightened in the post-mortem.
- **Greg's comments are mostly substantive (e.g. "you're missing X
  context")** → §5 / §6 / §7 of the template are too thin. Expand.

## Cover email (Mike sends after sign-off)

Drafted by the agent, sent by Mike. Template:

> Subject: GIX Q[N] [YEAR] investor update
>
> All —
>
> Q[N] update attached and linked. [One-sentence headline — same one as in
> §1 of the doc.]
>
> [If there are asks: one sentence with the ask. Otherwise omit.]
>
> Happy to discuss any of this — reply or grab time on my calendar.
>
> Mike

That's it. No marketing. The doc does the work.
