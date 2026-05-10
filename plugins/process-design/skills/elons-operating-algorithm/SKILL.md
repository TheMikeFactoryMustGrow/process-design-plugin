---
name: elons-operating-algorithm
description: Pressure-test any artifact (spec, plan, architecture, roadmap, feature list, process, code section) using Elon's Operating Algorithm — question requirements, delete, simplify, accelerate, automate, in that strict order. Use this skill whenever the user says "pressure test", "stress test", "apply Elon's algorithm", "Elon's operating algorithm", "is this overbuilt", "what should I delete", "make this less dumb", "compress this roadmap", "where can I cut", "is this right-sized", or shares a long plan/spec/architecture and asks for a simplification review — even if they don't explicitly name the algorithm. Output is a structured vault note modeled on the Bean Counter pressure test, with deletion verdicts (KEEP/QUESTION/DECOUPLE/DEFER/DELETE/SIMPLIFY), a 10% add-back log, a "what survives" synthesis, and a deepest-question reframe. This skill is the canonical home for the algorithm in your toolkit.
compatibility: requires read access to the artifact under review and write access to either the vault or the current working directory; uses scripts/scaffold.py (Python 3.8+).
version: 0.1.0
---

# Elon's Operating Algorithm — Pressure Test

This skill takes any artifact and runs Elon's 5-step Operating Algorithm against it: **question requirements → delete → simplify → accelerate → automate**, in that strict order. The output is a structured pressure-test note modeled on the Bean Counter Architecture Pressure Test in the user's vault — a worked example that compressed a 20-story roadmap to 8 stories and unblocked a months-long prerequisite chain.

The algorithm exists because most engineering orgs (and most product roadmaps, and most architecture docs) start at step 3 or 4 — they optimize and accelerate things that should have been deleted. The discipline lives in the *order*, not the steps themselves. Steps 1 and 2 do almost all of the real work.

## When this skill matters most

- The user shares a roadmap, architecture, spec, or process and asks anything in the family of "is this overbuilt", "what should I cut", "compress this", "is this the right shape".
- The artifact is from a smart person — the user, a colleague, a vendor proposal — and the user wants an honest read that doesn't get caught by comradery.
- The artifact has more than ~5 components, steps, requirements, or stories. Below that scale, applying the full algorithm becomes ceremonial.

If you're invoked on something one paragraph long, apply the algorithm proportionally — produce a one-screen pressure test, not a 412-line one. Do not pad to look thorough.

## Inputs

You can be invoked in any of these shapes; figure out which one applies and fill in the rest by reading the artifact or asking the user.

| Shape | What you're given | What you need to derive |
|---|---|---|
| **Path** | A file path (vault note, repo file, or anywhere on disk). | Subject name (filename → title), source link (file → wikilink if in vault), fitness metric. |
| **Wikilink** | `[[Some Note]]` — a vault title. | Resolve via the user's vault search; treat as Path once resolved. Subject + source link from the title. |
| **Paste** | Inline text in the user's prompt. | Subject (ask the user for a short name), fitness metric, no source link. |
| **Reference to recent context** | "the plan we just talked about", "the spec from earlier". | Pull from conversation context; ask for a short subject name. |

## Operating stance — do not skip

This skill is the place where comradery is most dangerous. Its job is to question the user's artifact, not to validate it. If you find yourself nodding along — *"yes, this looks reasonable, here are some minor optimizations"* — you have failed the skill regardless of how clean the output looks.

Before you start, **re-read `references/algorithm.md`**. The discipline is in the rigor of application, not in memorization. Your training data has a watered-down notion of "the algorithm" that drifts toward generic advice; the bundled reference is the canon for this skill.

## How to run a pressure test

The flow has 7 phases. Phase 0 is mandatory and gates the rest; phases 1–5 map to the algorithm; the final two phases produce and file the output.

### Phase 0 — Establish the fitness metric (mandatory)

Without a fitness metric, deletions become aesthetic. The Bean Counter pressure test pivoted on *"time-to-reliable-monthly-close"* — every verdict in every table can be traced back to that one phrase. That's the discipline.

Ask: what is this artifact actually trying to achieve? Express it in one sentence, with units if at all possible. Examples:

- For a roadmap: "time-to-first-customer-revenue", "weekly active users at 90 days", "operator hours saved per close".
- For an architecture: "p99 request latency", "time-to-recover-from-failure", "lines-of-code-to-add-a-new-importer".
- For a process: "throughput per operator-hour", "error rate per 1000 transactions".

Rules:

- The fitness metric must be **one sentence**, ideally a measurable number. If it requires a paragraph, it's two metrics in disguise — pick the primary.
- If the user can't state one in a sentence, propose 2–3 candidates and ask them to pick. Don't proceed with "let's just try" — that's how pressure tests turn into ceremony.
- If multiple metrics are in genuine tension, pick the primary and *name the tradeoff* in the output's §0. The pressure test runs against the primary; the secondary is a constraint.

