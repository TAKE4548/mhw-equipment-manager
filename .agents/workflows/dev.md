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
- **Starting Step Assignment Logic**:
  - If the item is a NEW enhancement or major redesign -> Step 3 (Architect).
  - If it is a fix or minor change involving **ANY UI adjustment** or UI specification update -> **Step 4 (UX Designer)**.
  - If it is a PURE logic fix with **NO UI changes** and no design impact -> Step 6 (Engineer).
- **Git Branching:** 
  - Create and switch to a new feature branch: `git checkout -b <feat/fix>/REQ-XXX`.
  - Confirm the branch is created before proceeding.

Step 2: [Role: Dev Coordinator]
- **Deliverables Verification Check:**
  - [ ] `docs/backlog.md` is updated with the target requirement.
  - [ ] The requirement has clear "Acceptance Criteria".
  - [ ] The item status is `in-progress`.
- If any item is missing, STOP and request a BA to refine the backlog.
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
- **Phase Deliverables Check:**
  - [ ] `docs/designs/{feature-name}.md` contains Architecture, Data Flow, and Testing Requirements.
  - [ ] (If UI changes) `docs/ui_spec.md` is updated with specific interaction flows.
- Present the Architect's technical design AND the UX Designer's UI spec to the user.
- **MANDATORY STOP & TURN-END**:
    - **One-Action Policy**: This presentation MUST be the final action of your current turn. Do NOT call `task-implementation-plan` or any other tool in the same turn.
    - **Wait for user approval**: Do NOT proceed until the user provides an affirmative word (e.g., "OK", "進めて").
- Update `Current step` to `Step 5`.
- If the user rejects the logic -> return to Step 3. If they reject the UI -> return to Step 4.
- Once approved, proceed to **Step 6**.

Step 6: [Role: Engineer]
- Execute `task-implementation-plan` to map out coding tasks.
- Execute `task-tdd-implementation` for logic code.
- Execute `task-manual-test-design` and `task-browser-debug` for UI interactions.
- Strictly follow `docs/designs/{feature-name}.md` and `docs/ui_spec.md`.
- Signal "implementation complete" when ready.

Step 6b: [Role: Dev Coordinator]
- **Condition**: Proceed only if the task involves UI changes or if the user requests visual adjustments.
- **Visual Polish Loop**:
    1. Present the current UI state (via screenshots/browser verification) to the user.
    2. Collect feedback.
    3. **Triage Feedback**:
        - **Refinement (Aesthetic)**: (e.g., margins, colors, labels) -> Return to **Step 6 (Engineer)** for a quick fix.
        - **Structural/Functional**: (e.g., layout reorganization, new buttons, data flow change) -> Return to **Step 4 (UX Designer)** or **Step 3 (Architect)** for formal redesign.
    4. **MANDATORY TURN-END**: After presenting the results, pause for user reaction. Do NOT proceed to Step 7 without visual confirmation or explicit "Done" from the user.

Step 7: [Role: Tester/Reviewer]
- **Handoff Acceptance Check (MUST verify):**
  - [ ] Engineer has provided Unit Test Logs.
  - [ ] Engineer has provided Browser Debug Results (for UI tasks).
- Execute `task-code-review`.
- **IMPORTANT:** The Engineer MUST NOT self-review. Only the Tester/Reviewer role can issue a review verdict. 
- **MANDATORY TURN-END**: 
    - Output the **Review Verdict (Pass/Fail)** as a standalone message and then END your turn immediately.
    - Do NOT proceed to Step 8 in the same turn.
- **DO NOT proceed to Step 8** without a "Pass" verdict.

Step 8: [Role: Dev Coordinator]
- **SSoT Integrity Gate (MANDATORY before commit):**
  1. Confirm `docs/ui_spec.md` matches the FINAL implemented state.
  2. Confirm `docs/designs/*.md` is consistent with what was actually built.
  3. **Update `docs/backlog.md`**: Change status to `done`, append the completion date, and set `Current step` to `none`. Update any other stale documents NOW.
- **Walkthrough Creation:** Create the walkthrough ONCE at this step only.
- **Git Committing (FINAL ACTION):** 
  - Ensure all documentation updates (Backlog, Designs, Specs) are staged.
  - Commit all changes: `git add . && git commit -m "<type>: implement REQ-XXX - [Short Description]"`.
  - Present the commit hash to the user.
- Present a final completion summary to the user (including instruction on how to merge the branch).
