---
name: task-hotfix-triage
description: >
  Triage for reported bugs or unexpected behavior. 
  Determines if it is a regression or a latent bug.
---

# Hotfix Triage Task

Your goal is to categorize a reported issue and route it to the correct fix process.

## 1. Compliance (CRITICAL)
- **DO NOT MODIFY ANY SOURCE CODE** during triage.
- **BA-FIRST**: Hearing and investigation only. The output is a backlog update.

## 2. Triage Framework: Time-Axis Classification

1. **Facts Gathering**: Ask "On which screen?", "What action?", "What error?". Use `view_file` to read logs if available.
2. **Regression Check**: Compare the symptom with the most recent `done` REQs.
   - If caused by a recent change -> **Regression**.
   - If it existed before or is unrelated to recent changes -> **Latent Bug**.
3. **Routing Decision**:
   - **Regression**: Change the original REQ status to `fix-needed`. Add Triage Notes.
   - **Latent Bug**: Create a NEW REQ with `Type: defect` and `Status: ready`.
   - **By Design**: Explain the specification. Suggest `/wish` if they want a change.
   - **Unknown**: Mark as `Status: needs-investigation`.

## 3. Backlog Entry (Triage Notes)

Update `docs/backlog.md` with:
- **Symptom**: Clear description of the observed failure.
- **Classification**: Regression / Latent / By Design.
- **Routing**: Specify the starting Step for `/dev` (e.g., Step 3 for design flaw, Step 6 for implementation bug).

## 4. Boundaries
- Do not propose technical solutions (Leave this to the Architect).
- Focus on "What is happening" and "Why it happened now".
