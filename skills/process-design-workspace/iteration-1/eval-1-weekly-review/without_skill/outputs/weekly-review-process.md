# Weekly Review — Process Specification

**Owner:** Mike Lingle
**Cadence:** Weekly, Friday 3:00–3:45 PM (45-minute hard stop)
**Version:** 1.0 (2026-04-27)
**Status:** Active

---

## 1. Purpose (the one-line job-to-be-done)

> Each Friday, produce a written, scored snapshot of where every active workstream stands so I can detect drift one week earlier than I would by gut feel, and start Monday with a ranked, not-vibes top-3 focus list.

**Success looks like:** I can hand last quarter's reviews to a stranger and they can tell you what I was working on, what was stuck, and whether I was getting better — without asking me a question.

**Failure looks like:** I skip it, OR I do it but a month later I can't remember what I decided last Friday, OR the focus list I wrote on Friday isn't what I actually worked on Monday.

---

## 2. Scope

**In scope:** All active workstreams across the portfolio. Current set (review and prune monthly):

1. **GiX Fiber** (operations, growth, infra)
2. **Wasson Enterprise** (deals, portfolio, team)
3. **Linglepedia / knowledge-graph** (vault hygiene, governance)
4. **Claude plugins & agent projects** (dmaic, qa-agents, process-design, etc.)
5. **Beancount stack** (finance-dashboard, bean-counter)
6. **Tracked Presentation Sharing** (gix-investor-deck → multi-tenant)
7. **Personal/health/relationships** (one tracked block, not a project list)

**Out of scope:** Daily standups, project-internal standups, journaling, planning meetings with team. This is *the personal operator-level review*, not a team ceremony.

---

## 3. Inputs (gather before you sit down)

The review depends on these being in arm's reach. If they aren't, the review degrades into recall, which is the failure mode you're trying to leave.

| Input | Source | Auto/manual |
|---|---|---|
| Calendar last 7 days | Google Calendar | auto |
| Closed PRs / commits | `gh` across active repos | auto |
| Asana tasks closed this week | Asana | auto |
| Open scheduled tasks | `mcp__scheduled-tasks__list` | auto |
| Inbox-zero status | Gmail counts | auto |
| Linglepedia vault deltas | git log on `~/Documents/Linglepedia` | auto |
| Last week's review file | Obsidian vault | manual link |
| The 3 commitments you made *to yourself* last Friday | Last review's "Next week top-3" | manual link |

A small fetch script (see §8) pulls the auto rows into a draft so you don't waste review time gathering.

---

## 4. The Review — fixed agenda, 45 min hard stop

Run in order. Each section has a time budget. If you blow the budget, you write *"OVER — by X min"* and move on. The point is consistency, not perfection.

### Section A — Context refresh (5 min)
- Open last week's review.
- Read your "Next week top-3" out loud.
- Score each: **Done / Partial / Not done / Abandoned-with-reason.**
- Hit-rate this week = (Done + 0.5 × Partial) / 3. **Track this.** It's metric #1.

### Section B — What shipped (10 min)
For each workstream in §2, write **one line per shipped thing**, no more.
- Format: `[workstream] verb-led outcome — link/evidence`
- "Shipped" means: a customer, teammate, or system other than you experienced the change. Internal notes, drafts, and "thinking about it" don't count.
- If a workstream has zero shipped lines two weeks running, that's a yellow flag — note it.

### Section C — What's stuck (10 min)
For each workstream, list anything that has been **on your plate ≥ 14 days without movement**. Format:
- `[workstream] thing — stuck because <one cause> — unblocker: <person / decision / artifact> — age: N days`

Rule: if you can't name a specific unblocker, the item is mis-framed. Spend 60 seconds reframing it or kill it.

### Section D — Drift check (5 min)
Three questions, written answers, each ≤ 2 sentences:
1. **Effort vs. intent.** Where did my time go this week vs. where I said it would go? Name the biggest delta.
2. **Energy.** Which workstream drained me? Which gave me energy? (One word each is fine.)
3. **The one I'm avoiding.** What did I dodge this week? Name it.

### Section E — Next week top-3 (10 min)
Pick exactly **3** outcomes for next week. Not 5, not 7. Three.
- Each must be an **outcome**, not an activity. ("Theresa removes WAF rule" not "follow up with Theresa.")
- Each must have a **definition of done** you can check on Friday.
- Each must be tied to a workstream from §2.
- If two of the three are in the same workstream, you are concentrating — flag it intentionally or rebalance.

### Section F — Closeout (5 min)
- Save file as `weekly-review-YYYY-MM-DD.md` in the vault.
- Score the review itself on the rubric in §5.
- Drop the 3-line summary into the next-Monday calendar event titled "Top-3 — week of YYYY-MM-DD".

---

## 5. Metrics — what makes this measurable

Three terminal metrics. Track all three, every week, in a single row of a sheet (`weekly-review-metrics.csv`). Drift shows up as a trend across these, not as one bad week.

### Metric 1 — Top-3 Hit Rate
- **Definition:** (Done + 0.5 × Partial) / 3, computed in Section A.
- **Range:** 0.00 – 1.00
- **Healthy band (green):** ≥ 0.66 (2 of 3 done)
- **Yellow:** 0.34 – 0.65
- **Red:** ≤ 0.33, OR red two weeks running at any level
- **Why this metric:** It's the only number that catches "I plan well but don't execute" AND "I execute well but plan the wrong things." A persistent low score means one of those two; the drift-check field tells you which.