**Hard gate:** do not enter Phase 1 until the fitness metric is named and recorded.

### Phase 1 — Question every requirement

Read the artifact. List every requirement, assumption, prerequisite, and "must" clause you can find. Then build two tables:

**1.1 Requirements that survive questioning** — those clearly traceable to a named person and clearly serving the fitness metric. Verdict: **KEEP**.

**1.2 Requirements that need harder questioning** — those that are vague, department-attributed ("legal said", "the team needs"), or whose path to the fitness metric is not direct. Each row gets a **specific challenge** (not a generic "is this needed?") and a verdict from `references/verdicts.md`.

Rules:

- Every row must attach a **named person**. "The team", "operations", "legal", "best practices" are not names. If you can't find a person, the requirement goes in 1.2 with verdict **QUESTION** and the challenge "no named owner — who specifically requires this?".
- Senior people's requirements are the *most* dangerous, not the least. Don't soft-pedal a requirement because it came from the user, the founder, or a vendor's CTO.
- Distinguish *requirements* (load-bearing constraints) from *implementation choices* (which tools, which patterns) — the algorithm applies to both, but the questions differ. For requirements: is this real? For implementation choices: is this the simplest shape that meets the requirement?

**End-of-phase gate:** if 1.2 ended up empty (zero requirements landed in "needs harder questioning"), you have under-questioned. Loop back. The Bean Counter test had 11 rows in this section out of an artifact that looked carefully thought through — the bar is high.

