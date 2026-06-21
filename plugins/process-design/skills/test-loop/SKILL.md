---
name: test-loop
description: >
  Turn a built implementation into a trustworthy one. Write the executable regression suite
  that locks the spec's decision rules and the project's conventions into tests, measure
  coverage (statements AND branches), and treat every failure the tests surface as a finding
  to fix at the root. This is the executable companion to dmaic-control: DMAIC *defines* the
  regression guard (what to monitor); this skill *builds* it — the tests that stop a regression
  from ever shipping. Use after a build agent implements a process-design spec, after writing
  or changing any code you intend to rely on, or when the user says "add tests", "get this to
  100% coverage", "lock in the conventions", "write a regression suite", "harden this",
  "make this trustworthy", or "add logging / improve observability". Trigger proactively the moment code is declared "done" but before
  it is relied on — the test pass is where the real bugs fall out.
compatibility: >
  Runs in any environment with the project's test runner and a coverage tool
  (pytest + coverage/pytest-cov, node --test/c8, jest, go test -cover, cargo tarpaulin, etc.).
  The loop is language-agnostic; only the commands change. No subagents required, though a large
  finding list can fan fixes out to Task when available.
version: 0.1.0
---

# Test Loop — Build the Executable Regression Guard

DMAIC's Control phase *defines* a regression guard. This skill *builds* the code half of it: the automated test suite that locks behavior so a future edit can't silently break it. The loop has **two products, not one** — the regression suite, and the bugs it surfaces while you write it. The second is often the more valuable.

This skill ships inside the `process-design` plugin. It is the executable downstream of two siblings: `process-design` hands a spec to a build agent (its Step 7 build prompt should require this suite), and `dmaic-control` defines the monitoring guard (this skill builds the test guard that fires earlier). When `qa-agents` confirms a flaw whose root cause is "missing/weak coverage," this skill is the fix.

---

## First Principles

The procedure derives from these, not from a coverage-percentage target:

- **P1.** A test is worth writing iff it would **fail on a plausible wrong implementation**. A test that passes no matter what the code does is theater. (Powers deletion of vanity tests.)
- **P2.** The highest-value tests lock **decision rules and conventions** — the values and rules a future edit could break without anyone noticing. Coverage of imperative/presentation code is secondary.
- **P3.** Coverage is a **floor, not a goal.** 100% line coverage with weak assertions is worse than 80% with sharp ones, because it lies. A branch the data can never reach is not a real gap.
- **P4.** A failing test *while writing the suite* is **the point, not an annoyance** — it's a real bug caught before production.
- **P5.** Untestable code is a **design smell.** If you must contort to test it, refactor for testability first.
- **P6.** A path you can't **observe** is a path you can't debug. Every important path — each decision rule, gate, and failure branch — should emit a **useful log** (what happened, with the values that decided it), and that log is itself an asserted behavior, not a side effect left to chance.

---

## When to use / not use

**Use** after a build agent implements a spec; after writing or changing code you intend to rely on; when hardening something for a recurring/automated job (where silent drift is the risk).

**Don't use** on throwaway scripts, exploratory spikes, or one-off analyses you won't run again. The loop earns its cost only when the code will be re-run or re-edited.

---

## The Loop

### Phase 0 — Anchor on what must not break

Before touching the test runner, list the **invariants**: the spec's decision rules plus the project's locked conventions (the weights, thresholds, exclusion sets, ID schemes, auth rules — anything a regression would violate).

- If there's a `process-design` spec, lift them from its decision rules and Metrics Map.
- If there's no spec, ask the user for the invariants directly. Don't guess them from the code — that bakes the current behavior in as "correct" even if it's the bug.

These become the must-have assertions. Write them down first.

### Phase 1 — Make it testable

Extract the pure logic out of scripts/handlers into importable functions. **Backward-compatible only** — the entry point (`main`, the CLI, the handler) must still work exactly as before. Prove behavior is unchanged by pinning a known-good output (Phase 2) before and after the refactor.

### Phase 2 — Write the locking tests (highest value first)

- **One test per decision rule / convention**, asserting the *specific* expected value — not "runs without error." `assert weight("Signed") == 0.90`, not `assert weight("Signed") is not None`.
- **Pin known-good outputs as regression anchors.** Assert the exact totals / IDs / counts the artifact currently produces, and **cite where the expected number came from** (the deployed value, the spec, a hand calc). An anchor with no provenance is a guess dressed as a test.
- **For gates / auth / validation: test both paths** — the reject path *and* the accept path. A gate only tested on the happy path isn't tested.

### Phase 3 — Measure

Run coverage with **branches on** (`--cov-branch`, `c8`, `-cover` with branch mode). Statement coverage alone hides untaken branches — the exact place regressions hide.