### Metric 2 — Stuck-Item Age (P50 and Max)
- **Definition:** Across all items listed in Section C, the median age in days and the max age in days.
- **Healthy band:** P50 ≤ 21 days, Max ≤ 45 days
- **Yellow:** P50 ≤ 30, Max ≤ 60
- **Red:** anything older, OR same item appearing red 3 weeks in a row (compounding drift)
- **Why this metric:** Stuck items are the leading indicator of portfolio drift. A growing P50 means you're accumulating, not closing.

### Metric 3 — Review Hygiene Score (self-graded, 0–4)
Score the review itself on this rubric, every week:
- +1 if you held the 45-minute hard stop
- +1 if every Section C item has a named unblocker
- +1 if every Section E item has a definition of done
- +1 if you actually answered "the one I'm avoiding" with something concrete
- **Healthy band:** ≥ 3
- **Yellow:** 2
- **Red:** ≤ 1, or skipped review entirely (score = 0)
- **Why this metric:** This is the meta-metric — it measures whether the *process* is working, independent of outcomes. If outcomes are bad but hygiene is high, the issue is upstream (strategy / capacity). If hygiene is bad, fix the process first.

### What to do with the numbers
- Plot all three monthly. Look for trends, not single-week spikes.
- Quarterly: review the trend lines and decide if §2 (scope), §4 (agenda), or §5 (metrics) need to change. **Do not edit the process inside a quarter** — that's how you avoid the "I keep redesigning the system instead of running it" trap.

---

## 6. Triggers — when a metric trips, what happens

| Condition | Action | Owner | When |
|---|---|---|---|
| Top-3 hit rate red 2 weeks in a row | Run a 30-min root cause: planning quality vs. execution capacity. Write findings as a note in vault. | Mike | Within 7 days |
| Same stuck item red 3 weeks running | Force a kill/escalate/delegate decision. No fourth week of the same item. | Mike | This Friday's review |
| Hygiene score ≤ 1 | Skip next week's *review content* and instead re-read this spec, fix what broke. The process IS the work that week. | Mike | Next Friday |
| Skipped review entirely | Log the skip with reason in metrics sheet. Two skips in a row = the spec is wrong; revise. | Mike | Next available Friday |
| All three metrics green for 8 consecutive weeks | Tighten thresholds by one notch (e.g., hit rate green ≥ 0.75). Process should keep getting harder as you get better. | Mike | Quarterly review |

---

## 7. Anti-patterns to watch for

These are the failure modes most likely to creep back in. Name them so you can spot them.

1. **The retrospective sprawl.** Section B becomes a 30-line journal. Cap it. One line per shipped thing. Period.
2. **Aspirational top-3.** You write three things you wish were true instead of three things you'll actually do. The hit-rate metric punishes this within two weeks.
3. **Stuck-item amnesia.** You "forget" to list something that's been stuck for 6 weeks because it's embarrassing. Cross-check Section C against the previous 4 weeks' Section C — items only disappear via Done or Killed, never by silence.
4. **Process porn.** You spend 90 minutes redesigning the template instead of doing the review. Lock the spec for a quarter. Edits queue up to the quarterly review.
5. **The Friday-afternoon-tired skip.** Move it earlier in the day if Friday afternoon energy is consistently bad. Don't move it off Friday — the weekly cadence is the load-bearing piece.

---

## 8. Tooling — what to automate, what to leave manual

**Automate (build once, save 10 min/week):**
- A `weekly-review-prep.sh` that runs Friday 2:30 PM and produces a draft `.md` with: closed PRs, calendar dump, Asana closed tasks, vault git log, last week's top-3 pre-loaded into Section A. Saves to vault.
- A `weekly-review-metrics.csv` append step at end of Section F that takes the three scores and adds a row.

**Leave manual (cognitive load is the point):**
- The drift-check questions (Section D). Writing forces thinking.
- The top-3 selection (Section E). Automating this would defeat the purpose.
- The hygiene self-score. The act of grading is the regression guard.

---

## 9. First four weeks — onboarding the process

Don't try to land at green from week 1. The plan:

- **Week 1:** Run the spec exactly as written. Expect hygiene = 2, hit rate uncalibrated. Goal: just complete it.
- **Week 2:** Same. Now you have a previous top-3 to score against.
- **Week 3:** First real metric trend visible. Don't change anything yet.
- **Week 4:** Retrospective on the process itself. Edit §2 (scope) if a workstream is wrong. Lock the rest.
- **Week 5+:** Run for a full quarter without spec edits. Then revisit.

---

## 10. Connection to your existing systems

- **DMAIC:** This spec IS a DMAIC artifact. Define = §1, Measure = §5, Analyze = §6, Improve = future iterations on the metrics, Control = the weekly cadence + quarterly review-of-review.
- **Linglepedia:** Each weekly review is a note in the vault, tagged `#weekly-review`, linked to the workstreams it touches. The MOC is `[[weekly-reviews-MOC]]`.
- **QA agents pattern:** After every quarterly spec edit, spawn a QA agent to challenge the new thresholds. Don't grade your own homework on process changes.