**The deepest question (§1.3):** Before leaving Phase 1, write one paragraph reframing the artifact's premise. Bean Counter's was "is this a build, or a configuration?" — a single reframe that recast the entire 20-story roadmap. Every pressure test produces one of these. If you can't, you haven't questioned hard enough — loop back. (Do not skip this section even when it's hard. The hard ones are the ones that matter.)

### Phase 2 — Delete

For every component, step, story, prerequisite, integration point, and box-on-the-diagram in the surviving artifact, ask: does this serve the fitness metric? If not — DELETE. If "yes, but later" — DEFER (with a trigger condition). If "yes, but the dependency edge is wrong" — DECOUPLE. If "yes, but in a much simpler shape" — SIMPLIFY (and name the simpler shape).

Build §2.1 (Candidates for deletion) as a table with the verdict and reasoning for each. Build §2.2 (What survives deletion) as a numbered list — the compressed deliverable.

Rules:

- The bias is toward deletion. If you're unsure, delete and add back later. Aim for ~10% add-back ratio.
- A row must land a verdict from the standard vocabulary (`references/verdicts.md`). "Refactor", "investigate", "consider", "maybe" are not verdicts.
- DEFER without a trigger condition = DELETE. Be specific about what would unlock it.
- The most common failure mode here is keeping things because they exist in the artifact. The right question is not "is this fine?" — it's "if we removed this, what specifically would break against the fitness metric?".

**End-of-phase gate:** if 2.1 ended up with no DELETE / DEFER / DECOUPLE / SIMPLIFY verdicts, you have under-deleted. Loop back. (KEEP belongs in 1.1, not 2.1.)

### Phase 3 — Simplify and optimize

For each surviving piece from §2.2, ask: is its current shape the simplest shape that does the job?

This is the step where most people *want* to start. Don't. The reason simplification belongs at step 3 is that 60–80% of what people want to simplify should have been deleted in step 2. If you find yourself simplifying something, restate why it survived §2.1.

Rules:

- "Simplify" must produce a **before → after** pair. "Simplify the trust model" is not a simplification; "Reduce trust model from 5 levels to 2" is.
- Don't list survivors that don't admit simplification. Silence is a valid answer.
- Watch for *implicit* deletions sneaking in here. If your "simpler shape" is "delete this entirely", that belongs in Phase 2 — go back and add it.

### Phase 4 — Accelerate cycle time

Where would going faster materially change outcomes against the fitness metric? List those levers with their expected effect.

Rules:

- Don't accelerate what wasn't simplified. The discipline of the algorithm is sequential.
- Cycle-time levers should affect the **time domain of the fitness metric** — if the metric is "time to first customer", accelerating an internal report has no claim to be in this section.
- Avoid the temptation to list every speed-up imaginable.

### Phase 5 — Automate

Last, not first. Automation candidates go in §5.1 with a **trigger condition** that would justify the automation investment.

Rules:

- Do not recommend automating in the same pressure test that just deleted half the artifact. Note where automation should *eventually* live.
- Automation of a thing that just survived its first deletion pass is premature — let the survivors run manually for a cycle, learn, *then* automate.

### Phase 6 — Add-back log + open questions

After phases 1–5 are written, scan back through. Two final sections:

**Add-back log:** anything you deleted that, on second look, you reinstated. Aim for ~10% of deletions appearing here. If zero, you didn't try hard enough; reconsider §2.1. If many, you may have under-deleted in the first pass — but better to leave them in than to suppress the signal.

**Open questions:** the questions the pressure test couldn't resolve. Each must be addressed to a named person with a date. Department-shaped questions ("Engineering should think about caching") are not allowed here — they're the failure mode this skill is built to prevent. The right shape is: *"For [[Sarah Chen]], by 2026-05-23: should we keep the Plaid integration on dev tier or move to production?"*

### Phase 7 — File the output

Use the `scripts/scaffold.py` helper:

```
python3 scripts/scaffold.py resolve-path \
  --subject "<short subject>" \
  --source "<path to source file, if any>" \
  --cwd "$(pwd)"
```

The script returns the destination path (next to the source if one exists; in `<vault>/Values and Mechanisms/Reviews/` if you're in the Linglepedia vault; in cwd otherwise) and flags any case-insensitive collision (per Mike's `feedback_case_insensitive_filenames.md` memory — APFS treats `Foo.md` and `FOO.md` as the same file, so always check before writing).

Then scaffold the skeleton:

```
python3 scripts/scaffold.py scaffold \
  --subject "<short subject>" \
  --fitness-metric "<one-sentence metric>" \
  --source-link "<wikilink-able vault title, if any>" \
  --extra-tags "tag1,tag2" \
  --output "<destination path>"
```

Edit the resulting file in place — fill in §0 through §5, the add-back log, and open questions. When done, run the validator:

```
python3 scripts/scaffold.py validate --file "<destination path>" --strict
```

The validator checks 30+ structural and content gates. Strict mode exits non-zero if any fail. Common failures: empty placeholder rows in §1.2 / §2.1, missing numbered survivors in §2.2, fewer than 2 distinct verdicts used.

End your response by giving the user the file path so they can click through. If the skill ran outside their vault, also tell them where it landed and that they can move it into the vault if they want.

## Optional adversarial follow-up

For high-stakes artifacts (architecture decisions, hiring plans, multi-quarter roadmaps), invoke the `qa-agents` skill on the resulting deletions to challenge them adversarially. Off by default — only run when (a) the user asked for it, or (b) the pressure test recommends deleting more than 30% of the artifact and the deletions are non-obvious.

## What this skill is not

- Not an interactive workshop. If the user wants a guided 5-phase session with hard gates between phases, that's the `dmaic` or `process-design` shape — different skill.
- Not a replacement for `qa-agents`. That skill challenges *correctness*; this one challenges *bloat*. Both can run on the same artifact.
- Not a checklist runner. The discipline is the order; the verdicts are decisions that come from reading the artifact, not from a fixed list.
- Not appropriate for one-line ideas. Apply proportionally — small artifacts get small pressure tests.

## Common failure modes (and how to recover)

| Failure | Symptom | Recovery |
|---|---|---|
| **Ceremonial output** | Tables full of placeholder phrases like "consider whether", no concrete deletions. | Re-read `references/algorithm.md`. Re-read the Bean Counter pressure test in `VEGA/Architecture/`. Pick three rows from §1.2 and force a real verdict on each. |
| **Skipping Phase 0** | Verdicts feel arbitrary; the user pushes back on one and you have nothing to anchor the response. | Stop. Go back to Phase 0 and name a fitness metric. Rewrite the existing tables with that metric in mind — most verdicts will change. |
| **No deepest question** | §1.3 is a soft summary, not a reframe. | Ask: what if the artifact's *category* is wrong? (Build vs. configuration. Product vs. service. Project vs. process.) That's where the deepest question lives. |
| **Empty add-back log** | You produced a long deletion list but reinstated nothing. | Either you deleted things the user genuinely needs (reinstate them, learn) or you under-deleted in the first pass (good — you're calibrated). The 10% number is a heuristic; the *signal* is whether you tested any of the deletions hard enough to reverse one. |
| **Department-attributed requirements** | §1.1 has rows like "Compliance: keep X". | Loop back. Find the named person. If you can't, the row goes in §1.2 with verdict QUESTION. |
| **"Simplify the X"** | Phase 3 has rows that don't name the simpler shape. | Each row is `before → after`. If you can't name the after, the row doesn't belong in Phase 3 — either delete (§2.1) or KEEP. |

## References (read at the start of each session)

- `references/algorithm.md` — the 5 steps + corollaries. Re-read every session.
- `references/verdicts.md` — the verdict vocabulary and when each applies.
- `references/output-template.md` — the structure and style of the output note.
- `references/worked-example-pointer.md` — pointer to the Bean Counter pressure test in the vault, with notes on what to copy and what not to copy.
