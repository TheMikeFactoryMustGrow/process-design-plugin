Implement the process described in `/Users/mikelingle/code/process-design-plugin/skills/process-design-workspace/iteration-2/eval-0-investor-update/with_skill/outputs/gix-investor-update.process-spec.md`. Honor every decision rule, edge case,
gate, and terminal state strictly. The Metrics Map specifies what gets measured at every
step — implement deterministic capture using a mechanism appropriate to the build target.

Architectural requirements (non-negotiable):

1. **Honor the spec.** Decision rules, edge case handling, gates, success criterion, and
   metrics specifications are non-negotiable. Implementation language, library choice,
   file structure, and capture mechanism are your call.

2. **Deterministic metrics capture.** Use hooks (`PreToolUse`, `PostToolUse`, `Stop`), MCP servers, structured tool result parsing for telemetry. Capture must
   not depend on the executing system "remembering" to log — it must fire on every run.

3. **Gates as named.** Each gate in the spec has a named verification method (script,
   agent, or human). Implement them at that fidelity. Don't escalate a script gate to an
   agent or vice versa without surfacing the change.

4. **Graceful degradation.** If telemetry storage is unreachable at runtime, the process
   completes with output and logs a degraded-mode warning. **Output correctness must not
   depend on telemetry working.**

5. **Surface ambiguity.** Don't paper over anything. If the spec's Assumptions and Open
   Questions section names a soft fail, ask before deviating from the literal spec.

Before you start, summarize the spec back to me, including:
- Which gates run as scripts vs. agents vs. humans
- Which telemetry mechanism you propose, and why it satisfies the deterministic-capture
  property
- Any ambiguity you found in the spec that you want clarified before coding

Process metadata:
- Build target:           claude-code
- Diagram type:           flowchart
- Spec status:            verified

