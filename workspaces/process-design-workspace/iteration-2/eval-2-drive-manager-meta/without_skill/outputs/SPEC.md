# Routing Correction Feedback Loop — Spec

A meta-process for capturing wrong routing decisions made by `drive-manager:process-inbox` and feeding them back into the skill's rules so the same mistake does not happen twice.

## 1. Problem statement

The `drive-manager` skill routes files from `~/Desktop/Inbox/` to the right folder on Google Drive / iCloud. Sometimes it routes wrong because the rules lack context (ambiguous filenames, unknown senders, new entities not yet in the index). Today, when the user moves a file to its correct home after the fact, that learning is lost — the skill will make the same mistake again next week.

The fix needs to be small enough to be one Python script, but disciplined enough to leave the rules file in a state that is auditable, reversible, and not corrupted by noisy one-offs.

## 2. Success and failure (DMAIC Define)

- **Success**: Each routing miscall the user fixes is captured as a structured correction record within 60 seconds of the fix, and within one week shows up as either (a) a new rule, (b) a strengthened existing rule, or (c) an explicit "ambiguous — ask the user" entry. Repeat-mistake rate trends to zero.
- **Failure**: Corrections pile up unprocessed; the rules file gets edited by hand without provenance; one weird one-off file mutates a rule and breaks the next ten files; or the user has to remember to log corrections manually.

## 3. The meta-process (5 phases)

```
   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ DETECT   │───▶│ CAPTURE  │───▶│ TRIAGE   │───▶│ PROMOTE  │───▶│ VERIFY   │
   └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
   File moved      Append to       Cluster /        Edit rules     Replay logs;
   away from       corrections.    rank by          file with      assert no
   skill's pick    jsonl           recurrence       provenance     regression
```

### 3.1 DETECT — "the skill was wrong"

Two trigger paths, both supported:

- **Live signal** (preferred): the skill writes a `route-decision.jsonl` audit log every time it moves a file. Each record has `{ts, file_hash, original_path, chosen_path, rule_id, confidence, candidates}`. A `fswatch` daemon (or a periodic scan, see §6) compares the chosen_path with where the file actually lives now. If they differ, that is a correction signal.
- **Manual signal** (fallback): the user runs `python feedback_loop.py log-correction <file>` after they move something. The script looks up the file in the audit log by hash, prompts for the correct destination if needed, and writes the same correction record.

The audit log is the single source of truth. Without it, this whole system does not work — wiring it up is task #1 if it is not already there.

### 3.2 CAPTURE — write a correction record

Append-only `corrections.jsonl`. One record per miscall:

```json
{
  "id": "corr-2026-04-27-001",
  "ts": "2026-04-27T14:03:11Z",
  "file": {
    "name": "Invoice_GIX_Mar2026.pdf",
    "hash": "sha256:abc...",
    "size": 184223,
    "mime": "application/pdf"
  },
  "skill_chose": "/Drive/Inbox-Unsorted/",
  "skill_rule_id": "fallback-unsorted",
  "skill_confidence": 0.31,
  "user_chose": "/Drive/GIX/Finance/Invoices/2026/",
  "signals_available_at_decision": {
    "filename_tokens": ["invoice", "gix", "mar2026"],
    "ocr_keywords": ["GIX Fiber", "Invoice #", "Net 30"],
    "sender": null,
    "created": "2026-04-26"
  },
  "user_note": "GIX invoices always go here, by month",
  "status": "new"
}
```

`status` walks `new → triaged → promoted → verified` (or `→ rejected` / `→ deferred`).

### 3.3 TRIAGE — decide what kind of learning this is

For each `new` record, the script classifies it into one of four buckets. This is the brain of the system; everything else is plumbing.

| Bucket | Meaning | Action |
|---|---|---|
| **A. New rule** | The destination is a folder the rules don't currently target, but the signals are clean (e.g. filename contains an entity name). | Generate a candidate rule. Promote after 1 occurrence if confidence is high; after 2 if medium. |
| **B. Strengthen existing rule** | An existing rule almost matched but lost on confidence. The correction tells us to raise its weight or add a token. | Patch the rule's keyword list / weight. |
| **C. Disambiguation needed** | Two rules tied, and the right answer depends on context the rules can't see (e.g. same vendor, different projects). | Add an explicit `ask_user` entry so the skill stops guessing on this signature. |
| **D. One-off / noise** | The file is genuinely unusual — wedding photo dropped in by mistake, etc. Not a pattern. | Mark `rejected` with reason. Do **not** touch rules. |

Triage is fuzzy. The script uses three heuristics, in order:

1. **Recurrence check** — has a similar correction (same target folder, overlapping signal tokens) appeared ≥ 2 times in the last 90 days? If yes, lean toward A or B.
2. **Signal cleanliness** — does the correction record contain at least one strong, low-collision signal (entity name, distinctive keyword, sender domain)? If no, lean toward C or D.
3. **User note** — if the user attached a note like "always go here," that's an explicit teach. Bias toward A.

