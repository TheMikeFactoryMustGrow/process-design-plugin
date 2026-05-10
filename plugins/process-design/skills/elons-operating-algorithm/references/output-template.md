# Output Note Template

This is the structure every pressure-test note follows. It's modeled on `VEGA/Architecture/Bean Counter - Architecture Pressure Test.md`, the canonical worked example in the Linglepedia vault. The structure is intentional: tables are the load-bearing element because they make the verdicts scannable.

The file `scripts/scaffold.py` writes the frontmatter + empty section skeleton. The agent fills in the content.

## Filename and path

- **Source-attached pressure test:** if the artifact under review is a vault note at `<path>/<source>.md`, write to `<path>/<source>-pressure-test.md`.
- **Standalone pressure test:** otherwise write to `~/Documents/Linglepedia/Values and Mechanisms/Reviews/<slug>-pressure-test.md` where `<slug>` is a kebab-cased short subject name.
- **Outside the vault:** if the user is not in their Linglepedia vault (e.g. running the skill from `~/code/some-repo`), write to `./<slug>-pressure-test.md` in the current working directory and tell the user where it landed.
- **Always** run a case-insensitive existence check before writing, per Mike's `feedback_case_insensitive_filenames.md` memory: APFS treats `Foo.md` and `FOO.md` as the same file and a Write would silently overwrite. Use `find -iname` first.

## Frontmatter

```yaml
---
type: pressure-test
subject: "<artifact name or [[Wikilink]] to the source>"
fitness-metric: "<one-sentence metric — see Phase 0>"
status: draft
version: 1
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
method: Elon's Operating Algorithm pressure test
author: "[[Mike Lingle]]"
tags:
  - pressure-test
  - operating-algorithm
  - <subject-area tag(s)>
related-docs:
  - "[[Elon's Operating Algorithm]]"
  - "<source artifact wikilink, when one exists>"
is_canonical: false
truth_score: agent-populated
last_verified: <YYYY-MM-DD>
---
```

`is_canonical: false` is correct for a pressure test even when its conclusions are good — the canonical artifact is the source under review (or the deliverable that comes out of "what survives"). Pressure tests are reviews of canonical artifacts, not canonical themselves.

## Body sections (in order)

```markdown
# <Subject> — Pressure Test

> **Method:** Elon's Operating Algorithm. Each requirement, component, and decision in <subject> is treated as a hypothesis that must justify itself against the fitness metric. The 5 steps run in strict order — questioning and deletion before simplification, simplification before acceleration, acceleration before automation.

> **Fitness metric:** <one sentence — what every decision is evaluated against>

---

## 0. Fitness metric

<2–3 sentences expanding on the metric. Why this metric and not another. What "moves the needle" looks like in concrete terms. If multiple metrics were in tension, name the tradeoff and pick one as primary.>

---

## 1. Step 1 — Question Every Requirement

> *"Every requirement must trace to a named person. The more senior the person, the more dangerous the requirement, because people are less likely to question it."*

### 1.1 Requirements that survive questioning

| Requirement | Who required it? | Justification | Verdict |
|---|---|---|---|
| <requirement> | <[[Person]]> | <why it serves the fitness metric> | **KEEP** |
| ... | ... | ... | ... |

### 1.2 Requirements that need harder questioning

| Requirement | Who required it? | Challenge | Recommendation |
|---|---|---|---|
| <requirement> | <[[Person]] or "(unattributed)"> | <specific challenge to the requirement> | **QUESTION / DECOUPLE / DEFER / DELETE / SIMPLIFY** |
| ... | ... | ... | ... |

### 1.3 The deepest question

<One paragraph reframing the artifact's premise. The Bean Counter example: "is this a build, or a configuration?" — recasting a 20-story build as a venv-and-some-scripts setup. Every pressure test should produce one of these. If you can't, you haven't questioned hard enough; loop back.>

---

## 2. Step 2 — Delete Any Part or Process

> *"If you aren't adding back at least 10% of what you delete, you're not deleting enough."*

### 2.1 Candidates for deletion

| Component / step / story | Current status | Verdict | Reasoning |
|---|---|---|---|
| <name> | <where it lives in the source> | **DELETE / DEFER / DECOUPLE / SIMPLIFY** | <why> |
| ... | ... | ... | ... |

### 2.2 What survives deletion

<Numbered list of what's left. The Bean Counter example collapsed a 20-story backlog to 8 numbered survivors. This is the most important section of the document — it's the compressed deliverable.>

1. <Surviving piece 1>
2. <Surviving piece 2>
3. ...

---

## 3. Step 3 — Simplify and Optimize

> *"The most common error is optimizing something that shouldn't exist."*

For each surviving piece from 2.2, ask: is its current shape the simplest shape that does the job?

### 3.1 Simplification targets

<For each item that admits simplification, give a "before → after" pair with a one-line rationale. Don't list survivors that don't need simplification — silence is fine.>

- **<piece>:** <current shape> → <simpler shape>. <one-line rationale>.

---

## 4. Step 4 — Accelerate Cycle Time

> *"Speed up every process — but only after you've deleted what shouldn't exist."*

### 4.1 Cycle-time levers

<Where would going faster materially change outcomes? Avoid the temptation to list every speed-up imaginable; the algorithm only authorizes acceleration on what's already been simplified.>

- <lever>: <expected effect on the fitness metric>.

---

## 5. Step 5 — Automate

> *"Last, not first. Automating waste produces waste faster."*

### 5.1 Automation candidates (deferred)

<List where automation should *eventually* live. Do not recommend automating in the same pressure test that just deleted half the artifact. Note the trigger condition that would justify investing in the automation.>

- <process>: automate when <condition>.

---

## Add-back log

<Things deleted in Step 2 that were reinstated by the end of the pressure test. Aim for ~10% of deletions appearing here. Zero items = you didn't try hard enough to delete; reconsider Step 2. Many items = you may have under-deleted in the first pass.>

- <item>: deleted in §2 because <reason>; added back because <new reason>.

---

## Open questions

<The questions the pressure test couldn't resolve. Each must be addressed to a named person with a date. Department-shaped questions ("Engineering should think about caching") are not allowed here — they're the failure mode this skill is built to prevent.>

- For <[[Person]]>, by <YYYY-MM-DD>: <question>.
```

## Style notes

- Tables, not prose. The pressure test must be scannable in 60 seconds.
- Verdicts in **bold** (the markdown bold, not just CAPS), so they jump out.
- Wikilinks in `[[...]]` for any vault entity referenced.
- One pull-quote per step, drawn from the algorithm. They aren't decoration — they keep the reader oriented to which step they're in.
- The "deepest question" section is what differentiates a real pressure test from a checklist run. Don't skip it.
