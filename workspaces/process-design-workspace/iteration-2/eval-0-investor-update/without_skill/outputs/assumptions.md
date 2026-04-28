# Assumptions made while writing this spec

Because this was a one-shot design with no back-and-forth, I made the
following assumptions. If any are wrong, they're the first thing to fix.

## About the company and the update

1. **GIX is in the build-and-light phase of a fiber infrastructure rollout.**
   So the core operational metrics are homes passed, customers connected,
   take rate, ARPU, churn, and CapEx burn. If GIX is past that phase (e.g.
   pure operate-and-monetize) or still pre-launch, §2 of the template
   needs different rows.

2. **The investor list is small enough that a written quarterly update
   makes sense** (vs a SEC-style filing, vs a quarterly call). A single
   Google Doc + cover email is the right artifact.

3. **Greg Nugent is one of several investors, but the most active reviewer.**
   I designed for him as primary reviewer because the user described him
   that way, but the doc goes to the full list. If Greg is the only
   investor, §9 (asks of investors) is overscoped.

4. **There is a financial model and an ops dashboard.** Most fiber cos
   have both — but the names, locations, and exact KPI definitions are
   GIX-specific. The agent prompts Mike for paths each quarter rather than
   hard-coding them.

5. **No public reporting obligations** (private company, no 10-Q
   equivalent). If there are, the spec needs a compliance review step
   before send.

## About the agent's environment

6. **The agent has access to Google Drive (or the local mirror) so it can
   read/write Google Docs and the financial model.** If not, the agent
   produces markdown drafts and Mike pastes them into Drive. Either is
   fine — the spec doesn't depend on the integration.

7. **The agent runs in a Claude Code session at a known project root** —
   probably something like `~/code/gix` or a Drive-mounted path. The
   `02_agent-prompt.md` is written assuming the agent can read absolute
   paths Mike provides.

## About the user's working style

8. **Mike wants to keep voice and final judgment.** The spec puts him in
   the loop at Step 4 (his pass) and Step 6 (manual send) for that reason.
   It does NOT auto-send.

9. **Mike doesn't want to babysit the agent.** The spec is structured so
   the agent runs end-to-end with clear gates, asks structured questions
   (not open-ended), and only stops when it actually needs Mike.

10. **Mike values the post-mortem step** — given the stated goal of "I want
    this to get better, not the same chaos every quarter." If post-mortems
    feel like overhead, the spec degrades by Q3. I made the post-mortem 4
    questions and 10 minutes for that reason. It's the smallest thing
    that still works.

## Things I deliberately did NOT do

- I did not specify exact SLAs in business hours vs calendar days beyond
  the 21-day target. Real fiber companies have construction crews running
  on weekends; "business days" gets ambiguous. Calendar days is cleaner.

- I did not write the post-mortem template as a separate file. It's 4
  questions and lives at §5 step 7 of the runbook. A separate file is
  unnecessary surface area until there are 4+ entries.

- I did not embed any actual GIX numbers, market names, or investor
  names beyond Greg. The spec is the durable artifact; instances are
  per-quarter.

- I did not design a "how to onboard a new agent to this process" doc —
  `00_README.md` does that job. If onboarding gets harder than reading
  the README, the spec has bloated.
