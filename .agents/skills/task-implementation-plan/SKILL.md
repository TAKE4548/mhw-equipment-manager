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

## MANDATORY GATE: Open Questions
If the implementation plan contains any **Open Questions** (質問項目) that require user clarification or decision:
- **ONE-ACTION POLICY**: Presenting the plan with these questions MUST be the only action in your turn. 
- **STOP IMMEDIATELY**: Do NOT proceed to execute any implementation tools (e.g., `task-tdd-implementation`) in the same turn.
- You MUST wait for the user's explicit response to the questions before proceeding.
