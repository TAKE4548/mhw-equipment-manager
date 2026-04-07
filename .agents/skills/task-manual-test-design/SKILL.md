---
name: task-manual-test-design
description: >
  Design manual test cases for UI and interaction behavior
  that cannot be covered by unit tests. Use when implementation
  plan identifies components requiring browser-based verification.
---

# Manual Test Design Task

## Use this skill when
- Testing UI components, layouts, dialog behavior, or screen transitions.
- Verifying user interactions (clicks, inputs, responsive adjustments).
- Creating test procedures for the browser sub-agent to execute.

## Output Format
Each manual test case should follow this structure:

### MT-{number}: {Test Name}
- **Pre-condition**: {State before test begins}
- **Steps**:
  1. {Action 1}
  2. {Action 2}
  ...
- **Expected Result**: {What visual or interactive state must be confirmed}
- **Related Acceptance Criteria**: {Reference to the design doc}
