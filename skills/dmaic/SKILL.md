---
name: dmaic
description: Measurement-and-improvement scaffold for any process the user wants to make better. Trigger whenever the user describes a process that's drifting, chaotic, or unmeasured — phrasings like "this is hit or miss", "we don't actually know if X is working", "I want to track [process]", "make this measurable", "design metrics for this", "create an improvement plan", or any time the user wants to tighten a fuzzy goal into named metrics with a regression guard, even when they never say "DMAIC" by name. Walks the five Six Sigma phases (Define → Measure → Analyze → Improve → Control) and writes a structured spec to the user's knowledge vault (Obsidian/Linglepedia) when present, otherwise to a markdown file. Defaults to this orchestrator over the per-phase skills (dmaic-define, dmaic-measure, dmaic-analyze, dmaic-improve, dmaic-control) unless the user is clearly asking for one phase in isolation, or another skill is calling a phase à la carte.
---

# DMAIC

Apply the full DMAIC cycle to a process or idea, then save a structured spec.

> **Order matters.** Define before you Measure. Measure before you Analyze. Analyze before you Improve. Improve before you Control. Most people start at Improve and wonder why nothing sticks.

---

## When to use this skill

Trigger on phrases like:

- "Run DMAIC on [process]"
- "Create metrics for [process / idea]"
- "Make [thing] measurable"
- "Design an improvement cycle for [thing]"
- "Spec [process] so we can improve it"
- "I want to track / improve / monitor [thing]"
- "Build a measurement plan for [thing]"

If the user only wants one phase (e.g., "just help me name the metrics"), invoke the phase skill directly: `dmaic-define`, `dmaic-measure`, `dmaic-analyze`, `dmaic-improve`, `dmaic-control`.

---

## Inputs to gather

Before running any phase, capture three things from the user. Ask only what's missing — don't ask if the request already answers it.

1. **The subject.** What process, system, or idea are we DMAIC-ing? Get a one-sentence description.
2. **The owner.** Who is accountable for this process? (Person, role, or team.)
3. **The output target.** Where should the final spec live? Default behavior:
   - If running in a session with a knowledge vault mounted (look for `CLAUDE.md`, an Obsidian vault root, or a `_schemas/` folder), propose saving as a structured note in the vault. Ask the user which folder.
   - If running in Linglepedia specifically, default to `Projects/` unless the subject clearly belongs in a domain folder (e.g., a GIX customer-onboarding process → `GIX/`).
   - Otherwise, write a markdown file to the working directory and tell the user the path.

Don't proceed until you have a subject. Owner and target can be filled in later if the user is exploring.

---

## The five phases

Two ways to run the phases — both are valid:

1. **Invoke the per-phase skills via the Skill tool.** Cleanest separation. Call `dmaic-define`, then `dmaic-measure`, then `dmaic-analyze`, then `dmaic-improve`, then `dmaic-control`, in that order. Each one returns its block.
2. **Apply the rules inline.** If invoking sub-skills isn't practical (e.g., they aren't installed, or the cost of the extra hops doesn't pay off for the task), follow the per-phase summaries below in the same order. The summaries are deliberately self-contained.

Either way, the order matters. Define before Measure, Measure before Analyze, Analyze before Improve, Improve before Control. Don't let the user start at Improve.

### Phase 1 — Define

Capture three sentences:
- **What is this process supposed to do?** State the purpose in one sentence. No jargon.
- **What does success look like?** A concrete, observable end state.
- **What does failure look like?** Equally concrete. Failure is the absence of success, but stating it explicitly forces clarity.

Stuck? The most common Define failure is fuzziness ("improve customer experience"). Push for "customers complete onboarding in under 5 minutes without contacting support." If the user can't write the failure sentence, the success sentence is too vague.

### Phase 2 — Measure

This is usually the user's biggest gap.

Pick **2–3 terminal metrics** — the metrics that, if they're good, the process is good. Not intermediate diagnostics. Not vanity counts.

For each metric, capture:
- **Name.** Short, unambiguous.
- **Definition.** How it's calculated, including units.
- **Collection.** How and how often it's gathered. Manual? Automated? Daily, weekly, per-event?
- **Baseline.** Current value (or "unknown — establish in week 1").
- **Target.** Where it needs to land for the process to count as working.

