# Contributing

How humans and agents work on this repo without stepping on each other.

## Protect `main`

`main` is the **shippable** branch: Claude marketplace consumers, Grok `.skill` packages in `dist/grok/`, and Cowork’s `.plugin` all lag off it.

| Rule | Detail |
| --- | --- |
| **No direct pushes to `main` by agents** | Open a branch + PR. Humans may fast-path tiny docs fixes; prefer PRs anyway when other agents are active. |
| **CI must be green** | `plugin-ci` validates marketplace/plugin manifests, version bumps, and tags. Don’t merge red. |
| **One outcome per PR** | Prefer small, reviewable diffs over multi-day megapacks. |
| **Don’t share a branch across agents** | Each agent (or task) gets its own branch. Serialize if two tasks touch the same skill files. |

### Suggested GitHub branch protection (repo settings)

In GitHub → **Settings → Branches → Branch protection rules** for `main`:

1. Require a pull request before merging  
2. Require status checks to pass: `validate`, `version-guard` (and `tag-check` if you use it on PRs)  
3. Do **not** allow force pushes  
4. Optional: require 1 approval when co-maintainers exist  

Agents cannot flip these settings for you — enable them once in the UI when you can.

## Workflow (agents and humans)

```text
1. git fetch && git checkout main && git pull
2. git checkout -b <type>/<short-slug>     # feat/ fix/ docs/ chore/
3. Make changes; keep scope tight
4. If plugins/process-design/ changed → bump plugin.json version (see Versioning)
5. If any skills/** changed → run ./build.sh (or at least package_for_grok.py)
6. Commit with a clear message (what + why)
7. git push -u origin HEAD
8. Open a PR → main; fill the template below
9. Wait for CI; address review; squash/merge (or merge commit — pick one repo style and stick to it)
```

### Branch names

| Prefix | Use |
| --- | --- |
| `feat/` | New skill behavior, new package surface |
| `fix/` | Bug in skill, script, or packaging |
| `docs/` | README, CONTRIBUTING, INSTALL-GROK only |
| `chore/` | CI, tooling, no user-facing skill change |

Examples: `feat/grok-packaging`, `fix/verify-spec-image-freshness`, `docs/install-grok`.

### PR description

GitHub auto-loads **[`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)** on every new PR.

Fill it fully — especially **First principles**, **Alternatives considered**, and **How to evaluate this update**. Reviewers (human or next agent) should be able to accept/reject from the reasoning alone, not only from the diff.

Short version of the same bars:

1. **Problem** — what was costly before?
2. **Principle** — why this change is correct in principle?
3. **Evaluate** — accept-if / reject-if criteria
4. **Version + packages** — bump rules + whether `dist/` was rebuilt

## Do PRs help the next agent?

**Yes.** A PR is the unit of handoff:

- **Diff** — what actually changed (not “read the whole tree”)  
- **CI** — whether manifests/versions are coherent  
- **Description** — intent the next agent should not re-derive  
- **Conversation** — decisions and “don’t do X” notes  

Direct-to-`main` leaves the next agent with only `git log` and guesswork. Prefer PRs whenever more than one agent/session might touch the repo.

## Versioning (semver for this plugin)

**Single version** lives in:

`plugins/process-design/.claude-plugin/plugin.json` → `"version": "X.Y.Z"`

That number is what Claude Code’s plugin update compares. If you change files under `plugins/process-design/` and **don’t** bump it, CI’s **version-guard** fails — and installed clients would never pull the new content even if CI were skipped.

Individual skills may carry a `version:` field in `SKILL.md` frontmatter for humans; that is **optional documentation**. The **plugin** version is the one that matters for distribution.

### How to choose X.Y.Z

Current example: **0.11.0**

| Bump | When | Examples |
| --- | --- | --- |
| **PATCH** `0.11.0 → 0.11.1` | Fix, clarify, or package-only; behavior of the procedure stays the same | Typo in SKILL.md, fix `verify_spec.py` edge case, rebuild `dist/grok` with no skill logic change, runtime-map wording |
| **MINOR** `0.11.0 → 0.12.0` | New capability, backward-compatible | New skill, new Step, new package surface (e.g. Grok install), new DMAIC phase, new script |
| **MAJOR** `0.11.0 → 1.0.0` | Breaking change for people already using the skills | Rename skill, remove a Step, change required frontmatter so old specs fail, incompatible deliverable shape |

**Pre-1.0 note:** This plugin is still `0.x`. MINOR can be a bit bolder (new skills often ship as MINOR). Still avoid silent breaks; if you break old specs, bump MAJOR or document a migration in the PR and README Versions.

### Checklist when you bump

1. Edit `plugins/process-design/.claude-plugin/plugin.json` `"version"`  
2. Add a bullet under **Versions** in `README.md`  
3. Run `./build.sh` so `dist/process-design.plugin` and `dist/grok/*` match source  
4. Optional release tag after merge: `v0.12.0` (must match plugin.json — see CI `tag-check`)  

### What does *not* need a version bump

- Root `README.md` / `CONTRIBUTING.md` / `docs/**` only  
- `.github/workflows/**` only  
- `meta-spec/**` only  
- Comments that don’t change installable skill behavior **and** live outside `plugins/`  

If you’re unsure: **any change under `plugins/process-design/` → bump at least PATCH.**

### Grok packages vs Claude plugin version

Same source tree, same version number. When you cut a release:

| Consumer | What they get |
| --- | --- |
| Claude Code marketplace | Pulls when plugin version increases |
| Grok Skills (manual upload) | Must re-download `dist/grok/*.skill` — no auto-update yet |
| Cowork drag-and-drop | Re-download `dist/process-design.plugin` |

Mention “re-upload Grok skills” in the README Versions note when the change affects runtime behavior.

## Dual runtime (Claude + Grok)

- **Source of truth:** `plugins/process-design/skills/<name>/`  
- **Do not fork** a separate “Grok-only” skill tree  
- Claude-native procedure text stays; tool remapping lives in `shared/agent-runtimes.md` (copied into each skill’s `references/`)  
- After skill edits: `python3 scripts/package_for_grok.py` or full `./build.sh`  

See [docs/INSTALL-GROK.md](docs/INSTALL-GROK.md).

## Local commands

```bash
# Validate + build Claude plugin + Grok .skill packages
./build.sh

# Grok packages only
python3 scripts/package_for_grok.py

# Structural check on a process spec (from a skill’s scripts/)
python3 plugins/process-design/skills/process-design/scripts/verify_spec.py path/to/spec.md
```

## What not to do

- Don’t commit secrets or vault-specific paths into skills  
- Don’t strip Claude-specific steps “to make Grok happier” — use the runtime map  
- Don’t mark a `build-workflow` spec `implemented` on Grok without a live runnable test on that host  
- Don’t leave `dist/` stale after skill edits that ship to users  

## License

By contributing, you agree contributions are MIT, same as the repo.
