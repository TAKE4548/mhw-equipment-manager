---
name: wish
description: "Intake for new feature requests or usability improvements. Focus on hearing and deep-diving before dev. Command: /wish"
---

# Feature Request Workflow (/wish)

Used when the user proposes new features, improvements, or expresses frustration with current functionality.

## Step 1: Listen & Record [Role: Business Analyst]
- Use `task-requirement-analysis` to capture the **Surface** statement.
- Ask clarifying questions to find the **Symptom** and **Root Cause**.
- Determine the **Goal (Requirement)**.

## Step 2: Backlog Entry [Role: Business Analyst]
- Create a new entry in `docs/backlog.md` with `Status: new`.
- Categorize the Root Cause (Information / Interaction / Visual).

## Step 3: Refinement
- If the goal is clear and the user agrees, mark as `Status: ready`.
- Invite the user in Japanese to start the `/dev` workflow when they are ready.
