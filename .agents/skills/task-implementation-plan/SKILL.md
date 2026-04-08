---
name: task-implementation-plan
description: >
  Create a low-level implementation design from the architect's and UX designer's
  specifications. Use when engineer role starts working on an approved design.
---

# Implementation Plan Task

## Input
- `docs/designs/{feature-name}.md` (Architect's technical design)
- `docs/ui_spec.md` (UX Designer's interaction and layout design, if applicable)

## Output
---
name: task-implementation-plan
description: >
  Create a low-level implementation design from the architect's and UX designer's
  specifications. Use when engineer role starts working on an approved design.
---

# Implementation Plan Task

## Input
- `docs/designs/{feature-name}.md` (Architect's technical design)
- `docs/ui_spec.md` (UX Designer's interaction and layout design, if applicable)

## Output
- Implementation Sequence (ordered by dependency).
- Granular step-by-step logic updates (which files and functions to change).
- Test Design Strategies:
  - Unit Tests: Logic paths.
  - Manual Tests: UI interactions, step-by-step verifications.

## Steps
1. Break down the high-level designs into concrete coding tasks.
2. Order the tasks based on module dependencies (e.g., models -> logic -> UI layer).
3. Determine the testing strategy for each subtask (unit test vs manual/browser test).
4. Outline the exact test cases and manual test scenarios to be written.

## MANDATORY GATE: Approval & Questions
- すべてのゲート管理（質問がある場合のターン停止、ユーザー承認の待機等）については、**`project-conventions/SKILL.md` の「Universal Integrity Gates」** を厳守してください。
- 計画内に質問（Open Questions）が含まれる場合は、無条件でターンを終了し、回答を待つ必要があります。
