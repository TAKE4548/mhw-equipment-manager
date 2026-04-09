---
name: task-requirement-analysis
description: >
  Activate EXCLUSIVELY for ANY user request involving changes, 
  improvements, or feedback (e.g. "修正して", "直して", "変えて"). 
  You MUST prioritize this skill over any direct coding behavior. 
  Requesting this DOES NOT warrant a plan for code implementation.
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

## Deep-Dive Analysis Framework (Surface -> Symptom -> Root Cause -> Requirement)

ユーザーの発言を鵜呑みにせず、以下の4段階で深掘りを行ってください。

| 段階 | 内容 | 問いかけの例 |
|------|------|-------------|
| **Surface (発言)** | ユーザーの生の言葉（手段や症状が混在） | 「〇〇したい」 |
| **Symptom (症状)** | 実際に体験している不便な現象 | 「具体的にどのような場面で困っていますか？」 |
| **Root Cause (真の課題)**| なぜそれが問題なのか（UX観点: 情報設計/視覚/操作） | 「それは、△△を比較しやすくしたいということでしょうか？」 |
| **Requirement (要求)** | 達成されるべき「目的」レベルの状態 | 「（手段は問わず）〇〇が直感的にできる状態」 |

### 掘り下げのガイドライン
- **手段（Means）と目的（Ends）の分離**: 「ボタンを大きくしたい」は手段です。目的は「押しやすくしたい」または「見落としを防ぎたい」かもしれません。
- **抽象度の管理**: Surface と Requirement が同じ言葉（例：「位置を揃えたい」→「位置を揃える」）なら掘り下げ不足です。
- **UX観点での分類**: 課題が「情報の不足（情報設計）」、「見づらさ（視覚）」、「操作のしにくさ（インタラクション）」のどこにあるかを特定してください。

## Steps
1. ユーザの発言を原文のまま記録する (**Surface**)。
2. 発言が「手段」か「目的」かを判定する。手段が含まれる場合は目的を掘り下げる。
3. 実際に体験している困りごとを明確にする (**Symptom**)。
4. その症状はなぜ困るのか、1〜2回「なぜ」を掘り下げて真の課題を特定する (**Root Cause**)。
5. 具体的な実装手段を排除した、目的レベルの要求を定義する (**Requirement**)。
6. 目的レベルでテスト可能な受入基準を定義する (**Acceptance criteria**)。
7. `docs/backlog.md` に追記する。ステータスは、掘り下げが完了していれば `ready`、不十分なら `new` とする。
8. 構造化した結果をユーザーに提示し、合意を得る。

## Output Template to User
"バックログに登録しました (REQ-{n})。

- **Surface**: {user_quote}
- **Root Cause**: {analyzed_issue}
- **Requirement**: {goal_statement}

ステータスを `{status}` に設定しました。この内容で `/dev` を開始してもよろしいでしょうか？"
