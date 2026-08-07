# Agent runtimes (Claude Code · Grok Skills · Grok Build)

This plugin's skills are **runtime-portable Agent Skills** (`SKILL.md` + optional
`references/`, `scripts/`, `templates/`). Claude-native wording in skill bodies is
**preserved** — it still works on Claude Code / Cowork. Use this map when the
host is Grok (or any Agent Skills host that is not Claude Code).

## Host detection (agent)

| Host | How you know |
| --- | --- |
| **Claude Code / Cowork** | `Skill` tool, Claude plugin namespaces (`process-design:…`), optional Workflow tool |
| **Grok Skills** (web / iOS / Android) | Skill installed in the user's Grok Skills library; tools are Grok's (web search, code execution, etc.) |
| **Grok Build** | Project/global skills under `.grok/skills/` or `~/.grok/skills/`; coding-agent tools (`task`, file tools, shell) |

If unsure, prefer the **generic** column below — it works on every host.

## Tool / concept map

| Skill text (Claude-native) | Generic meaning | Grok Skills | Grok Build |
| --- | --- | --- | --- |
| `Skill(name)` / `Skill(process-design:name)` | Load sibling skill instructions and follow them | Open installed skill `name` (or its `SKILL.md`) and follow it | Read `.grok/skills/<name>/SKILL.md` (or `~/.grok/skills/<name>/`) and follow it |
| `Task` / subagents | Isolated parallel agents with clean context | Spawn parallel agent turns / independent reasoning passes; if isolation is unavailable, use `inline_simulation` and log it | Grok `task` tool (`general-purpose` / `explore` / `plan`); separate calls per adversarial role |
| `AskUserQuestion` | Ask the human | Ask in chat (one consolidated message) | Ask in chat (one consolidated message) |
| Claude Code Workflow tool / `.claude/workflows/*.js` | Runnable automation of a verified process | Produce a portable handoff (script, checklist, or Grok-runnable steps). Do **not** claim `implemented` without a live run on this host | Prefer implement-in-Build or a Node/Python script under the project; only write `.claude/workflows/` when the user wants a Claude export |
| `${CLAUDE_PLUGIN_ROOT}/skills/<name>/…` | Absolute path to this skill's files | Paths inside the installed skill package | `/workspace/.grok/skills/<name>/…` or `~/.grok/skills/<name>/…` |
| `mmdc` (Mermaid CLI) | Render flowchart PNG | Use host image/render tools, or ship Mermaid fenced markdown as fallback | `mmdc` with Chromium config when available; else Mermaid markdown fallback |
| Telemetry `~/.claude/process-design-sessions/` | Session JSONL log dir | Use `$PROCESS_DESIGN_LOG_DIR` if set; else a user-visible project folder; best-effort only | `/workspace/.process-design-sessions/` or `$PROCESS_DESIGN_LOG_DIR` |

## Rules that never change

1. **Do not delete Claude-specific steps** when running on Claude Code — they remain authoritative there.
2. **Do not invent a different procedure** on Grok — same steps, gates, and deliverables; only the *tool names* change.
3. **Soft-fail + log** when a host lacks subagents, Workflow, or `mmdc` — same as existing skill fallbacks (`inline_simulation`, Mermaid markdown, etc.).
4. **Foreground the flowchart** (path or rendered image) on every host that can surface files/images.
5. **Scripts stay stdlib Python 3** — run with `python3` from the skill's `scripts/` directory.

## Sibling skill names (install these together)

`process-design`, `qa-agents`, `dmaic`, `dmaic-define`, `dmaic-measure`, `dmaic-analyze`, `dmaic-improve`, `dmaic-control`, `elons-operating-algorithm`, `test-loop`, `build-workflow`, `system-map`, `system-build-loop`

On Claude Code they are namespaced `process-design:<name>`. On Grok they install under the bare `name`.

## Recommended install sets

| Goal | Minimum skills |
| --- | --- |
| Design one process | `process-design` + `qa-agents` |
| Full metrics loop | above + `dmaic` (+ phase skills as needed) |
| Pressure-test any artifact | `elons-operating-algorithm` |
| Harden code after build | `test-loop` |
| Multi-process systems | `system-map` (+ `process-design` per box) |
| Autonomous ramble→system | `system-build-loop` (pulls the rest) |

## Packaging note

Source of truth remains `plugins/process-design/skills/<name>/`.  
Grok `.skill` artifacts are built by `scripts/package_for_grok.py` into `dist/grok/` without rewriting Claude plugin layout.
