---
name: task-requirement-analysis
description: >
  Activate when user expresses dissatisfaction, frustration,
  or wishes about the product. Requesting this DOES NOT warrant a plan.
  Wait for triggers like: "使いにくい", "面倒", "欲しい", "だるい", "自動でやってほしい",
  "不便", "微妙", "イラっとする", "これ毎回やるの面倒だわ",
  "もっとスリムに", "1クリックで済ませたい", "余白多すぎ",
  "xxxみたいにしたい", "パッと見でわかるようにして".
---

# Requirement Analysis Task (INTAKE ONLY)

## CRITICAL: NO SOURCE CODE ACCESS
- **DO NOT READ OR VIEW ANY SOURCE CODE (.py, .js, etc.)** during this task. 
- You are strictly limited to reading and writing `docs/backlog.md`. 
- By not reading the source code, you prevent yourself from accidentally starting a technical plan.

## Planning Mode Guidance (MANDATORY INTERPRETATION)
- **YES, IT WARRANTS A PLAN:** If the system asks if this request warrants a plan, the answer is **YES**.
- **BUT THE PLAN IS ONLY FOR BACKLOG REGISTRATION:** The "plan" you create MUST be exclusively about:
  1. Extracting the problem and requirement.
  2. Formatting the requirement into a backlog item.
  3. Appending it to `docs/backlog.md`.
- **FORBIDDEN:** Creating a plan to modify source code (.py, .js), styling, or any business logic. Any such technical plan is a SEVERE violation of this skill.
- **SUCCESS DEFINITION:** The task is finished and "Successfully verified" once the backlog is updated.

## Use this skill when
- The user expresses vague complaints or functional requests (e.g., "使いにくい", "だるい", "スリムにしたい").
- Emotional expressions are present.

## Do not use this skill when
- Specific defect/bug reports (use `hotfix-triage` instead).
- During active implementation or design phases in `/dev`.

## Steps
1. Record the user's original statement exactly as said.
2. Extract the "Problem" (what is causing the frustration).
3. Derive the "Requirement" (what condition must be met to solve the problem).
4. Define tentative "Acceptance criteria" (testable conditions).
5. Append a new item to `docs/backlog.md` with `Type: enhancement`. Check for duplicates.
6. Present the structured result to the user.

## Output Template to User
"I have added this to the backlog (REQ-{n}).
There are currently {count} pending items.
Whenever you are ready to develop, please start with `/dev`."
