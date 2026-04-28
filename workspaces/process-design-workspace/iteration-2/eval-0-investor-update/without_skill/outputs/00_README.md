# GIX Quarterly Investor Update — Process Spec

This folder is the durable spec for the quarterly investor update Mike sends to Greg
Nugent (and any other GIX investors on the list). It is designed so that next
quarter, a Claude Code agent can read this folder, ask Mike a small number of
targeted questions, pull the rest from named source-of-truth files, and produce a
draft that is 80%+ ready for Greg's review.

## Files in this folder, and when to read them

1. `01_process-runbook.md` — the spec itself. Read this first. Defines the
   process, inputs, outputs, roles, success/failure criteria, metrics, and the
   regression guard. This is the single source of truth for "how the quarterly
   update gets made."

2. `02_agent-prompt.md` — the prompt to paste into a fresh Claude Code session
   when starting next quarter's update. The agent reads the runbook plus
   `04_inputs-checklist.md` and then drives the work.

3. `03_update-template.md` — the structural template the update follows every
   quarter. Stable structure → easier comparison quarter over quarter →
   easier for Greg to skim.

4. `04_inputs-checklist.md` — concrete list of source artifacts (financial model,
   prior update, ops dashboards, etc.), with the field-level detail the agent
   needs to extract from each. This is what makes "pull figures from the
   financial model" deterministic instead of chaotic.

5. `05_review-loop.md` — the Mike↔Greg review loop, captured as a small protocol
   so revision rounds don't drag.

6. `assumptions.md` — what I assumed in writing this spec, since I couldn't
   ask. Read this if anything in the spec looks off — it's likely an
   assumption that needs correcting.

7. `session-notes.md` — one-pager describing what this session produced and
   how I approached it. For the human reviewer of this design exercise.

## How to use this next quarter

In a Claude Code session at the GIX project root (or wherever the financial
model + prior updates live):

1. Open `02_agent-prompt.md` and paste it as the first user message.
2. Answer the agent's clarifying questions (the prompt forces it to ask
   structured questions, not open-ended ones).
3. Review the draft. Send to Greg using the protocol in `05_review-loop.md`.

When the cycle finishes, run the "post-mortem" step at the bottom of
`01_process-runbook.md` to update this spec. The spec is supposed to get
sharper every quarter.
