---
name: task-code-review
description: >
  Review completed implementation against architect and UX specifications
  and check test quality. Use when engineer has finished
  implementation and all tests pass.
---

# Code Review Task

## Input
- `docs/designs/{feature-name}.md` (Architect's design)
- `docs/ui_spec.md` (UX Designer's spec)
- Implementation code + test code
- Test execution results (Unit + Browser)

## Review Items
1. **Design Conformity**: Does the logic/DB layer match the Architect's design? Does the visual layer match the UX Designer's specific instructions?
2. **Acceptance Criteria**: Are all ACs from the backlog fulfilled?
3. **Test Quality**:
   - Are the tests comprehensive?
   - Do they avoid anti-patterns (brittle assertions, heavy dependency on internal implementation details)?
4. **Edge Cases**: Empty states, out-of-bounds inputs, race conditions.
5. **Regressions**: Are existing features unaffected?

## Output
- **Passed**: Declare "Review Passed" and proceed to completion.
- **Failed**: Output a clear list of deficiencies along with concrete correction proposals. Hand back to the Engineer.
