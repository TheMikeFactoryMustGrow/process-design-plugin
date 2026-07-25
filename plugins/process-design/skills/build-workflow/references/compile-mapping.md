# Spec → Workflow script compile mapping

The canonical mapping from process-design spec elements to Workflow script
constructs. The left column is what the spec guarantees; the right column is the
only correct translation. Deviations go through the user (Build Notes: "ask before
deviating").

| Spec element | Script construct |
|---|---|
| Step with `if <cond> → <step_id>` successors | `if`/`else` or `while` on validated schema fields |
| Gate, `method: script` | Plain JS check between `agent()` calls |
| Gate, `method: agent` | One `agent()` call with a verdict schema (boolean or enum) |
| Gate, `method: human` | Split point: return a `needs-decision` payload; resume with the decision in `args` |
| Decision rule | Schema enum field; the script branches on the field |
| Parallel section | `pipeline()` by default; `parallel()` only for a true join |
| Join point | The barrier of one `parallel()` call |
| Edge case | Input validation branch, tested with a seeded input |
| Metric (per step) | `log()` line plus a field in the returned run record |
| Input | `args` field with top-of-script validation |
| Terminal state | Return payload with `state: "<terminal_id>"` |

---

## Pattern: defensive args

Some harness paths deliver `args` as a JSON string. Always open with:

```js
const input = typeof args === 'string' ? JSON.parse(args) : args
const task = input && input.task
if (!task) throw new Error('Pass args.task — <what it is>.')
```

## Pattern: verdict gate (method: agent)

```js
const verdict = await agent(
  `Judge the draft against <criterion>. Fail only for real defects, not taste.\n\nDRAFT:\n${draft.output}`,
  { label: 'gate:quality', phase: 'Review', schema: {
      type: 'object',
      properties: { pass: { type: 'boolean' }, feedback: { type: 'string' } },
      required: ['pass', 'feedback'] } },
)
if (!verdict.pass) { /* fail edge — loop or escalate per the spec */ }
```

## Pattern: retry loop with feedback (Pass? no → feedback → Worker)

The reviewer fan-in is a TRUE join — the synthesis needs all reviews — so the
`parallel()` barrier is correct here.

```js
let draft = null, feedback = null, passed = false, round = 0
while (round < MAX_ROUNDS && !passed) {
  round++
  draft = await agent(workerPrompt(task, plan, draft, feedback),
    { label: `worker (round ${round})`, phase: 'Work', schema: WORK_SCHEMA })
  const reviews = (await parallel(
    LENSES.map((lens, i) => () => agent(reviewPrompt(lens, draft),
      { label: `reviewer ${i + 1} (round ${round})`, phase: 'Review', schema: REVIEW_SCHEMA })),
  )).filter(Boolean)
  const synth = await agent(synthPrompt(task, draft, reviews),
    { label: `synthesise (round ${round})`, phase: 'Synthesise', schema: SYNTH_SCHEMA })
  passed = synth.pass
  feedback = synth.feedback
}
```

Full worked example of this shape, when the project carries it:
`.claude/workflows/graph-max.js`.

## Pattern: human gate split (method: human)

```js
if (!input.decision) {
  // First invocation stops at the gate. The session asks the human and re-invokes.
  return {
    state: 'needs-decision',
    gate: '<gate_id>',
    question: '<what the human must decide>',
    context: preGateResults,
    resumeWith: 'args.decision = "<option>"',
  }
}
// Second invocation continues past the gate with input.decision set.
```

## Pattern: seeded-defect test (fail-branch coverage)

Write a test task that instructs the worker to produce a deterministically wrong
output on round 1 only, and tells reviewers the exact-match criterion. The run must
fail round 1, loop the feedback back, and pass round 2. This exercises the fail
edge, the feedback threading, and the loop exit in one cheap run.

## Sizing

Count agents per run before launching: steps × rounds + gates + delivery. Stay
inside the session's workflow size guideline. When the spec implies more, say so
and get sign-off — do not silently cap coverage (log what a cap drops).
