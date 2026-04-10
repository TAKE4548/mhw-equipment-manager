---
name: dev
description: >
  Formal development session workflow. Tracks progress via session.md.
  Includes Escalation and Architecture Feedback loops.
---

# Development Workflow (/dev)

This workflow manages the lifecycle of a requirement from selection to deployment.

## Step 0: Session Initialization [Role: Dev Coordinator]
- Read `docs/session.md` and `docs/backlog.md`.
- **Resumption Logic**: If `docs/session.md` contains an active REQ and a specific `Current Step`, ask the USER: "Would you like to resume {REQ-ID} from {Step Name}?"
- If the USER says Yes, jump to that step. Otherwise, proceed to Step 1.
- **Protocol**: Update `docs/session.md` with "active" status and Current REQ.

## Step 1: Item Selection & Setup [Role: Dev Coordinator]
- Present `ready` or `fix-needed` items from `docs/backlog.md`.
- The USER selects a target (REQ).
- **Git Setup**: 
  - Create feature branch: `git checkout -b <feat/fix>/REQ-XXX`.
- **Session Update**: Initialize `docs/session.md` for the new REQ.
- **Starting Step Selection**:
  - New feat/redesign -> Step 3 (Architect).
  - UI refinement only -> Step 4 (UX Designer).
  - Pure logic bug (no UI change) -> Step 6 (Engineer).

## Step 2: Handoff Verification [Role: Dev Coordinator]
- Verify target REQ has clear "Acceptance Criteria".
- Confirm the branch is active.
- Handoff to the next role.

## Step 3: High-Level Design [Role: Architect]
- **Session Entry**: Update `docs/session.md` (Step 3, Architect).
- Execute `role-architect` responsibilities.
- **Feasibility Check**: If the requirement is technically unfeasible -> report `[IMPASSE]` to Coordinator and END.
- Output: `docs/designs/{feature}.md` or `docs/ui_spec.md`.
- **Session Exit**: Update status in `docs/session.md`.

## Step 4: UI/UX Specification [Role: UX Designer]
- *Condition: Skip if no UI changes.*
- Execute `task-ux-design`.
- Update `docs/ui_spec.md` and `docs/design_system.md`.

## Step 5: Approval Gate [Role: Dev Coordinator]
- **Session Entry**: Update `docs/session.md` (Step 5, Coordinator).
- Present Architecture and UI designs to the USER.
- **MANDATORY TURN-END**: Wait for explicit USER approval (Japanese context allowed).
- **One-Action Policy**: No implementation tools in this turn.
- Once approved, proceed to Step 6.

## Step 6: Implementation [Role: Engineer]
- **Session Entry**: Update `docs/session.md` (Step 6, Engineer).
- **Escalation Watch**: If 3 attempts fail, report `[IMPASSE]` and END.
- Implementation: Code + Unit Tests + Browser Verification.
- Evidence: Save screenshots as `MT-{num}_{pass|fail}.png`.
- **Structured Report**: Provide verdict and AC check.
- **Session Exit**: Update `docs/session.md`.

## Step 7: Verification & Review [Role: Tester/Reviewer]
- **Session Entry**: Update `docs/session.md` (Step 7, Reviewer).
- Compare code against designs and verify AC via evidence.
- **Architecture Feedback**: Identify "Concerns (懸念事項)" for future debt.
- **Verdict**: PASS | FAIL (If Fail, return to Step 6).
- **MANDATORY TURN-END**: Terminate turn after providing the verdict.

## Step 8: Finalization & SSoT [Role: Dev Coordinator]
- **Session Entry**: Update `docs/session.md` (Step 8, Coordinator).
- **Record Tech Debt**: If Reviewer reported "Concerns", record them in `docs/backlog.md`.
- **SSoT Sync**: Ensure docs/design/ui_spec match the actual implementation.
- **Backlog Update**: Set status to `done`, update `Current step` to `none`.
- **Git Commit**: `git add . && git commit -m "<type>: implement REQ-XXX"`.
- **Session Exit**: Mark `docs/session.md` as "inactive" (clear it for next session).
- Present final walkthrough and merge instructions.

---

## Escalation Handling Path (IMPASSE Branch)
If an `[IMPASSE]` is reported in Step 3 or Step 6:
1. **Coordinator** updates `docs/session.md` status to `escalated`.
2. **Coordinator** presents specific technical constraints to the USER.
3. **USER Decision**:
   - Change requirement -> Return to Step 1 (BA) or Step 3 (Architect).
   - Accept tradeoff -> Architect updates design, resume from Step 5.
   - Archive/Defer -> Coordinator marks REQ as `archived` in backlog, END session.
