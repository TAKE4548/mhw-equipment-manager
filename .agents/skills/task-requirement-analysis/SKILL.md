---
name: task-requirement-analysis
description: >
  Activate when user expresses dissatisfaction, frustration,
  or wishes about the product. Wait for triggers like:
  "使いにくい", "面倒", "欲しい", "だるい", "自動でやってほしい",
  "不便", "微妙", "イラっとする", "これ毎回やるの面倒だわ",
  "もっとスリムに", "1クリックで済ませたい", "余白多すぎ",
  "xxxみたいにしたい", "パッと見でわかるようにして".
---

# Requirement Analysis Task

## Use this skill when
- The user expresses vague complaints or functional requests.
- Emotional expressions ("frustrating", "annoying", "want") are present.
- It includes improvement ideas or UI/UX related dissatisfaction.

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
