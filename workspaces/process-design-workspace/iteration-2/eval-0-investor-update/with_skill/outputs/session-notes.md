# Session Notes — GIX Investor Update Process Design

**Process slug:** `gix-investor-update`
**Build target:** `claude-code`
**User:** Mike Lingle
**Date:** 2026-04-27

---

## Phase 1 — Working Backwards

### 1.1 Output
- **Concrete output:** A finalized quarterly investor update document (Google Doc + email-ready prose) covering the prior quarter's GIX (Gigabit Internet Xchange / gixfiber.com) operating, financial, and strategic results, sent to investors.
- **Success criterion:** (a) Greg Nugent (lead investor reviewer) approves with ≤2 rounds of edits, AND (b) all financial figures match the source-of-truth financial model in Linglepedia, AND (c) sent within 30 days of quarter close.
- **Failure modes:**
  - Greg sends 3+ rounds of edits → too many ambiguous/sloppy claims, agent draft was thin.
  - Numbers mismatch financial model → trust loss with investors.
  - Sent late (>45 days from quarter close) → cadence break, investor confidence erodes.
- **Consumers:** GIX investors (Greg + ~6 others). Greg is gatekeeper; rest are downstream readers.

### 1.2 Inputs

**Assumption (logged):** The financial model lives in Linglepedia (likely `~/Documents/Linglepedia/`) as a structured note or linked spreadsheet. Exact path deferred to build agent.

| Input | Source | Controllable? | Format | Validation |
|---|---|---|---|---|
| Financial model figures | Linglepedia financial-model note (or linked GSheet) | Partially (we control update cadence and structure, not the underlying numbers) | Numbers in named cells / YAML fields | Latest as-of date is within current quarter; all referenced fields populated |
| Operating highlights | Mike's notes, Slack threads, ops dashboard | Yes | Free text bullets | At least 3 highlights named with concrete numbers |
| Strategic narrative ("the story this quarter") | Mike's head, then articulated | Yes | Prose paragraphs | Articulates one through-line; cites at least one operating or financial fact |
| Prior quarter's letter | Linglepedia / Drive | Yes (we choose to reference or not) | Markdown / Doc | Exists, dated within last 100 days |
| Greg's prior feedback | Email thread, comments on prior doc | Yes (we choose to incorporate or not) | Email / comments | Captured in writing somewhere we can re-read |

### 1.3 Constraints
- **Timing:** within 30 days of quarter close (target), ≤45 days (hard).
- **Cost:** mostly Mike's time; agent should reduce that to <2 hours of review.
- **Quality bar:** Greg's bar — clear, no fluff, concrete numbers, strategic clarity.

### 1.4 Existing process (intuited)
1. Mike drafts something (chaotic, varies)
2. Mike pulls financial figures (from financial model — manually, error-prone)
3. Send to Greg
4. Greg reviews; back-and-forth on numbers and prose
5. Revise; re-send for final
6. Send to all investors

Minimum path derivation: collect-inputs → draft → fact-check-numbers → Greg-review → revise → send. The current chaos is in step "draft" (no template, varies) and step "fact-check" (manual lookups, error-prone).

### 1.5 Build target
**Claude Code** — Mike wants a Claude Code agent to do most of it next quarter.

### Gate 1
- Output is noun: yes (a finalized update document) ✅
- Output concrete: yes ✅
- ≥1 controllable input named: yes (operating highlights, strategic narrative) ✅
- Every input has validation: yes ✅
- Build target specified: yes ✅
**Gate 1 passes.**

---

## Phase 2 — Metrics Design

### 2.1 Output Metrics
- `letter.greg_edit_rounds` — count of revision cycles before Greg approves. Target: ≤2.
- `letter.numbers_match_model_pct` — % of cited financial figures that match the financial model exactly. Target: 100%.
- `letter.days_from_quarter_close` — days between quarter end and send. Target: ≤30.

