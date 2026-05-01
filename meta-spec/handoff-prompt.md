# Build Handoff Prompt

**Build target:** `existing-skill-audit-and-dmaic-feed`

**Paste the prompt below into the build agent (or invoke a fresh Claude Code session in the plugin repo):**

---

> Audit the existing process-design skill at `~/.claude/plugins/marketplaces/local-desktop-app-uploads/process-design/` against the spec at `~/Documents/Linglepedia/_claude_config/process-design/meta-spec/process-design.process-spec.md`. The flowchart for review is at `~/Documents/Linglepedia/process-design-flowchart-review.md` (Obsidian-rendered).
>
> Honor the spec strictly: every named decision rule, edge case, gate, success criterion, and metric is binding. The 8 drift items in the spec's Build Notes section are the specific updates SKILL.md needs:
>
> 1. Phase 3 (Algorithm) dissolves into distributed deletion + concentrated Step 3 pruning AFTER the visual exists
> 2. Render hoisted to Step 2 with hard-gate review BEFORE metrics design
> 3. Step 0 (Ingest) added for existing source descriptions
> 4. Step 8 (Reconcile) added (conditional on Step 0)
> 5. Step 5.5 folded into Step 6 as `image_freshness` blocking assertion
> 6. Step 2 Review hard gate has 3 explicit outcomes (confirm / reject+named / reject-silent→1A)
> 7. Gap-probe per-agent completion gate (not just Task availability check)
> 8. Foregrounding requirement: agent's response MUST surface image path on its own line after Step 2 render
>
> After SKILL.md is reconciled with the spec, invoke `Skill(dmaic)` against `~/.claude/process-design-sessions/` for the next review cycle. Identify the three highest-priority improvements from accumulated telemetry. Propose specific updates to SKILL.md, `verify_spec.py` assertion table, and telemetry taxonomy.
>
> Wire in the new telemetry event `post_handoff_clarification` (named in this spec; not in existing SKILL.md taxonomy). Use deterministic capture appropriate to the runtime.
>
> Surface ambiguity rather than papering it over. If any drift item conflicts with existing SKILL.md content in a way that requires user judgment, ask before deviating.
>
> Before starting, summarize the spec back: which gates run as scripts vs. agents vs. humans, and which of the 8 drift items you intend to handle in this session vs. defer to the next.

---

## Artifacts produced this session

- `meta-spec/process-design.process-spec.md` — verified spec (status: verified)
- `meta-spec/process-design.flowchart.mmd` — Mermaid source
- `meta-spec/handoff-prompt.md` — this file
- `process-design-flowchart-review.md` (Linglepedia root) — Obsidian-rendered flowchart for review

## Verification status

- Phase 4 mode: `task_fanout` (4 parallel sub-agents)
- Phase 7 mode: `inline_simulation` — qa-agents skill not invoked; finder/auditor/referee simulated inline. Adversarial isolation collapsed. **Re-run Phase 7 against this spec from a runtime with subagent + skill capability before treating as production-grade.**
- Telemetry: `degraded` — telemetry destination not exercised this session; emit will resume in normal runs
- Hard gate (Step 2 Review): confirmed by user

## Open items

1. Concreteness rule needs sharpening (Step 1A) — DMAIC review-1 candidate
2. `intent_articulation_quality` operational measure needs tightening — DMAIC review-1 candidate
3. Step 8 "user refuses to name canonical" failure mode unspecified — DMAIC review-1 candidate
4. `mmdc` CLI bootstrap missing on user's machine — SKILL.md bootstrap section needed
5. `health.cost_tokens` requires external instrumentation — DMAIC-feed measurement gap
