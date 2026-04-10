---
name: task-code-review
description: >
  Review code against design, AC, and evidence. 
  Reports technical debt as "Concerns".
---

# Code Review Task

Your goal is to verify that the implementation is functionally correct, aligns with the designs, and does not introduce critical technical debt.

## 1. Compliance
- Follow the **3-Check Protocol** in `GEMINI.md`.
- Review the **Evidence (Screenshots/Logs)** provided by the Engineer. Do not take "Completed" at face value.

## 2. Review Process

1. **AC Match**: Compare the Engineer's "AC Check" results with the original `backlog.md` and evidence.
2. **Design Fidelity**: Verify if the implementation matches `docs/designs/*.md` and `docs/ui_spec.md`.
3. **Evidence Audit**:
   - Check `MT-{num}_{pass|fail}.png` for UI correctness.
   - Check Unit Test logs for logic correctness.
4. **Impact Assessment**: Check for regressions in existing features.
5. **Technical Debt (Concerns)**: Identify non-blocking issues that may cause future problems (Architecture violations, hardcodes, etc.).

## 3. Output Format (Review Verdict)

You MUST provide your verdict in this structured format:

- **Verdict**: [PASS] | [FAIL]
- **Correction Proposals**: (If [FAIL], list specific fixes)
- **Concerns (懸念事項)**: (Architecture feedback or potential debt. This will be recorded in the backlog by the Coordinator.)

**MANDATORY**: End your turn immediately after presenting this verdict.
