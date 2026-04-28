# Process Runbook: GIX Quarterly Investor Update

## 1. Definition (what this process is)

**Purpose.** Produce a written quarterly update from GIX (fiber infrastructure
company; Mike Lingle, CEO) to its investor list — primary recipient Greg Nugent
— covering the prior fiscal quarter's operational, financial, and strategic
state, plus the outlook on the next quarter and any asks of investors.

**Cadence.** Once per quarter. Target: send within 21 calendar days of
quarter close. The 21-day clock starts the day after quarter end.

**Owner.** Mike (CEO) is accountable. The Claude Code agent is the executor for
drafting, figure extraction, and revision tracking. Greg is the primary reviewer
on the investor side.

### Success looks like
A single Google Doc (or PDF derived from it) that:
- Hits every section in `03_update-template.md`.
- Every number in the doc is traceable to a named cell/row in the financial
  model or a named row in the ops dashboard. No orphan numbers.
- Greg's review produces ≤ 1 round of substantive numerical corrections (i.e.
  Mike isn't fixing the same kind of error he fixed last quarter).
- Sent to the full investor list within 21 days of quarter close.
- Tone is calm, specific, and factual. Bad news is named first; good news
  doesn't need adjectives.

### Failure looks like
- Sent later than 35 days post-close, OR
- Greg flags a number as wrong on the second pass (means the figure-extraction
  step is broken, not just a typo), OR
- Mike rewrites the draft from scratch instead of editing the agent's output
  (means the spec didn't capture his voice / the inputs were wrong), OR
- An investor has to ask "what about X?" where X is one of the standing topics
  in the template.

## 2. Roles

| Role | Who | Responsibility |
|------|-----|----------------|
| Owner | Mike | Final sign-off, voice, judgment calls on what to disclose. |
| Drafter | Claude Code agent | Pulls inputs, drafts update, tracks revisions, sends. |
| Primary reviewer | Greg Nugent | First investor read; catches numerical / framing issues. |
| Distribution list | Investor list (Mike maintains) | Final recipients. |

## 3. Inputs (source-of-truth files)

The agent must read these before drafting. See `04_inputs-checklist.md` for the
field-level extraction list.

1. **Financial model** — current quarter actuals + forward forecast. Mike to
   confirm path each quarter (it moves around). Numbers in the update MUST
   come from here, not be retyped from elsewhere.
2. **Prior quarter's investor update** — for continuity, "what we said we'd do
   vs what we did," and to mirror tone/structure.
3. **Operations dashboard** — homes passed, take rate, ARPU, churn, OpEx,
   construction milestones. Whatever GIX uses as the live ops doc.
4. **Outstanding investor asks/commitments log** — anything Mike promised the
   investor list last quarter that needs an answer this quarter.
5. **Anything the board saw this quarter** — board decks, board meeting
   minutes. The investor update should never contradict what the board got.
6. **Mike's running notes for this quarter** — wins, scares, hires, losses,
   regulatory items. Mike maintains; the agent prompts for the path.

## 4. Output

**Primary:** Google Doc, named `GIX Investor Update — Q[N] [YEAR]`, in the GIX
investor folder on Drive. Structure follows `03_update-template.md`.

**Secondary:** PDF export, attached to a short cover email to the investor
list.

## 5. Process steps (the loop the agent runs)

Step by step, with the gate that has to pass before moving on:

### Step 1 — Locate inputs
Agent confirms paths to all six inputs in §3. **Gate:** all paths confirmed,
all files accessible. If anything is missing, agent stops and asks Mike.

### Step 2 — Extract figures
Agent pulls every figure listed in `04_inputs-checklist.md` from the financial
model and ops dashboard into a small "figures table" at the top of its working
notes. Each figure is annotated with the cell/row it came from. **Gate:** Mike
spot-checks 3 figures against the source. If any is wrong, the extraction step
is rerun before drafting begins. (This is the step that historically caused
back-and-forth — fixing it here saves a round with Greg.)

### Step 3 — Draft v0
Agent writes the full draft against `03_update-template.md`, using only
figures from the figures table. **Gate:** every number in the draft has a
matching entry in the figures table.

### Step 4 — Mike's pass
Mike reads v0 end to end, edits in-doc. Voice, judgment calls, what to
disclose. Agent applies the edits and produces v1. **Gate:** Mike approves v1
to go to Greg.

### Step 5 — Greg's pass
v1 goes to Greg with the protocol in `05_review-loop.md`. Greg returns
comments. Agent applies, produces v2. **Gate:** Greg approves OR Mike
overrides on a specific point with a recorded reason.

### Step 6 — Distribution
Agent exports to PDF, drafts the cover email, places both in
Mike's drafts folder. **Mike sends manually** — distribution is not delegated,
because the send action is the moment Mike personally vouches for the content.

### Step 7 — Post-mortem (small, 10 min)
Within 3 days of sending, Mike + agent answer four questions and append the
answers to `06_post-mortems.md` (created on first run):
1. What was wrong in the draft that we fixed in Mike's pass? (→ improve the
   prompt or the template.)
2. What was wrong that Greg caught? (→ improve the inputs checklist or the
   figure-extraction step.)
3. How long did each step take? (→ track the cycle-time metric.)
4. Anything in the spec wrong / out of date? (→ edit this runbook.)

The spec is supposed to get sharper every quarter. If post-mortem is skipped,
the process will drift back to chaotic within ~2 quarters.

## 6. Metrics (the regression guard)

Three metrics, tracked in the post-mortem log. If any goes red two quarters
in a row, this runbook needs a rework — not just a tweak.

| Metric | Definition | Green | Yellow | Red |
|--------|------------|-------|--------|-----|
| Cycle time | Days from quarter close to send | ≤ 21 | 22–35 | > 35 |
| Numerical correction rounds | Distinct rounds where Greg or Mike flags a wrong number | 0 | 1 | ≥ 2 |
| Mike's edit volume in Step 4 | Approx % of draft Mike rewrites (not just edits) | ≤ 15% | 16–35% | > 35% |

## 7. Out of scope

This spec does NOT cover:
- Annual letters / year-end reviews (different artifact, different cadence).
- 1:1 investor emails outside the quarterly cycle.
- Board materials (separate process; the investor update derives from board
  materials, not the other way around).
- Press releases or external comms.

If Mike wants any of those covered, write a sibling runbook — don't bolt it
onto this one.
