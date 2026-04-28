"""Render the Phase 8 build-handoff prompt for a verified spec.

Usage:
  python render_handoff.py <spec.md> --target {claude-code|claude-design|python-script|lambda|n8n|other}

Reads the spec's frontmatter and Build Notes, picks the target-specific capture
mechanism examples, and emits the prompt text the user can paste into the build
agent. Architecture-only — never prescribes implementation mechanism.

Stdlib only.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_spec import read_spec, section


CAPTURE_EXAMPLES = {
    "claude-code": "hooks (`PreToolUse`, `PostToolUse`, `Stop`), MCP servers, structured tool result parsing",
    "claude-design": "built-in event tracking, session telemetry",
    "python-script": "decorators, context managers, structured logging libraries (e.g., structlog)",
    "lambda": "middleware wrapping the handler, CloudWatch Metrics, X-Ray segments",
    "n8n": "built-in execution data, custom webhook nodes for downstream telemetry",
    "zapier": "built-in zap history, custom webhooks for richer events",
    "other": "a structured logging library, OpenTelemetry, or whatever idiom fits the runtime",
}


PROMPT_TEMPLATE = """\
Implement the process described in `{spec_path}`. Honor every decision rule, edge case,
gate, and terminal state strictly. The Metrics Map specifies what gets measured at every
step — implement deterministic capture using a mechanism appropriate to the build target.

Architectural requirements (non-negotiable):

1. **Honor the spec.** Decision rules, edge case handling, gates, success criterion, and
   metrics specifications are non-negotiable. Implementation language, library choice,
   file structure, and capture mechanism are your call.

2. **Deterministic metrics capture.** Use {capture_examples} for telemetry. Capture must
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
- Build target:           {build_target}
- Diagram type:           {diagram_type}
- Spec status:            {status}
"""


def render(spec_path: Path, target: str) -> str:
    fm, body = read_spec(spec_path)
    target = target.lower()
    capture = CAPTURE_EXAMPLES.get(target, CAPTURE_EXAMPLES["other"])
    return PROMPT_TEMPLATE.format(
        spec_path=spec_path,
        capture_examples=capture,
        build_target=fm.get("build_target", target),
        diagram_type=fm.get("diagram_type", "(unspecified)"),
        status=fm.get("status", "(unspecified)"),
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Render a build-handoff prompt.")
    parser.add_argument("spec", type=Path)
    parser.add_argument(
        "--target",
        required=True,
        choices=sorted(CAPTURE_EXAMPLES.keys()),
        help="build-target identifier",
    )
    args = parser.parse_args(argv)

    if not args.spec.is_file():
        print(f"no such file: {args.spec}", file=sys.stderr)
        return 2

    print(render(args.spec, args.target))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
