---
name: task-browser-debug
description: >
  Execute manual tests using the browser sub-agent.
  Debug UI issues by iterating through test cases
  and fixing failures. Use when manual test cases are
  designed and need to be executed in a real browser.
---

# Browser Debug Task

## Steps
1. Review the list of Manual Test Cases (`MT-xxx`).
2. Boot the application and hand over the objective to the `browser_subagent`.
3. Sequentially execute the test cases:
   a. Follow the steps of the manual test.
   b. Compare the Expected Result with the Actual Result.
   c. If it fails: Identify the cause in the codebase, make minimal modifications, and re-execute.
4. Repeat until all test cases pass without errors.
5. Output a summary of the test results.

## Rules
- Keep modifications minimal and related strictly to the failed UI interaction.
- Ensure that unit tests are also rerun after UI fixes to catch any regressions.
- **Approach-Based Impasse Detection (CRITICAL):**
  Track the TECHNICAL APPROACH being used (e.g., "CSS absolute positioning overlay").
  If the SAME APPROACH fails 2 times, regardless of how many tweaks were applied:
  → Immediately declare `[IMPASSE]` and hand off to Dev Coordinator.
  → Do NOT try a 3rd CSS/JS variation of the same strategy.
  → A fundamentally different approach must be proposed by the Architect first.
