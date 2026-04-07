---
name: task-hotfix-triage
description: >
  Activate for ANY report of bugs, errors, or unexpected results. 
  "動かない", "エラー出た", "直ってない", "バグってる", "修正して", "おかしい" 
  などの直接的な「直し」の要求も、まずこのスキルで吸い上げること。
  エンジニアとして直接走り出す前に、必ずこのトリアージを通さなければなりません。
---

# Hotfix Triage Task

## CRITICAL: NO SOURCE CODE MODIFICATION
- **DO NOT MODIFY ANY SOURCE CODE** during this triage task.
- You are allowed to READ code and logs to identify causes, but the output must be limited to updating `docs/backlog.md`.

## Planning Mode Guidance (MANDATORY INTERPRETATION)
- **YES, IT WARRANTS A PLAN:** If the system asks if this report warrants a plan, the answer is **YES**.
- **BUT THE PLAN IS ONLY FOR TRIAGING:** The "plan" you create MUST be exclusively about:
  1. Hearing the user's symptoms and structuring facts.
  2. Searching for the root cause in logs or recent changes.
  3. Updating the status and "Triage notes" in `docs/backlog.md`.
- **FORBIDDEN:** Creating a plan to fix the bug directly. Fixing MUST be done in a separate `/dev` session.

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

## Triage Notes Scope Restriction
The "Triage Notes" field in `docs/backlog.md` MUST contain ONLY:
- Symptom description (what the user observed)
- Time-axis classification (regression / latent / by-design)
- Routing decision (which step in `/dev` to resume from)

**FORBIDDEN in Triage Notes:**
- Technical solutions (how to fix it) — that is the Architect's task in Step 3.
- CSS or code-level proposals.
Writing design decisions in Triage Notes bypasses the Architect and causes Step 3 to be skipped.
