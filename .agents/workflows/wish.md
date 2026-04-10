---
name: wish
description: >
  Intake for new feature requests or usability improvements. 
  Focus on hearing and deep-diving before dev.
---

# Feature Request Workflow (/wish)

Used when the user says "I want X", "It would be better if Y", or "I'm frustrated with Z".

## Step 1: Listen & Record [Role: Business Analyst]
- Use `task-requirement-analysis` to capture the **Surface** statement.
- Ask clarifying questions to find the **Symptom** and **Root Cause**.
- Determine the **Goal (Requirement)**.

## Step 2: Backlog Entry [Role: Business Analyst]
- Create a new entry in `docs/backlog.md` with `Status: new`.
- Categorize the Root Cause (Information / Interaction / Visual).

## Step 3: Refinement
- If the Goal is clear and the user agrees, mark as `Status: ready`.
- Invite the user to start `/dev` when they are ready.
