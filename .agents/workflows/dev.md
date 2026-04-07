---
description: >
  Start a formal development session. Pick a requirement from the backlog
  and take it through design, implementation, review, and completion.
  Start with: /dev or resume an existing session.
---

# Development Session Pipeline

Step 0: [Role: Dev Coordinator]
- Read `docs/backlog.md`.
- If an item with `Status: in-progress` and `Current step: {N}` is found, ask the user: "Would you like to resume REQ-XXX from Step {N}?"
- If the user says Yes, jump directly to that step. Otherwise, proceed to Step 1.

Step 1: [Role: Dev Coordinator]
- Present actionable items (new, ready, fix-needed) to the user.
- The user selects an item (PO decision).
- Update the item's status to `in-progress` and `Current step` to `Step 1`.
- Determine the starting step based on the item type (e.g., jump to Step 6 for a minor fix, or Step 3 for a new enhancement).

Step 2: [Role: Dev Coordinator]
- Confirm that previous phase deliverables are safely stored in `docs/`.
- Update `Current step` to `Step 2`.
- Announce the role switch and hand off.

Step 3: [Role: Architect]
- Read `docs/architecture.md`.
- Execute `task-system-design` to produce `docs/designs/{feature-name}.md`.
- Handoff complete.

Step 4: [Role: UX Designer]
- *Condition: Proceed only if the requirement involves UI changes or user interactions.*
- Execute `task-ux-design`.
- Ensure interaction specs (1-click workflows, dialog logic) align with the Architect's system boundary.
- Update `docs/ui_spec.md` and `docs/design_system.md`.
- Handoff complete.

Step 5: [Role: Dev Coordinator]
- Present the Architect's technical design AND the UX Designer's UI spec to the user.
- **STOP and wait for user approval.**
- Update `Current step` to `Step 5`.
- If the user rejects the logic -> return to Step 3. If they reject the UI -> return to Step 4.

Step 6: [Role: Engineer]
- Execute `task-implementation-plan` to map out coding tasks.
- Execute `task-tdd-implementation` for logic code.
- Execute `task-manual-test-design` and `task-browser-debug` for UI interactions.
- Strictly follow `docs/designs/{feature-name}.md` and `docs/ui_spec.md`.
- Signal "implementation complete" when ready.

Step 7: [Role: Tester/Reviewer]
- Execute `task-code-review`.
- Output: Pass or Fail with details.

Step 8: [Role: Dev Coordinator]
- Handle the review outcome.
- On success: Update `docs/backlog.md` status to `done`, append date, and set `Current step` to `none`.
- Update `docs/architecture.md` if the overarching structure has changed.
- Present a final completion summary to the user.
