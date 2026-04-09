---
name: task-requirement-analysis
description: >
  Activate EXCLUSIVELY for ANY user request involving changes, 
  improvements, or feedback (e.g. "修正して", "直して", "変えて"). 
  You MUST prioritize this skill over any direct coding behavior. 
  Requesting this DOES NOT warrant a plan for code implementation.
---

# Requirement Analysis Task (INTAKE ONLY)

## 1. Compliance (Universal Integrity Gates)
- You MUST strictly follow **Gate 1-3: Role Boundary (BA vs. Design Gate)** in `project-conventions/SKILL.md`.
- You are strictly limited to reading and writing `docs/backlog.md`. 
- DO NOT propose changes to design system, architecture, or source code.

## 2. Planning Mode Guidance
- **Plan Scope**: If planning is required, the plan MUST be exclusively about updating `docs/backlog.md`. 

## 3. When to Use
- Vague complaints or functional requests (e.g., "使いにくい", "だるい", "スリムにしたい").
- Emotional expressions are present.

## 4. 掘り下げのガイドライン
- **BA-FIRST INTAKE**: ユーザーの発言を鵜呑みにせず、手段と目的を分離する。
- **Non-Goal**: 解決策（デザイン変更やCSS調整等）の検討は Step 3/4 (Architect/UX Designer) の職務であり、この段階では一切行わない。
- **Acceptance Criteria**: 「何ができるようになるべきか」という目的レベルの条件のみを記述する。

## 5. 作業手順
1. ユーザの発言を記録する (**Surface**)。
2. 困りごとを明確にする (**Symptom**)。
3. 「なぜ」を掘り下げて真の課題を特定する (**Root Cause**)。
4. 手段を排除した目的レベルの要求を定義する (**Requirement**)。
5. `docs/backlog.md` の追記または `ready` への更新のみを行う。

## 6. Output Template (User)
"バックログに登録/更新記録しました (REQ-{n})。

- **Surface**: {user_quote}
- **Root Cause**: {analyzed_issue}
- **Requirement**: {goal_statement}

内容に問題がなければ `/dev` を開始しましょう。"