Reject vanity metrics (impressions, headcount, page views) unless they're truly terminal for this specific process. Push for outcome metrics (conversion, latency, error rate, dollars retained).

> **Rule of thumb:** If the metric goes up but the world isn't better, it's the wrong metric.

### Phase 3 — Analyze

Connect each metric to action:

- **Threshold.** When does this metric cross a line that demands investigation? Define a green/yellow/red band or a specific trigger value.
- **Known failure modes.** When this metric goes bad, what are the 3–5 most common causes? List them now so future-you isn't staring at a dashboard wondering what to do.
- **Investigation playbook.** For each threshold breach, what's the first action? Who runs it?

Without this phase, you have dashboards nobody looks at.

### Phase 4 — Improve

Frame every improvement attempt as an experiment.

For the first proposed improvement (or for each one in flight), capture:
- **Hypothesis.** "We believe [change] will [effect] because [reasoning]."
- **Test plan.** What gets changed, on what scope, for how long.
- **Success criterion.** Which metric moves, by how much, to call it a win.
- **Failure criterion.** What result would make us revert.

If the user is just spec'ing the process and has no improvement to test yet, leave this section as a template. Note in the spec that experiments will be logged here as they run.

> **Failed experiments are data, not waste.** Every attempt — successful or not — gets logged.

### Phase 5 — Control

Design the regression guard:

- **Monitoring.** Which metric, watched on what cadence, by whom?
- **Alert.** What trips an alert? Where does the alert go? Who responds?
- **Recurring review.** When and how often does someone re-examine the spec to confirm the metrics still measure the right thing?

Most fixes regress because nobody designed the guard. The Control section is the difference between a temporary win and a durable one.

---

## Composing the output

The plugin ships a helper script — `scripts/dmaic.py` (sibling of this SKILL.md) — that handles the deterministic parts of authoring the spec: vault detection, frontmatter assembly, and schema validation. **Use it.** Building the markdown by hand from string concatenation is error-prone and creates formatting drift between runs; the script is bit-for-bit consistent.

### Step 1 — Detect the vault

Before writing anything, run:

```bash
python3 <plugin-root>/skills/dmaic/scripts/dmaic.py detect-vault --cwd <pwd>
```

It returns JSON with:
- `vault_type`: `"obsidian"`, `"linglepedia"`, or `"none"`
- `vault_root`: absolute path or `null`
- `linglepedia_domain_folders_present`: hint for routing the new spec into the right domain folder

If `vault_type == "none"`, fall back to writing the spec to the current working directory.

### Step 2 — Build a spec.json in memory

Collect the outputs of the five phases into a dict matching this shape, then write it to a temp file:

```json
{
  "process": "GIX Fiber Customer Onboarding",
  "owner": "VP of Customer Operations",
  "status": "draft",
  "tags": ["dmaic", "gix", "operations"],
  "summary": "One-sentence summary of what this spec covers and why we're writing it.",
  "related_extra": ["NY Fiber (GIX)"],
  "define_block":   "**What this process is supposed to do:** ...\n\n**What success looks like:** ...\n\n**What failure looks like:** ...",
  "measure_block":  "### Metric 1: ...\n- **Definition:** ...\n- **Collection:** ...\n- **Baseline:** ...\n- **Target:** ...\n\n### Metric 2: ...\n...",
  "analyze_block":  "### [Metric 1 Name]\n- **Threshold:** ...\n- **Known failure modes:** ...\n- **First action:** ...\n\n### [Metric 2 Name]\n...",
  "improve_block":  "### Current experiment\n- **Hypothesis:** ...\n- **Test plan:** ...\n- **Success criterion:** ...\n- **Failure criterion:** ...\n- **Owner:** [[Person]]\n- **Decision date:** YYYY-MM-DD",
  "control_block":  "### Monitoring\n- ...\n\n### Alert\n- ...\n\n### Recurring spec review\n- ...",
  "notes_block":    "(optional free-form context, links to related work, decisions, references)"
}
```

Every block is markdown — no leading `## Define` heading; the script adds the headings.

