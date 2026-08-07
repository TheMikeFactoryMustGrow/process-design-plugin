# AGENTS.md

Project instructions for coding agents.

<!-- agent-papercuts:begin -->
## Log agent papercuts

When you hit **small friction** while working — a tool call that missed and had
to be retried, a confusing or undocumented setup step, a flaky command, a stale
cache, a misleading error, a non-obvious gotcha — log it via:

```bash
papercut -m <model> "one or two sentences: what you were doing → what got in the way"
```

Data lives under **`.agent-papercuts/`** (open list + history), not a root
`PAPERCUTS.md`, so it does not collide with product files. Do this
**proactively, in the moment**.

Sand: skill **papercuts** ("fix the papercuts"). Clear with `papercut resolve`
(not hand-delete). Long cycle: **papercuts-kaizen**.
<!-- agent-papercuts:end -->

## Branch and PR workflow

Agents working on this repo: **do not push straight to `main`**.

1. Branch from latest `main` (`feat/`, `fix/`, `docs/`, `chore/`).
2. Open a PR into `main`.
3. If you changed anything under `plugins/process-design/`, bump
   `plugins/process-design/.claude-plugin/plugin.json` version (see
   [CONTRIBUTING.md](CONTRIBUTING.md) — PATCH / MINOR / MAJOR).
4. If skills changed, run `./build.sh` so `dist/` stays in sync.

Full rules: [CONTRIBUTING.md](CONTRIBUTING.md).

