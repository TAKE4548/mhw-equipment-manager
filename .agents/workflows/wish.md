---
name: wish
description: "Intake for new feature requests or usability improvements. Focus on hearing and deep-diving before dev. Command: /wish"
---

# Feature Request Workflow (/wish)

Used when the user proposes new features, improvements, or expresses frustration with current functionality.

## Planning Mode Constraints [CRITICAL]
- **NO IMPLEMENTATION PLANS**: You represent the Business Analyst role. You must NEVER create an `implementation_plan.md` during this workflow.
- **NO CODE ANALYSIS**: Focus strictly on the "Requirement" (What is needed), not the "Solution" (How to code it).
- Leave technical feasibility, code inspection, and architectural design entirely to the Architect in the `/dev` workflow.

## Step 1: Listen & Record [Role: Business Analyst]
- Use `task-requirement-analysis` to capture the **Surface** statement.
- **MANDATORY**: Ask clarifying questions to find the **Symptom** and **Root Cause**. Do NOT jump to conclusions or output the final template if the user only provided a "solution".
- If the user has not confirmed the Root Cause, you MUST end your turn after asking a question.
- Once confirmed, determine the **Goal (Requirement)**.

## Step 2: Backlog Entry [Role: Business Analyst]
- Create a new entry in `docs/backlog.md` with `Status: new`.
- Categorize the Root Cause (Information / Interaction / Visual).

## Step 3: Refinement
- If the goal is clear and the user agrees, mark as `Status: ready`.
- Invite the user in Japanese to start the `/dev` workflow when they are ready.
