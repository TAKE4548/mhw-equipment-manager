---
name: task-hotfix-triage
description: >
  Activate when user reports critical failures or unexpected behavior.
  Wait for triggers like:
  "動かない", "エラー出た", "さっきの直ってないよ", "バグってる",
  "反映されない", "真っ白になった", "落ちる", "壊れた", "おかしい",
  "意図した動きじゃない", "前は動いてたのに".
---

# Hotfix Triage Task

## Use this skill when
- The user reports an error, a crash, or things not working as expected.
- It is NOT a new feature request, but a report about something that SHOULD work but does not.

## Steps

### Phase 1: Hearing
1. Ask clarifying questions if the symptom is vague: "On which screen?", "What action triggered it?", "What is the exact error?".

### Phase 2: Classification (Time Axis Assessment)
2. Review the `docs/backlog.md` for recently "done" items.
3. Determine if the symptom is caused by:
   - A newly introduced regression (tied to a recent feature).
   - An existing latent bug (was always there but unnoticed).

### Phase 3: Routing
4. Based on the classification:
   - **Recent Regression**: Change the backlog item status from `done` to `fix-needed`. Add Triage Notes explaining the cause (Design flaw, Implementation bug, Test omission). Tell user you will fix it in `/dev`.
   - **Latent Bug**: Create a NEW backlog item with `Type: defect` and `Status: ready`. Tell user it's a pre-existing issue and is logged.
   - **Working as Designed**: Explain the specification. Ask if they want to treat it as an enhancement request instead.
   - **Cannot Determine**: Add a NEW item with `Status: needs-investigation`. Request reproduction steps in `/dev`.
