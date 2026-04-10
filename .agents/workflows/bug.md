---
name: bug
description: >
  Triage for reported bugs or unexpected behavior. 
  Determines if it is a regression or a latent bug.
---

# Bug Triage Workflow (/bug)

Used when the user reports "Error X", "It's broken", or "Not working as before".

## Step 1: Fact Finding [Role: Hotfix Triager]
- Use `task-hotfix-triage` to collect symptoms and context (Which screen? What action?).
- Read logs or recent `done` REQs to identify the cause.

## Step 2: Time-Axis Classification
- **Regression**: Caused by a recent `done` REQ. Change that REQ back to `fix-needed`.
- **Latent Bug**: Existed before recent changes. Create a new `REQ` with `Type: defect`.
- **By Design**: Explain the spec. If the user wants to change it, switch to `/wish`.

## Step 3: Routing
- Update `docs/backlog.md` with Triage Notes.
- Guide the user to start `/dev` for the fix.