Target: **100% on logic-bearing modules.** Be pragmatic on imperative/presentation code (PDF/HTML/plot drawing) — smoke-test the artifact (it builds, it's valid, it carries the headline facts) instead of asserting layout internals. Chasing the last lines there produces brittle tests, not safety.

### Phase 4 — Close the gap (this is the loop)

Each **uncovered line/branch** is a question. Answer it, don't paper over it:

| The uncovered thing is… | Do |
|---|---|
| a missing test | write the test |
| dead code | **delete it** — never pad coverage with code nothing calls |
| a genuinely-unreachable defensive guard | exclude it (`# pragma: no cover` / `c8 ignore` / etc.) **with a comment**, and list it transparently in the report |

Each **failing test** is a finding → fix the **root cause**, not the test. If the same class of failure recurs, route it through root-cause analysis (qa-agents Phase 5) before continuing. Re-run. Repeat until the invariants are locked and the coverage target is met **with every exclusion named**.

### Phase 4b — Cover the logging (observability is part of the guard)

Tests prove a path is *correct*; logs are how you find out *which* path ran when something goes wrong in production. **Review the system's logging and add missing coverage until every important path produces useful, tested logs.**

- **Walk the important paths** — the same list from Phase 0 (decision rules, gates, failure/error branches) plus anything that retries, falls back, or silently swallows. Each should answer, in the logs, *what happened and which values decided it*.
- **A useful log is specific.** Log the deciding values (the weight applied, the gate's verdict, the row count excluded, the error and its context), at the right level: `error`/`warn` for failures and rejected paths, `info` for the decisions a reader would want to reconstruct, `debug` for the rest. A bare `"done"` or a swallowed exception with no log is a gap.
- **Test the logs you rely on.** A log that matters is an assertion: capture output (`caplog`, a test handler/transport, captured stdout) and assert the important path logged what it should — especially the **failure and rejected-gate paths**, where logs are the only forensic trail. Don't assert on cosmetic phrasing; assert the *fact and the value*.
- **Each missing log is a finding**, handled like an uncovered branch: add the log if the path matters, or decide the path doesn't warrant one — and say which in the report. Don't pad with noise logs nothing reads, the logging twin of vanity tests (P1).

### Phase 5 — Lock it in

Wire the suite into the project so it runs without being remembered: a test script in the manifest, a `fail_under` / coverage threshold, and a pre-commit or CI hook if the project has one. Then report (see Output).

---

## Honesty Rules — what "100%" must mean

A coverage number is a claim. These keep it true:

- **Never pad** with dead code or vanity tests to hit a number. Delete or exclude-with-reason instead.
- **Every exclusion is named and justified** in the report — the reader sees exactly what "100%" did and didn't cover.
- **Pinned anchors carry provenance.** Cite the source of every hard-coded expected value.
- **Weak assertions are a smell** (`not None`, `len > 0`) unless that truly is all the spec constrains.
- **Report the bugs, not just the green check.** The findings surfaced while writing the suite are a first-class deliverable.

---

## Output

1. The test files + coverage config, committed (with the test command wired into the manifest).
2. A short report:
   - Coverage: statements **and** branches, per logic module.
   - **Excluded-lines list** with a one-line reason each.
   - **Bugs surfaced and fixed** during the pass (the high-value half).
   - **Logging coverage:** important paths that gained logs (and any tested), plus paths deliberately left unlogged with the reason.
   - Refactors made for testability (and how behavior was proven unchanged).

---

## Relationship to the Sibling Skills

- **`dmaic-control`** *defines* the regression guard (monitor / alert / review). This skill *builds* the code half. For a coded process, the **test suite is the primary regression guard**; monitoring and alerts then cover the runtime drift tests can't see. The two are complementary, not redundant.
- **`process-design`** Step 7 hands a spec to a build agent. The build prompt should require a spec-locking test suite; run this skill on the result to produce it.
- **`qa-agents`** finds flaws. When a confirmed flaw is "missing/weak test coverage," or when Phase 5 RCA names "prevent recurrence with a test," the fix is this skill.

---

## Worked Example (generic data-pipeline)

A small data pipeline (data-transform script + a serverless data function gated by a password + a PDF generator) was declared "done."

- **Phase 0:** invariants = the stage-probability weights, the row-exclusion set, the headline totals, and the gate (no password → reject; correct password → data).
- **Phase 1:** the transform script ran top-to-bottom on import; extracted `load / build / weight / render` into importable functions, behavior pinned identical via the known-good total.
- **Phase 2:** one assertion per weight, per exclusion, and the exact headline total (anchored to the already-shipped value); the gate tested on both the reject and accept paths.
- **Phase 3–4:** branch coverage surfaced a **real deploy bug** — the serverless function was CommonJS while the package declared `"type": "module"`, which would crash on the host at runtime. Fixed to ESM. A dead helper function was **deleted** (not covered-by-vanity-test). Two unreachable defensive guards were excluded with comments and listed.
- **Result:** 100% statements **and** branches on the logic modules; a smoke test on the PDF generator (valid file, carries the headline facts) rather than layout assertions; the deploy bug and the dead code both reported.

The product wasn't "100%." The product was a suite that locks the conventions **and** two real defects caught before anyone relied on the code. That's the bar.
