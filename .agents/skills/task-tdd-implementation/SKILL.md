---
name: task-tdd-implementation
description: >
  Implement features using test-driven development.
  Write tests first, then implement code to pass them.
  Use when engineer has a completed implementation plan
  and test design.
---

# TDD Implementation Task

## Steps
1. Proceed according to the task sequence in the implementation plan.
2. For each logic or backend task:
   a. First write the Unit Test based on the Acceptance Criteria (Red).
   b. Write the minimal code to pass the test (Green).
   c. Refactor.
3. Ensure all Unit Tests pass.
4. > [!WARNING]
   > Do NOT attempt to run unit tests for front-end visual interactions or manual UI procedures here. 
   > For UI and visual components, hand off directly to the `browser-debug` skill.

## Rules
- Never write implementation code before writing the test condition.
- Verify that the test fails (Red) before beginning the implementation logic.
