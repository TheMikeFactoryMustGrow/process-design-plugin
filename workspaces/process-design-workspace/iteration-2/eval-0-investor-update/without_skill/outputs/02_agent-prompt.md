# Agent Prompt — GIX Quarterly Investor Update

Paste this as the first user message in a fresh Claude Code session, started
from the GIX project working directory.

---

You are drafting the GIX quarterly investor update for the quarter that just
closed. Mike Lingle (CEO of GIX, fiber infrastructure) is the user. The
primary reviewer on the investor side is Greg Nugent.

Before you write anything, do the following in order. Do NOT skip ahead.

## Phase A — Read the spec
Read these files (absolute paths) end to end:
1. `01_process-runbook.md` — the process you are executing.
2. `03_update-template.md` — the structure of the output.
3. `04_inputs-checklist.md` — the figures you must extract.
4. `05_review-loop.md` — the review protocol.
5. The most recent prior quarter's update (Mike will give you the path).
6. The most recent post-mortem entry, if `06_post-mortems.md` exists. Pay
   particular attention to "what we will do differently this quarter."

After reading, respond with: a one-paragraph summary of what you understood,
and then the structured questions in Phase B.

## Phase B — Ask Mike for the inputs (structured, not open-ended)
Ask exactly these questions, as a numbered list. Do not improvise extras.

1. What is the absolute path to the current financial model?
2. What is the absolute path to the operations dashboard / current KPI sheet?
3. What is the absolute path to your running notes folder for this quarter?
4. What is the absolute path to the prior quarter's update?
5. Is there an outstanding-investor-asks log? If yes, path. If no, state
   "none" and note any commitments you remember from last quarter.
6. Anything Greg specifically asked for in last quarter's review that we need
   to address this quarter? (One sentence per item.)
7. Is there material this quarter that Mike does NOT want sent to the
   investor list, even though it's in the model or dashboard? (Confidential
   M&A talks, personnel issues, etc.) List them; the agent will exclude.
8. What is the target send date? (Default: 21 days post-close.)

Wait for answers before doing anything else.

## Phase C — Extract figures
Open the financial model and the ops dashboard. Pull every figure listed in
`04_inputs-checklist.md`. Build a "figures table" in a scratch markdown file
at `./scratch/figures-table-Q[N]-[YEAR].md` with columns:

| Figure | Value | Unit | Source file | Source cell/row | Notes |

Do not invent figures. If a figure listed in the checklist isn't in the
sources, mark it `MISSING` and ask Mike where to find it before drafting.

When the table is complete, present it to Mike and ask him to spot-check
three rows. Wait for confirmation before drafting.

## Phase D — Draft v0
Write the update against `03_update-template.md`. Rules:
- Every number in the draft must appear in the figures table. If you want to
  use a number that isn't there, stop and add it to the table first.
- Mirror the tone of the prior update (read it again before drafting).
- Bad news first in each section. Good news without adjectives.
- No marketing language. No "we are excited to announce." Investors hate it.
- Length target: 1500–2500 words. Brevity is a feature.
- If you don't know something, say "we don't yet have visibility on X" and
  flag it in a comment for Mike. Do not paper over gaps.

Output the draft as a Google Doc in the GIX investor-updates folder, named
`GIX Investor Update — Q[N] [YEAR] — DRAFT v0`.

## Phase E — Iterate with Mike
Mike reads v0, comments inline. Apply his edits, produce v1. If Mike's edits
are large enough that you're rewriting more than ~15% of the doc, stop and
ask whether the inputs were wrong or the spec is wrong. Don't just keep
patching.

## Phase F — Send to Greg
Use the protocol in `05_review-loop.md`. When Greg returns comments, apply,
produce v2, get Mike's sign-off.

## Phase G — Distribution package
Export PDF. Draft the cover email (≤ 6 sentences) into Mike's drafts folder.
Do NOT send. Mike sends manually.

## Phase H — Post-mortem
Within 3 days of send, run the four-question post-mortem from §5 step 7 of
the runbook. Append to `06_post-mortems.md`. Propose concrete edits to the
runbook, the template, or the inputs checklist if the post-mortem surfaces
them.

---

When you're ready, start with Phase A.
