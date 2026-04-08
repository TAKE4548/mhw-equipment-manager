---
trigger: always_on
description: "Project conventions. ALL IMPLEMENTATION PLANS MUST BE IN JAPANESE."
---

# Project conventions

## 1. Universal Integrity Gates (CRITICAL)
これらのルールは、他のいかなるスキルやワークフローの指示よりも優先される最上位の行動規範です。

### 1-1. Draft Status & Approval Gate
以下の条件に当てはまる成果物（設計書、UX仕様書、実装プラン）は「ドラフト（未承認）」とみなされます。
- 内容に "質問", "Open Question", "未定", "TBD" 等が含まれている。
- ユーザーからの明示的な「OK」「承認」「進めて」等の合意が履歴にない。

### 1-2. Mandatory Turn-End (One-Action Policy)
- ドラフト状態の成果物を提示した際、または承認が必要なフェーズ（Step 5/Step 6のプラン提示等）では、**必ずそのターンの最後で処理を終了**しなければなりません。
- 同一ターン内で、承認を前提としたツール（`run_command`, `task-tdd-implementation`等）を呼び出してはなりません。

## 2. General Guardrails
- **NO ACCESS TO UNRELATED FILES:** 現在の作業に直接関係のないコードや設計図（他機能のもの）を好奇心で読み込まない。
- **NO OUT-OF-BACKLOG EXECUTION:** `backlog.md` に未登録、または未着手のタスクを勝手に実装しない。
- **BA-FIRST INTAKE:** ユーザーの要望（「直して」「おかしい」等）に対して、いきなりコードを書き始めない。まず Business Analyst として状況を整理し、バックログを更新する。

## 3. /dev Workflow Governance
- **Milestone Enforcement:** `task.md` には `dev.md` の公式ステップ名（例：`Step 3: Architect Design`）をそのまま使用する。
- **Role Announcement:** ロールを切り替えた直後、またはステップの開始時に `[Role: XXX]` を明示する。
- **SSoT Integrity:** 実装が完了したら、必ず `docs/*.md`（仕様書）を最新の実装状態と同期させた上で、バックログを `done` にする。

## 4. Language of Artifacts
- **IMPLEMENTATION PLANS MUST BE IN JAPANESE:** ユーザー承認を仰ぐための `implementation_plan.md` は必ず**日本語**で作成すること。
- **Internal Docs:** `docs/designs/*.md` や `docs/ui_spec.md` は、技術的正確性を期すため、指示がない限り英語で記述して良い。

## 5. Context Optimization (Defrag Rule)
- 複数のファイルに似た指示がある場合、常にこの `project-conventions` の定義を正とする。
- アーキテクトは、冗長な指示を積極的に削除・統合し、指示の「密度と実行力」を維持しなければならない。
