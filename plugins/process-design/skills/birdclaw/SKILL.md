---
name: birdclaw
description: >
  Read and analyze your OWN X/Twitter data from the local birdclaw workspace. birdclaw
  (https://birdclaw.sh) keeps your timeline, mentions, bookmarks, likes, and DMs in a local
  SQLite database with full-text search; this skill drives its CLI to pull a slice as JSONL and
  then analyze it three ways: a plain-language overview (birdclaw's native AI digest), targeted
  extraction (full-text search + filtering), or an adversarial pass (hands the JSONL to the
  qa-agents sibling skill to stress-test a take, thread, or draft before you post). Use when the
  user says "what's in my mentions", "summarize my timeline", "what did I bookmark about X",
  "analyze my X inbox", "what are people saying to me on Twitter", "digest my X day/week", or
  "red-team this thread before I post". SCOPE: your own account data only — birdclaw cannot fetch
  arbitrary public tweets, other users' histories, or topic firehoses; if the user wants those,
  say so plainly and do not pretend otherwise.
compatibility: >
  Requires the birdclaw CLI on PATH (`brew install steipete/tap/birdclaw`), an initialized
  workspace (`birdclaw init` + an imported Twitter archive to establish identity), and — for the
  digest and ranked-inbox features — OPENAI_API_KEY in the environment. The adversarial analysis
  mode additionally requires subagents (Task tool) for the qa-agents handoff. Python 3 is needed
  for the bundled pull.py helper. All reads are local SQLite; live refresh (`--sync`) needs
  birdclaw's configured X transports.
version: 0.1.0
---

# birdclaw — Read & Analyze Your Own X Data

This skill turns your local [birdclaw](https://birdclaw.sh) workspace into an analyzable data
source. birdclaw archives **your own** X/Twitter world — timeline, mentions, bookmarks, likes,
DMs — into local SQLite with FTS5 search and exports it as JSONL. This skill drives that CLI and
routes the result into the right kind of analysis.

> **Scope guard, read first.** birdclaw operates on *your* account data. It can sync your home
> timeline, mentions, likes, bookmarks, and DMs through your authenticated X transports — it
> **cannot** scrape arbitrary public tweets, pull another user's full history, or watch a topic
> firehose. If the user asks for any of those, tell them plainly that this tool can't do it
> rather than returning partial or invented results.

---

## When to use

Use this skill when the user wants to understand or act on their own X data:

- "What's in my mentions / inbox?" → ranked inbox or mentions slice
- "Summarize my X day / week" → native digest
- "What did I bookmark about <topic>?" → search over bookmarks
- "Find my tweets about <topic>" → full-text search
- "Red-team this thread before I post" → adversarial analysis via qa-agents

Do **not** use it for competitor analysis, sentiment over arbitrary accounts, or scraping public
timelines — birdclaw can't reach that data.

---

## Preconditions

Verify before doing anything else. If a precondition fails, stop and tell the user how to fix it
— do not fabricate data.

1. **CLI present** — `command -v birdclaw`. If absent: `brew install steipete/tap/birdclaw`.
2. **Workspace initialized** — `birdclaw init` has been run and a Twitter archive imported
   (`birdclaw archive find --json` then `birdclaw import archive --json`). The archive establishes
   account identity; live syncs refresh slices on top of it.
3. **OPENAI_API_KEY** set in the environment — required only for the digest and ranked-inbox
   modes. Search and raw export work without it.

---

## Procedure

### Step 1 — Confirm scope and pick a slice

Restate what the user wants in terms birdclaw can serve, and name the slice:
`timeline`, `mentions`, `bookmarks`, `likes`, or a `search` query. If the request is out of
scope (arbitrary public tweets), say so and stop.

### Step 2 — Pull the data as JSONL

Use the bundled helper, which wraps `birdclaw ... --json` defensively and normalizes the
envelope to one JSON object per line. Add `--sync` to refresh live data first.

```bash
# Refresh + pull the last 100 timeline items
python3 scripts/pull.py timeline --sync --limit 100 --out ./birdclaw-timeline.jsonl

# Bookmarks mentioning a topic
python3 scripts/pull.py search --query "local-first" --bookmarked --hide-low-quality --out ./bm.jsonl

# Mentions only
python3 scripts/pull.py mentions --sync --limit 50 --out ./mentions.jsonl
```

The helper prints a one-line JSON summary (`{"slice","count","path"}`) and exits non-zero with a
clear message if birdclaw is missing (2), a command failed (3), or args are bad (4). Surface that
message to the user; never paper over it.

You may also call birdclaw directly when the helper doesn't fit — the canonical commands are:

```bash
birdclaw sync timeline --limit 100 --refresh --json
birdclaw sync bookmarks --mode auto --all --json
birdclaw search tweets "query" --limit 100 --json
birdclaw search tweets --bookmarked --hide-low-quality --json
birdclaw inbox --score --hide-low-signal --limit 8 --json
```

`--json` envelopes go to stdout; progress and warnings go to stderr.

### Step 3 — Analyze (pick the mode that matches the ask)

**A. Overview / summary → birdclaw's native AI digest.** Don't re-summarize by hand when
birdclaw already does it well:

```bash
birdclaw today              # today's digest
birdclaw digest week --json # structured weekly digest
birdclaw inbox --score --hide-low-signal --limit 8 --json  # ranked inbox
```

Read the JSON and report the highlights. Requires `OPENAI_API_KEY`.

**B. Targeted extraction → read the JSONL directly.** For "find/count/group" asks, operate on the
JSONL from Step 2 — filter, count, pull representative rows, quote real tweets verbatim with their
IDs. Cite what's actually in the data; if a field is missing, say so.

**C. Adversarial pass → hand off to qa-agents.** When the user wants a take, thread, or draft
*stress-tested* ("is this take wrong?", "red-team this before I post", "poke holes in my thread"),
pass the JSONL (or the draft text) to the **qa-agents** sibling skill. qa-agents runs the
Finder/Auditor/Referee loop and a root-cause pass — far tougher than a plain read. Frame the
artifact for it (e.g. "the claims in these tweets" or "this draft thread") and let it score.

### Step 4 — Report

Lead with the answer. Quote real rows with their tweet IDs so the user can verify. State the
slice, the row count, and whether data was live-synced or read from cache. If you hit a
precondition failure or an out-of-scope request, say that instead of guessing.

---

## Composition

- Feeds **qa-agents** for adversarial analysis of your own posts/threads/takes (Step 3C).
- The JSONL it emits is git-friendly and can be tracked over time; pair with **dmaic** if you
  want to measure something about your posting cadence or inbox signal as a recurring review.

## Honesty rules

- Never invent tweets, counts, or sentiment. Every claim traces to a `birdclaw --json` row.
- Never imply you reached data outside the user's own account.
- If `OPENAI_API_KEY` is missing, do the non-AI modes (search/extract) and say the digest is
  unavailable rather than faking a summary.
