# Install Process Design skills on Grok

These skills use the open **Agent Skills** format (`SKILL.md`). They work on:

- **Grok Skills** (grok.com / iOS / Android) — persistent across *all* your Grok chats
- **Grok Build** — coding agent (project or global skill folders)
- **Claude Code / Cowork** — unchanged; use the Claude plugin path in the root README

Claude-native instructions inside each skill are **kept**. When a host is not Claude Code, the agent follows `references/agent-runtimes.md` (tool name mapping only).

---

## A. Grok Skills (global — recommended for daily use)

1. Download packages from this repo:
   - Per skill: [`dist/grok/<name>.skill`](../dist/grok/)
   - Everything: [`dist/grok/process-design-skills.zip`](../dist/grok/process-design-skills.zip)
2. On [grok.com](https://grok.com) open **Skills** (or Customize → Skills).
3. **Create / Upload skill** and choose one of:
   - a `.skill` file (preferred — one skill per upload), or
   - a `.zip` / `.md` if the UI offers those formats.
4. Repeat for the skills you want. Minimum useful set:
   - `process-design.skill`
   - `qa-agents.skill`
5. Start a **new chat** and try: *“Design a process for weekly content review.”*

**Tip:** Install the full set if you want sibling handoffs (`dmaic`, `elons-operating-algorithm`, `system-map`, …) to resolve by name.

### Suggested install order

| Priority | Package | Why |
| --- | --- | --- |
| 1 | `process-design.skill` | Headliner — flowchart + build-ready spec |
| 2 | `qa-agents.skill` | Adversarial verify (Step 6) |
| 3 | `dmaic.skill` | Metrics review cycles |
| 4 | `elons-operating-algorithm.skill` | One-shot deletion-first pressure test |
| 5 | `test-loop.skill` | Executable regression guard after builds |
| 6 | `system-map.skill` | Multi-process altitude |
| 7 | `system-build-loop.skill` | Autonomous ramble → ratified system |
| 8 | `build-workflow.skill` | Claude Code Workflow compile (optional on Grok) |
| 9–13 | `dmaic-define` … `dmaic-control` | À-la-carte DMAIC phases |

---

## B. Grok Build (coding agent)

### Project-scoped (this repo / a project)

```bash
# from a project root
mkdir -p .grok/skills
unzip -o /path/to/process-design-skills.zip "skills/*" -d /tmp/pd-skills
cp -R /tmp/pd-skills/skills/* .grok/skills/
```

### Global across all Grok Build projects (on a machine with the CLI)

```bash
mkdir -p ~/.grok/skills
unzip -o /path/to/process-design-skills.zip "skills/*" -d /tmp/pd-skills
cp -R /tmp/pd-skills/skills/* ~/.grok/skills/
```

Restart the Grok Build session so skills load.

---

## C. Claude Code / Cowork (unchanged)

Do **not** use the Grok packages for Claude if you already use the marketplace plugin — prefer:

```bash
/plugin marketplace add TheMikeFactoryMustGrow/process-design-plugin
/plugin install process-design@process-design-plugin
```

Or Cowork drag-and-drop: [`dist/process-design.plugin`](../dist/process-design.plugin).

The Grok packages and Claude plugin **share the same skill source** under `plugins/process-design/skills/`. Shipping both does not fork behavior.

---

## D. Rebuild packages after editing skills

```bash
# optional: pip install pyyaml
python3 scripts/package_for_grok.py
./build.sh   # still builds the Claude .plugin
```

CI / release: commit updated `dist/grok/*` when you cut a version so non-git users can download artifacts from GitHub.

---

## E. Runtime notes (Grok)

| Capability | Behavior on Grok |
| --- | --- |
| Subagents (`Task`) | Use host multi-agent / parallel turns when available; else `inline_simulation` + log in Verification Record |
| `Skill(qa-agents)` | Open installed `qa-agents` skill and follow it |
| Flowchart PNG (`mmdc`) | Render when CLI+Chromium exist; else Mermaid fenced markdown fallback |
| `build-workflow` | Prefer a portable handoff or Grok Build implementation unless user wants a Claude Workflow export |
| Telemetry | Best-effort JSONL under `$PROCESS_DESIGN_LOG_DIR` or a project folder; never block the skill |

Full map: `plugins/process-design/shared/agent-runtimes.md` (also injected into each `.skill` as `references/agent-runtimes.md`).