If a `_schemas/dmaic-spec.md` exists in the vault, read it first and add any extra fields it requires. The script's required-keys list is permissive — additional frontmatter fields you put in the spec.json get passed through.

### Step 3 — Compose and validate in one call

```bash
python3 <plugin-root>/skills/dmaic/scripts/dmaic.py compose \
  --input /tmp/dmaic-spec.json \
  --output <vault_root>/<domain_folder>/dmaic-<slug>.md \
  --validate-after
```

`--validate-after` runs the same schema check as `validate` and exits non-zero if anything fails. If you see failures, fix the inputs and re-run; don't ship a malformed spec.

For target paths in a Linglepedia vault, route by domain:
- A GIX process → `<vault_root>/GIX/`
- A WE deal/portfolio process → `<vault_root>/WE/`
- A personal/health process → `<vault_root>/Projects/`
- A fallback → `<vault_root>/Projects/`

Use a kebab-case slug derived from the process name (e.g., `dmaic-gix-fiber-customer-onboarding.md`).

### Step 4 — Validate any spec, anytime

If the user re-runs DMAIC on an existing spec, or asks "is this spec still good?", run:

```bash
python3 <plugin-root>/skills/dmaic/scripts/dmaic.py validate --file <path-to-spec.md>
```

Returns per-check pass/fail. Useful when the user comes back to a spec they wrote months ago.

### What the spec must contain (for reference)

If for any reason the script isn't available and you have to compose the spec inline, follow `references/spec-template.md` exactly. The required pieces are:

1. **YAML frontmatter** with: `type: dmaic-spec`, `process`, `owner`, `status`, `created`, `last_reviewed`, `truth_score`, `tags` (must include `dmaic`), and `related` listing `"[[DMAIC]]"` plus any other relevant wikilinks.
2. **One section per phase** — Define, Measure, Analyze, Improve, Control — using `## ` (H2) headings exactly.
3. **An Experiments Log** section with a `| Date | Hypothesis | Result | Decision |` table, empty initially.
4. **`[[DMAIC]]`** wikilink in `related` when writing into an Obsidian vault.

---

## Vault-aware behavior (Linglepedia + Obsidian)

Detection is handled by `scripts/dmaic.py detect-vault` (see "Step 1" above). When it reports a vault, follow these conventions:

- Always quote wikilinks in YAML: `related: "[[DMAIC]]"`.
- Read `_schemas/README.md` before writing if it exists, and conform to any `dmaic-spec` schema you find.
- Use the existing folder taxonomy (`GIX/`, `WE/`, `Projects/`, etc.) — don't invent a new top-level folder.
- If the spec touches a person, company, or entity already in the vault, link to it with `[[wikilinks]]`.
- After writing the note, surface it to the user as a `computer://` link if running in Cowork.

If no vault is detected, write a `.md` file to the working directory and tell the user the path.

---

## Common mistakes to flag

When the user is working through a phase, watch for these and push back gently:

- **Starting at Improve.** "Let me suggest we Define first — what does this process even do?"
- **Skipping Control.** Don't let the spec ship without a Control section, even if it's "TBD — needs designing in week 2."
- **Measuring everything.** Cap at 3 terminal metrics. More is noise.
- **Vanity metrics.** Push for outcomes, not activity.
- **Treating it as a one-time spec.** Set `last_reviewed` and tell the user the spec needs a quarterly re-read.

---

## References

- `references/spec-template.md` — exact markdown template for the output note
- `references/dmaic-reference.md` — the canonical DMAIC theory (excerpt of `[[DMAIC]]` from the Linglepedia vault)

---

## Principles (from `[[DMAIC]]`)

1. **Mechanisms over philosophy.** "Get better every day" is a wish. A DMAIC cycle with named metrics and regression detection is a mechanism.
2. **Measure before you improve.** Establish a baseline first, even if the numbers are embarrassing.
3. **Control is not optional.** Every improvement without a regression guard is temporary.
4. **Terminal metrics are the only ones that matter.** Intermediate metrics are for diagnosis, not justification.
5. **Failed experiments are data.** Log every attempt.
6. **Agents own their own DMAIC.** Each owner inventories their own processes and builds their own cycles.
7. **Evolve the framework.** Propose improvements as you learn what works.
