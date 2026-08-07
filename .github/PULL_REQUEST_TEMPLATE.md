<!--
  Agents and humans: fill every section that applies.
  Reviewers evaluate the *reasoning*, not only the diff.
  Delete HTML comments before submit if you want a clean body.
-->

## Summary

<!-- 1–3 bullets: what changed in concrete terms -->

-

## Problem / opportunity

<!-- What was wrong, missing, or costly *before* this PR? Who felt it? -->



## First principles

<!--
  Why this change is correct *in principle*, not only "it works on my machine."
  Prefer claims we can argue with. Examples for this repo:
  - A process is reviewable iff its structure is visible at a glance
  - Prefer scripts for deterministic checks; agents for judgment
  - Delete at the moment of addition (P2) — no ceremony that doesn't produce value
  - Dual runtime: same procedure; tool names map — don't fork Claude vs Grok skill trees
  - main is shippable; installed clients only see version bumps under plugins/
-->

| Principle | How this PR honors it |
| --- | --- |
| | |
| | |

### Alternatives considered

<!-- What we could have done instead, and why we rejected it (1–3 bullets). "None" is fine if trivial. -->

-

### Non-goals

<!-- What this PR deliberately does *not* change. Stops scope creep and bad review expectations. -->

-

## How to evaluate this update

<!--
  Give the reviewer a checklist they can run mentally or literally.
  Bad: "LGTM if CI green."
  Good: observable criteria tied to the problem.
-->

**Accept if:**

- [ ]
- [ ]

**Reject / send back if:**

- [ ]
- [ ]

**Manual / scripted checks run:**

```text
# commands you ran, or "docs only — no runtime check"
```

## Impact surface

<!-- Who/what feels this after merge? Check all that apply. -->

- [ ] Skill procedure (`plugins/process-design/skills/**`)
- [ ] Helper scripts (`**/scripts/**`)
- [ ] Claude marketplace / Cowork plugin (manifest, install path)
- [ ] Grok packages (`dist/grok/**` or packaging scripts)
- [ ] CI / repo hygiene only
- [ ] Docs only

**Blast radius (one line):**



## Version

See [CONTRIBUTING.md](../CONTRIBUTING.md) — single source: `plugins/process-design/.claude-plugin/plugin.json`.

- [ ] No change under `plugins/process-design/` → **no version bump**
- [ ] Fix / clarify / package-only → **PATCH** (`0.x.Y` → `0.x.Y+1`)
- [ ] New capability, backward-compatible → **MINOR**
- [ ] Breaking for existing users/specs → **MAJOR**

**Version in this PR:** `unchanged` / `___.___.___`

- [ ] README **Versions** section updated (if release-worthy)

## Packages

- [ ] N/A (docs / CI only)
- [ ] Ran `./build.sh` (Claude `.plugin` + `dist/grok/*`)
- [ ] Ran `python3 scripts/package_for_grok.py` only

**Grok Skills users need re-upload?** Yes / No / N/A

## Risk & rollback

**Risk level:** Low / Medium / High

**If this is wrong, rollback is:**

<!-- e.g. revert PR; users re-upload previous .skill; no migration needed -->



## Test plan

- [ ]
- [ ]

---

### Agent notes (optional)

<!-- Session context the next agent needs: open questions, follow-ups, files deliberately left alone -->
