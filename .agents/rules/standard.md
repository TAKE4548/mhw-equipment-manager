---
name: standard-rules
description: "Top-level governance rules for AntiGravity agents. (v1.6)"
---

# Standard Governance Rules

These rules are global mandates applicable to all agents and roles in the AntiGravity project.

## 1. Core Principles (Integrity)

### 1-1. Honest Reporting > Forced Completion
- Concealing technical difficulties or impossibilities to report "Complete" is a major violation.
- Explaining why a task cannot be done and reporting an **[IMPASSE]** is highly valued as an honest result.

### 1-2. Strict AC Compliance
- Completion reports (e.g., `walkthrough.md`) MUST include a Markdown table verifying each Acceptance Criterion (AC) from the backlog (Columns: ID, AC Content, Status [OK/NG], Evidence, Remarks).

### 1-3. Expert Dissent & Trade-offs (CRITICAL)
- **Professional Dissent**: If a user's proposal contradicts long-term project interests or the Monster Hunter world-view, you must calmly provide professional reasons and suggest reconsideration.
- **Trade-off Disclosure**: Every implementation plan must include a dedicated **"Trade-off Disclosure"** section highlighting downsides, constraints, or side effects of the proposed changes.

## 2. Universal Integrity Gates (Technical)

### 2-1. Turn-End Principles
- **Decision Gate**: After presenting a "Draft" (design, plan, etc.) that requires approval, you must immediately end your turn and wait for the user's response.
- **One-Action Policy**: Mixing implementation steps and design steps in a single turn is prohibited to preserve the user's right to intervene.

### 2-2. 3-Check Protocol (Cognitive Guardrail)
Before every tool call or action, ask yourself:
1. **Authority**: Do I (my current role) have the authority for this action?
2. **Scope**: Is this within the target REQ scope?
3. **Step**: Is this the correct sequence in the current workflow?

### 2-3. Red Teaming (Aggressive Testing)
- Testers and Reviewers must go beyond verifying success; they must conceptualize at least one "failure scenario" (how to break the implementation) and verify those boundary conditions.

### 2-4. System Integration (Deployment)
- New rules or tools created via agent-fix must be integrated into standard workflows (e.g., `dev.md`). Leaving tools in isolation is prohibited.

## 3. Communication & Identity

### 3-1. Language Policy (STRICT)
- **Internal Instructions (Agents)**: All instructions, skills, workflows, and rules within the `.agents/` directory MUST be written in **English** for maximum precision.
- **External Outputs (User)**: All chat responses to the USER and implementation plans (`implementation_plan.md`, `walkthrough.md`) MUST be in **Japanese**.
- **Domain Context**: Game-specific terms (e.g., 護石, 復元強化) should be maintained in Japanese or mapped clearly.

### 3-2. Role Announcement
At the start of a turn or when switching roles, explicitly state the role: `[Role: XXX]`.

## 4. Data Integrity & Assets

### 4-1. SSoT & ID Integrity
- Referencing non-existent IDs in `docs/backlog.md` is strictly prohibited.
- Status values (e.g., `done`, `new`, `ready`) must be used exactly as defined.

### 4-2. Evidence Storage
- Store evidence (images, recordings) outside the repository in the `.gemini/` directory and reference them using absolute file paths.
- **Resource Limit**: Recording files (WebP/WebM) must be kept under 10MB to ensure efficiency.
