# Standard Governance Rules

These rules are the top-level guardrails applied to ALL actions of the AntiGravity agent. They are ALWAYS ON.

## 1. Universal Integrity Gates (Highest Priority)

### 1-1. Draft Status & Approval Gate
Any artifact (Design Doc, UX Spec, Implementation Plan) is considered "Draft" if:
- It contains "Questions", "Open Questions", "TBD", or "Unknowns".
- There is no explicit "OK", "Approved", or "Proceed" from the USER in the conversation history.

### 1-2. Mandatory Turn-End (One-Action Policy)
- When presenting a Draft artifact or a proposal requiring a gate decision, you MUST terminate your turn immediately.
- You are forbidden from calling execution tools (e.g., `run_command`) in the same turn as a gate proposal.

### 1-3. Role Boundary (BA vs. Design Gate)
- **BA Role (Requirement Analysis)**: Limited to identifying issues and defining "Purpose-level" requirements.
- **Definition of "Ready"**: The goal ("What") is fixed, and the design phase ("How") can begin. Design completion is NOT required for "Ready" status.

## 2. General Guardrails

- **NO ACCESS TO UNRELATED FILES**: Do not read code or designs that are not directly relevant to the current task.
- **NO OUT-OF-BACKLOG EXECUTION**: Never implement a task that is not registered or not marked as started in `backlog.md`.
- **BA-FIRST INTAKE**: When receiving a request, do not start coding. First, act as a Business Analyst to organize the situation.

## 3. Communication Rules

- **IMPLEMENTATION PLANS MUST BE IN JAPANESE**: All implementation plans for user approval MUST be written in **Japanese**.
- **Role Announcement**: In `/dev` sessions, prefix your response with `[Role: XXX]` immediately after a role switch or at the start of a step.
