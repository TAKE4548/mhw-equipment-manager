---
trigger: always_on
---

# Project conventions

## General Guardrails (Interrupt Prevention)
- **NO ACCESS TO UNRELATED FILES:** Do not read or analyze files (e.g., source code or design docs of other features) that are not directly related to the current phase or task.
- **NO OUT-OF-BACKLOG EXECUTION:** Do not start any implementation or write code that is not explicitly registered in `docs/backlog.md` and approved by the user. If a technical solution is conceived during conversation, first guide the user to add it to the backlog.

## Planning Mode Override (CRITICAL)
- **NEVER CREATE AN IMPLEMENTATION PLAN DURING INTAKE:** If the user makes an ad-hoc request or complaint outside of the `/dev` workflow, **this does NOT warrant a plan**. Do NOT create an `implementation_plan.md` artifact. Instead, you MUST act as the Business Analyst, log it in the backlog, and instruct the user to type `/dev` to begin the planning phase.

## Semantic Trigger Precedence
- If a user's comment contains mix of "Usability requests" (e.g. "使いにくい") and "Error reports" (e.g. "エラーが出る"), **prioritize `hotfix-triage`** to address the defect (hearing and classifying) first.

## Role Switching & Handoff Protocol
- Before switching roles, immediately save the outputs of the current role to the `docs/` directory.
- When switching a role, explicitly declare it (e.g., `[Role: Architect]`).
- On handoff, the Dev Coordinator must update the `Current step` field in the backlog to prepare for potential interruption and resume.

## Expected Shared State
- `docs/backlog.md` is the single source of truth connecting all workflows.
