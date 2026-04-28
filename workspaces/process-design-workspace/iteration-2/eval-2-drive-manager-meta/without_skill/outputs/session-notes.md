# Session notes — drive-manager feedback loop meta-process

## Approach

The user asked for a meta-process, not a pile of code, but they also said they want to build it as a Python script. I produced both: a spec that explains the design, and a working Python scaffold that implements it.

I framed the design around the DMAIC mindset because that fits how the user thinks (they have a `dmaic` plugin):

- **Define** — clear success and failure sentences in §2 of the spec.
- **Measure** — three metrics in §7 (capture rate, promotion latency, repeat-miss rate).
- **Analyze / Improve / Control** — the 5-phase pipeline (DETECT → CAPTURE → TRIAGE → PROMOTE → VERIFY) is essentially Analyze + Improve + Control wrapped together. The Verify replay is the regression guard.

The hardest part of this design isn't capture, it's triage. A naive system that auto-promotes any correction into a rule will let one weird file mutate the rules and break the next ten. So I made triage a deliberate, human-in-the-loop step with four buckets (new rule / strengthen / disambiguate / noise), and gave it a simple suggestion heuristic the user can override.

The other big design call was making the audit log (`route-decision.jsonl`) the single source of truth. Without it, this whole thing is just a manual journal. The spec calls out wiring that into `drive-manager` as task #1.

## What I produced

1. **`SPEC.md`** — the meta-process design. Problem statement, 5-phase pipeline with an ASCII diagram, data model, CLI surface, documented assumptions, metrics, and an explicit "what this is not" section.
2. **`feedback_loop.py`** — a working Python scaffold (~600 lines) implementing all six subcommands: `detect`, `log-correction`, `review`, `promote`, `verify`, `status`. Compile-clean, uses only stdlib + PyYAML, abstracts the rules file behind a `RulesStore` so YAML can be swapped for JSON/TOML if drive-manager uses something else. Includes a regression-guard replay before any rule edit is committed.

## Assumptions I made (since I couldn't ask)

- Rules are in YAML at `~/.drive-manager/rules.yaml`. The spec documents this, and `RulesStore` makes it swappable.
- The skill can be made to write a `route-decision.jsonl`. If it can't, the script degrades gracefully — `log-correction` still works, but `detect` is useless without the audit log.
- Human-in-the-loop triage is acceptable; auto-promotion is explicitly rejected.
- Single-user, single-machine. Local backups, optional git commit if the rules file is in a repo.

## Things I deliberately did *not* do

- No ML/LLM-based classifier. The triage heuristic is dumb and conservative on purpose; the rules file should stay human-auditable.
- No real-time fswatch daemon. The spec mentions it as the preferred trigger, but the scaffold ships with a polling `detect` command and assumes a launchd/cron schedule. Cheaper to build, easier to debug.
- No tests. This is a scaffold the user will iterate on; testing it before they wire it to a real audit log would be premature.