Triage runs in a "review session" the user opens on demand (e.g. weekly). The script presents each `new` correction, suggests a bucket, and asks for thumbs-up / edit / reject. Nothing auto-promotes without confirmation. This is the guard against one-off files mutating rules.

### 3.4 PROMOTE — edit the rules file with provenance

Rules live in a structured file (assumed YAML; format-agnostic). Every edit must:

- Be done through the script, not by hand.
- Carry a `provenance` block listing the correction IDs that justified it.
- Be a single semantic operation: add rule, modify rule, add ask_user entry, raise weight. No bulk rewrites.
- Be wrapped in a git commit (or a timestamped backup if the rules file isn't in a repo) so it is reversible.

Example rule with provenance:

```yaml
- id: gix-invoices
  match:
    filename_tokens_any: [invoice, "inv-"]
    filename_tokens_all: [gix]
  route_to: "/Drive/GIX/Finance/Invoices/{YYYY}/"
  weight: 0.8
  provenance:
    created_from: [corr-2026-04-27-001, corr-2026-04-15-007]
    last_modified: 2026-04-27
```

The promote step also bumps the matching correction records to `status: promoted` and stamps them with the resulting rule_id, closing the loop.

### 3.5 VERIFY — make sure the fix actually fixed it (DMAIC Control)

The regression guard. Before the script exits a promote action, it does a **dry-run replay**:

1. Take every correction record where `user_chose == <new rule's target folder>` from the past 90 days.
2. Re-run the rules engine against the original signals.
3. Assert: ≥ 90% of those would now route correctly. If not, the new rule is too narrow; warn and ask the user before committing.
4. Also re-run against a sample of *correct* historical decisions to make sure the new rule doesn't pull in files that were already going to the right place. (Catch overcorrection.)

After promotion, mark records `verified` once the same signature shows up again and is routed correctly.

## 4. Data model summary

| File | Purpose | Owner |
|---|---|---|
| `route-decision.jsonl` | Append-only log of every routing decision the skill makes | `drive-manager:process-inbox` |
| `corrections.jsonl` | Append-only log of detected miscalls | This script |
| `rules.yaml` (or whatever the skill uses) | The active routing rules | This script writes; skill reads |
| `rules.yaml.bak/` | Timestamped backups of every rules edit | This script |

All four live in `~/.drive-manager/` (assumed; configurable).

## 5. Python script CLI

One script, `feedback_loop.py`, with subcommands:

```
feedback_loop.py detect           # scan audit log, find files moved away from skill's pick, write new corrections
feedback_loop.py log-correction <path>   # manual entry path
feedback_loop.py review           # interactive triage of all `new` corrections
feedback_loop.py promote          # apply triaged corrections to rules.yaml (with verify)
feedback_loop.py verify [--rule <id>]    # rerun replay against history
feedback_loop.py status           # show counts: new / triaged / promoted / rejected, plus top recurring signatures
```

A typical week: `detect` runs nightly via launchd; user runs `review` Friday afternoon; `promote` happens at the end of the review session and runs `verify` automatically.

## 6. Assumptions (documented because the user couldn't be asked)

1. The `drive-manager` skill can be made to write a `route-decision.jsonl` audit log. If it can't today, that is a prerequisite — the spec calls this out as task #1. A degraded mode (manual `log-correction` only) works without it but loses ~80% of the value.
2. Rules live in a structured file we can read and write. YAML is assumed; the script abstracts file I/O behind a `RulesStore` class so swapping JSON / TOML is one method change.
3. The user is OK with a human-in-the-loop triage step. Auto-promotion is explicitly rejected — one-off files would otherwise corrupt rules.
4. "Same file" identity uses sha256 of contents. Renames are tracked; edits to the file between routing and correction make it un-trackable, which is fine (skip those).
5. Backups are local; not pushed anywhere. If the rules file is in a git repo, the script commits instead of backing up.
6. The script is single-user, single-machine. No locking beyond a simple flock on `corrections.jsonl` for the append.

## 7. Metrics to watch (DMAIC Measure)

Three metrics, recomputed by `feedback_loop.py status`:

- **Capture rate** — corrections logged ÷ corrections that should have been logged (estimated from `route-decision.jsonl` entries where chosen ≠ final path). Target: ≥ 95%.
- **Promotion latency** — median days from correction.ts to rule edit. Target: ≤ 7 days.
- **Repeat-miss rate** — among corrections in the last 30 days, what fraction has a correction in the prior 90 days with overlapping signals? Target: ≤ 5% and trending down. This is the one that proves the loop works.

## 8. What this is not

- Not a replacement for the `drive-manager` skill's runtime decision logic. It only edits rules; the skill still does the routing.
- Not an ML system. It is deliberately a rule-edit ledger with a triage step, because a pile of YAML rules is auditable in a way a model is not.
- Not auto-pilot. Every rule change is human-confirmed. The point is to make confirming cheap, not to remove the human.
