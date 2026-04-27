# Test Writing (TDD)

> Write failing tests first that define the expected behavior, then implement the code to make them pass. Run the test suite before committing. All tests must pass.

---

## Why TDD Matters for Process Spec Design

Test-driven development is usually applied to code. Applied to process spec design, it produces a different and useful discipline: **define what makes the spec complete and correct *before* drafting it.**

The default failure mode without TDD: write the spec, then check it. The check happens against an implicit, fuzzy standard ("does this look right?"). This is biased — the writer evaluates their own work against the same mental model that produced it.

The TDD approach: define the verification suite (the tests the spec must pass) before drafting. Then draft to satisfy the suite. Then run the suite to confirm.

This works because:

1. **The test definition forces specificity.** "The spec must be complete" is not a test. "Every step has a named requirement owner and a named failure mode if removed" is a test. The act of writing the test surfaces what "complete" actually means.

2. **The bar is set before the work starts.** The writer knows what they're aiming at. The verification is not a subjective post-hoc judgment; it's a checklist defined in advance.

3. **Failing tests are diagnostic.** When a test fails, the writer knows precisely what's missing. "The Metrics Map test failed because the controllable input metrics section has no entries" is actionable. "The spec feels incomplete" is not.

---

## Adapting for `process-design`

The skill's Phase 5 (Format Selection) should produce, in addition to the diagram type choice, a **verification suite** for the spec. Concrete checks the draft must pass, defined before drafting begins.

Many checks fall out automatically from the principles in `spec-principles.md`:
- Every step has a named requirement owner
- Every decision rule is testable on input alone
- Every input has documented validation
- The Metrics Map has entries in all four categories
- Every controllable input has at least one tracked dimension
- Every diagram node displays its owner annotation

Process-specific checks may need to be added based on what surfaced in Phases 1-4:
- Specific edge cases that came up during stress-testing
- Specific failure modes that need explicit handling
- Specific metric refinement plans that the user identified

Phase 6 (Draft) then writes the spec to pass the suite. Phase 7 (Verify) runs it.

If a check in the suite is genuinely impossible to satisfy in the current spec, that's data — either the check is wrong (suite needs revision) or the spec has a real gap (spec needs revision). Both surface in Phase 7.
