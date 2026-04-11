---
name: dev
description: "Formal development session workflow. Tracks progress via session.md. (v1.7)"
---

# Development Workflow (/dev)

## Step 0: Session Initialization [Role: Dev Coordinator]
- **Environment Check**: Ensure the Streamlit application is running (localhost:8501). If not, start it using `./start.ps1` or `start.bat`.
- **Deterministic Check**: Run all Linters under `.agents/scripts/` (backlog, asset, doc_link). Propose fixes if deficiencies are found before proceeding.
- Read `docs/session.md` and `docs/backlog.md`.
- **Resumption Logic**: If `docs/session.md` is `active`, confirm with the user whether to resume or start a new session.
- **Protocol**: Transition state to `active` and record the target REQ in `session.md`.

## Step 1: Item Selection & Setup [Role: Dev Coordinator]
- Present `ready` or `fix-needed` items for the user to select a REQ.
- **Git Setup**: Run `git checkout -b <feat/fix>/REQ-XXX`.
- **Path Selection**: Choose Step 3 (Architect) for new features/large fixes, or Step 4 (UX) for minor UI changes.

## Step 2: Handoff Verification [Role: Dev Coordinator]
- Verify that the AC for the REQ is clear and hand off to the next role.

## Step 3: High-Level Design [Role: Architect]
- **UX Strategy Integration**: For UI/UX-related tasks, consult with the **UX Designer** at this stage to solidify the core user experience.
- Perform impact analysis and create designs (e.g., `docs/designs/*.md`) and the `implementation_plan.md`.
- **Trade-off Disclosure**: A "Trade-offs and Constraints" section is MANDATORY in the plan.
- **UX Review**: Receive audit feedback from the UX Designer after design completion.

## Step 4: UI/UX Specification [Role: UX Designer]
- *Condition: Only if UI changes are involved.*
- Create specific visual specifications (`docs/ui_spec.md`).
- As an expert, actively propose improvements or dissent against user requests if they compromise UX.

## Step 5: Approval Gate [Role: Dev Coordinator]
- Present the design and implementation plan to the user in Japanese.
- **MANDATORY TURN-END**: You MUST set `RequestFeedback: true` in the `implementation_plan.md` artifact metadata OR output a direct question using the `ask_question` tool.
- DO NOT proceed to Step 6 until explicit user approval is received.

## Step 6: Implementation [Role: Engineer]
- Perform code implementation, unit testing, and browser verification.
- **Evidence Management**: Save evidence images to `.gemini/` outside the repository and link them in the Walkthrough.
- **AC Checklist**: Include an AC verification table in the completion report as per the template.

## Step 7: Verification & Review [Role: Tester/Reviewer]
- **Red Teaming**: Audit the implementation from a "How to break it" perspective and present the AC verification table.
- **Verdict**: Issue PASS / FAIL / CONCERNS. If deficiencies are found, return to Step 6.
- **MANDATORY TURN-END**: End your turn immediately after issuing the verdict.

## Step 8: Finalization & SSoT [Role: Dev Coordinator]
- **Linter Final Check**: Run all Linter scripts again to ensure consistency before completion.
- **Backlog Sync**: Change status to `done` and add the completion date (YYYY-MM-DD).
- **SSoT Sync**: Ensure final alignment between design documents and implementation.
- **Session Exit**: Reset `session.md` to `inactive` and close the session.
- Present the Walkthrough in Japanese and provide instructions for merging the branch.

---

## Escalation Path (IMPASSE Branch)
- If an `[IMPASSE]` occurs in Step 3 or 6, the Coordinator changes the session state to `escalated` and discusses countermeasures (requirement relaxation, archiving, etc.) with the user.