### 2.2 Controllable Input Metrics
| Input | Dimensions | Captured at |
|---|---|---|
| Operating highlights | quality (concreteness: % with specific numbers), volume (count), recency (days old) | input-collection step |
| Strategic narrative | quality (single through-line: yes/no), volume (paragraph count) | drafting step |
| Prior letter | source (used / not used), recency | input-collection step |
| Greg's prior feedback | volume (count of prior comments incorporated), source (which prior letter) | input-collection step |

### 2.3 Agent Performance Metrics
Standard performance metrics on every step (latency, retry count, confidence, clarification requests, failures, unexpected paths).

Step-specific additions:
- Fact-check step: number of figures checked, number of mismatches found, source-of-truth lookup count.
- Greg-review step: number of comments received, number of comments accepted vs. rejected.

### 2.4 Process Health Metrics
- End-to-end cycle time (input collection start → final send)
- Cost per run (agent tokens + Mike's review time minutes)
- Throughput (target: 4/year, one per quarter)

### 2.5 Anecdote / Exception Capture
- **Anecdotes:** capture every quarter's full draft → final diff, plus Greg's comments verbatim.
- **Exceptions:** any figure mismatch, any cycle taking >45 days, any round count >3.

### Gate 2
- All four categories have entries ✅
- Every controllable input has ≥1 dimension ✅
- Output metrics testable ✅
- Anecdote/exception capture named ✅
**Gate 2 passes.**

---

## Phase 3 — Apply the Algorithm

### 3.1 Question Every Requirement
| Step | Trace | Owner | Metrics emitted | Mark |
|---|---|---|---|---|
| Collect operating highlights | controllable input → output | Mike | input quality | ✅ |
| Pull financial figures | financial model → output (numbers) | Mike (decider), build agent (executor) | fact-check signals | ✅ |
| Draft using template | inputs → prose → output | Build agent | draft latency, confidence | ✅ |
| Fact-check numbers against model | numbers → trust → success | Build agent | mismatch count | ✅ |
| Greg review | judgment → output quality | Greg | edit_rounds | ✅ |
| Revise per Greg | feedback → output | Build agent | retry count | ✅ |
| Send to all investors | output → consumers | Mike | terminal | ✅ |
| (Pre-existing in chaos) "Mike polishes prose unnecessarily" | doesn't move controllable input → output once draft is there and fact-checked | Mike | nothing | 🚩 |
| (Pre-existing in chaos) "Multiple back-and-forth on numbers with Greg" | symptom of bad fact-check, not a step | — | — | 🚩 (as a step; underlying cause is the missing fact-check gate) |

### 3.2 Delete
- **Proposing to delete:** "Mike polishes prose unnecessarily" — once the draft passes fact-check and follows the template, additional prose polish before Greg sees it adds latency, not quality. Greg is the polish-quality reviewer; doing his job before he sees it is wasted work. Metrics consequence: none lost (this step emitted nothing). **Accepted.**
- **Proposing to delete:** "Multiple rounds of number-fixing with Greg" — this is the chaos. Replace with an explicit fact-check gate before Greg sees the draft. Numbers must match the model 100% before review. Metrics consequence: `numbers_match_model_pct` becomes a gate, not an output metric. **Accepted (replaced with gate, not deleted as concept).**

Add-back ratio: 0/2 = 0 (vacuous; no deletions added back). Sanity check passes.

### 3.3 Simplify
- Combine "collect operating highlights" and "collect strategic narrative" into one input-collection step with two named sub-inputs. Simpler, same metrics.
- Reorder: fact-check happens before Greg sees the draft, not after. This is the structural fix to the chaos.

### 3.4 Parallelize
- Input collection (highlights, narrative, prior letter, prior feedback) is parallelizable — four independent reads.
- Drafting depends on all inputs → sequential.
- Fact-check is sequential after drafting.

### Gate 3
- All deletion proposals explicitly accepted ✅
- Metrics impact named ✅
- Every surviving step has owner + failure mode (filled in spec) ✅
- Add-back ratio: 0 ≤ 0.30 ✅
**Gate 3 passes.**

---

## Phase 4 — Probe for Gaps

**Phase 4 mode: `inline_simulation`** — Task tool not available in this runtime. Sub-types 4.1–4.4 ran sequentially in this same context. Adversarial isolation between sub-types is partial; treat 4.5 integration as lower-confidence than a real fan-out pass.

### 4.1 Input stress-testing (Agent A — inline)
| Input | Missing | Malformed | Boundary | Adversarial |
|---|---|---|---|---|
| Financial model | Quarter not yet closed → no figures | Figures present but stale (last update >30 days) | Quarter just closed; some numbers are preliminary | Numbers were updated mid-draft, draft references stale snapshot |
| Operating highlights | Mike forgets to provide | Vague ("we did good things"), no numbers | Only 1–2 highlights, thin quarter | Conflicting highlights from different sources (Slack vs. ops dashboard disagree) |
| Strategic narrative | Mike has no through-line this quarter | Multiple competing narratives | Last quarter's narrative still applies; nothing new | Narrative contradicts a fact in the operating highlights |
| Prior letter | Doesn't exist (first quarter) | Exists but heavily edited post-send | Sent <30 days ago; little to compare | Prior letter made a forecast we missed — deal with it explicitly or not? |
| Greg's prior feedback | None captured | Captured but in a Slack thread, not searchable | One-line "lgtm" — no substance | Feedback contradicts itself across rounds |

### 4.2 Decision rule stress-testing (Agent B — inline)
| Decision | Resolves on input alone? | Two agents same branch? | Boundary | Ambiguous |
|---|---|---|---|---|
| Fact-check pass/fail | Yes (numbers match model exactly: yes/no) | Yes | Rounding: model has 3 decimals, draft has 1 — match? Decision: round consistently to 1 decimal in letter, but verify against full-precision model | Numbers match but units differ ("$1.2M" in letter vs "1,200,000" in model) — normalize before compare |
| Greg approval | Judgment | Greg is the human; only one branch reaches this | Greg says "fine, send" — counts as approve | Greg sends partial feedback ("I'll have more later") — block or proceed? Decision: block. |
| Send to investors | Yes (Greg approved AND fact-check passed AND within window: yes/no) | Yes | At day 44, partial Greg approval — escalate to Mike | Greg unreachable for >7 days — escalate to Mike for go/no-go |

### 4.3 Failure-mode probing (Agent C — inline)
- Drafting fails partway → partial draft saved; resume from next bullet.
- Fact-check fails → loop back to draft revision with explicit list of figures that mismatched. Bounded retry: 3 attempts, then escalate to Mike.
- Greg unresponsive >7 days → escalate to Mike, who decides to send anyway or extend.
- Send fails (email bounce, Drive permission) → retry once, then surface to Mike.
- Financial model unreachable → log degraded mode; do not silently proceed without numbers.

### 4.4 Missing-step probing (Agent D — inline)
- Assumes Mike has already collected inputs. Add explicit "input-collection trigger" step (calendar reminder 5 days after quarter close).
- Assumes Greg's email/comment thread is parseable. Add explicit "parse Greg's feedback" step that extracts comments and pairs them with sections.
- Implies handoff: who archives the final letter? Add archival step (save to Linglepedia + Drive folder).
- Missing observability: where does each input metric land? Add: write to a `gix-investor-updates/<YYYY-Qn>/metrics.json` log per run.
- Missing: explicit pre-send checklist (subject line, recipients, attachments). Add as part of send step.

### 4.5 Metrics coverage probing
With the above gaps:
- Add a tracked dimension `freshness` to financial model input (days since last update) — surfaces 4.1's malformed-financial-model case.
- Add `narrative_through_line` boolean metric (one through-line: yes/no) — surfaces 4.1's malformed narrative.
- Add `feedback_round_count` metric to Greg-review step — already present.
- Add `fact_check_mismatch_count` metric — already present.

### Gate 4
- All 4 stress-test sub-types performed ✅
- Every input stress-tested across four dimensions ✅
- Every decision rule stress-tested ✅
- New gaps reflected in spec sections ✅ (will be in draft)
**Gate 4 passes.**

---

## Phase 5 — Verification Suite

### 5.1 Diagram type
**Choice: `flowchart`** — branches and a loop (Greg revision cycle), no persistent dwelling state. Sequence diagram tempting (multiple actors) but the actors aren't exchanging messages; they're reaching decisions. Flowchart fits.

### 5.2 Verification suite checks
Standard set from spec-principles + process-specific:

| Check | Type | Method |
|---|---|---|
| Every step has named requirement owner | structural | script |
| Every decision rule testable on input alone | semantic | agent |
| Every input has validation | structural | script |
| Metrics Map has all four categories | structural | script |
| Every controllable input has ≥1 tracked dimension | structural | script |
| Every diagram step node has owner annotation | structural | script |
| Every gate has named verification method | structural | script |
| Successor IDs all exist | structural | script |
| ≥1 terminal state reachable | structural | script |
| No unreachable non-terminals | structural | script |
| No unbounded loops | structural | script |
| Output is noun, concrete | semantic | agent |
| Spec matches design intent | semantic | agent |
| **Process-specific:** Fact-check gate appears before Greg-review step | semantic | agent |
| **Process-specific:** Send step has pre-send checklist criteria | semantic | agent |
| **Process-specific:** Bounded retry on fact-check loop (no unbounded loop on fact-check) | structural | script (covered by unbounded-loop check) |

### Gate 5
- Diagram type chosen with justification ✅
- Verification suite enumerates checks ✅
- Each check classified ✅
**Gate 5 passes.**

---

## Phase 6 — Draft

Draft written to disk at `outputs/gix-investor-update.process-spec.md` with `status: draft`. First Gate 6 run revealed one structural failure:

- `All step ID references in Procedure resolve` failed because `sent_terminal` and `aborted_terminal` were referenced via `→` but only declared in the Terminal States section, not as numbered Procedure entries. The `verify_spec.py` regex extracts step IDs from Procedure-numbered bullets only and only allows the literal tokens `Terminal`, `End`, `terminal`, `end` as implicit successors.
- This is NOT a verifier quirk per the anti-pollution Drafting Principle — the spec genuinely declares semantic terminals, and the right design fix is to declare them as Procedure entries 9 and 10 (with no successors). Doing so is a real design improvement: terminals are now first-class steps with owners, failure modes, and metrics participation, instead of dangling labels.
- Fix applied. Gate 6 re-ran clean: 32/32 passed.

### Verifier quirks logged
- None. The one failure was a real design completeness gap, not a parsing quirk.

### Gate 6 result: PASS (32/0).

### Soft fails through Phase 6: 0

---

## Phase 7 — Verify Adversarially

**Phase 7 mode: `inline_simulation`.** First attempted the real path: invoked `Skill(qa-agents:qa-agents)` with the prescribed args string. The qa-agents skill loaded and printed its protocol, but its operating model requires three isolated `Task` subagents and the Task tool is not available in this runtime (confirmed via `ToolSearch` for `select:Task` returning no matches). Per SKILL.md Phase 7, fell back to inline simulation: ran Finder → Auditor → Referee with role-discipline in this same context, saving each as JSON to `outputs/qa-agents-gix-investor-update/{finder,auditor,referee}.json`.

**Adversarial isolation collapsed.** A Verification Record note has been added to the spec body recording this — a downstream reader sees the simulation note without consulting these session notes. Per the SKILL.md Phase 7 contract:

> Phase 7 simulation note: qa-agents skill not reachable; finder/auditor/referee simulated inline. Adversarial isolation collapsed. Treat findings as lower-confidence than a real qa-agents pass; re-run Phase 7 against this spec from a runtime with subagent capability before treating the spec as production-grade.

### Findings synthesis

| ID | Sev | Title | Auditor | Referee | Routed to | Resolution |
|---|---|---|---|---|---|---|
| F1 | 5 | Greg-approval criterion uses 'equivalent unambiguous OK' (judgment, not input-alone) | ACCEPT | n/a | Phase 6 (drafting fix to a decision rule) | Replaced with enumerated approval-token set |
| F2 | 5 | Day-44 partial-approval edge case unspecified | DISPROVE (conf 6) | UPHOLD-DISPROOF | n/a | No spec change; case is caught at gate_greg_approval one step earlier |
| F3 | 1 | comments_accepted_pct may be vanity in isolation | ACCEPT, weakest_flag | WEAK | Watch-item | Added to Assumptions as 4-run watch-item; not a blocking fix |
| F4 | 5 | Late-stage model amendment after fact-check has no re-check | ACCEPT | n/a | Phase 4 (missing edge case) | Added freshness re-check at pre_send_checklist; new edge-case row |
| F5 | 1 | Sparse-but-real quarter routes to escalation as if broken | DISPROVE (conf 5) | UPHOLD-FINDING | Phase 4 | Added quiet-quarter edge-case row + quiet_quarter metric flag |
| F6 | 5 | Internal contradiction: success says ≤2 rounds; gate escalates at >=2 | ACCEPT | n/a | Phase 6 / Phase 1 boundary | Reconciled gate boundary to `> 2`; success criterion (≤2) is honored |
| F7 | 5 | gate_pre_send method=agent but includes a human sub-check (Mike approval) | ACCEPT | n/a | Phase 5 (verification-check) | Split into gate_pre_send_agent (script) + gate_pre_send_human (human) |
| F8 | 5 | escalate_to_mike has open-ended successor with no enumerated legal targets | ACCEPT | n/a | Phase 6 (drafting fix) | Enumerated 5 legal resume targets; any other instruction rejected |

**Score line.** Finder total = 32. Auditor disprovals attempted = 2 (one upheld, one overruled). Referee net = 0 (1 correct UPHOLD-DISPROOF, 1 correct UPHOLD-FINDING — assuming the Referee was right; user has ground truth).

**Re-run criterion check.** Per SKILL.md, re-run qa-agents if: (1) any fix loops back to Phase 1–5 — yes (F4, F5, F7), or (2) two or more findings confirmed — yes (6 confirmed). The re-run rule applies. **Soft-fail logged here:** the inline simulation cannot meaningfully re-run itself in the same context (the same role-disciplined writer can't produce a fresh adversarial pass), so the re-run is deferred. This is recorded in the spec's Assumptions as: "Re-run Phase 7 against this spec from a runtime with subagent capability before treating the spec as production-grade." This counts as **one soft fail** (Phase 7 re-run deferred).

### Soft fails through Phase 7: 1 (Phase 7 re-run deferred — runtime limitation).

Below the threshold of 3, no surfacing required. Logged to Assumptions per soft-fail protocol.

### Promotion check
Phase 8 blocking-assertion soft-fail check: the deferred re-run does not correspond to any specific Phase 8 blocking assertion (qa-agents verification is logged in the Verification Record, satisfying the `qa-agents verification logged` assertion). Promotion to `status: verified` is allowed.

### Phase 7 result: spec promoted to status=verified.

---

## Phase 8 — Build Handoff

`verify_spec.py --final` run on the verified spec: **40 passed, 0 failed.** All blocking assertions clean.

`render_handoff.py --target claude-code` generated `outputs/build-handoff.md` (35 lines). Capture-mechanism examples for Claude Code: hooks (`PreToolUse`, `PostToolUse`, `Stop`), MCP servers, structured tool result parsing.

### Phase 8 result: clean. Spec is build-ready.

---

## Mode summary

| Phase | Mode | Reason |
|---|---|---|
| Phase 4 fan-out | `inline_simulation` | Task tool unavailable in this runtime |
| Phase 7 verification | `inline_simulation` | qa-agents skill protocol requires Task subagents; Task unavailable |

## Total soft fails: 1
- Phase 7 re-run deferred (logged to spec Assumptions)

## Final outcome
- Verified spec: `outputs/gix-investor-update.process-spec.md` (status: verified)
- Build handoff: `outputs/build-handoff.md`
- qa-agents intermediate JSONs: `outputs/qa-agents-gix-investor-update/{finder,auditor,referee}.json`
- `verify_spec.py --final`: **40 passed, 0 failed**

