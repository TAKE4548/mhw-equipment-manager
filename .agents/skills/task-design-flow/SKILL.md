---
name: task-design-flow
description: 【必須手順】新規開発・仕様変更・不具合解決の設計フェーズ。docs/の更新とプラン作成を強制する。
---
# 🏛️ Design Workflow (Mandatory)

> [!IMPORTANT]
> すべての新規開発、仕様変更、不具合解決において、このフロー（Phase 0-3）を遵守することは義務であり、各フェーズの開始・移行時には必ずその旨を明示的に宣言せよ。
> **Phase 0/1 の完了まで、実装プランの作成やコード編集を行ってはならない。**

### Phase 0: 要求の明文化 (Stop-Gate)
- `docs/requirements.md` に要求（REQ-XXX）を追記せよ。不具合改修の場合も、現象と影響を記録せよ。
- **追記内容をユーザーに提示し、合意を得るまで Phase 1 に進んではならない。**

### Phase 1: 要求の構造化
- 解決すべき課題を整理せよ。
- **不具合対応の場合**は、いきなり推測で設計を変えるのではなく、まず既存コードやエラーログを調査し、根本原因（Root Cause）を特定した上で論点を提示し、ユーザーと合意せよ。

### Phase 1.5: UI/UX詳細設計 (委譲フェーズ)
- **UI変更が1点でもある場合、このフェーズは必須である。**
- `role-ux-designer` を召喚し、`task-ux-design` を実行させよ。
- `ui_spec.md` が更新され、UXデザイナーから「完了」の報告を受けるまで、Phase 2 に進んではならない。

### Phase 2: 設計書の改廃 (Single Source of Truth)
- UX Designerから引き継ぎを受けた場合、提案された `ui_spec.md` や `design_system.md` の更新内容を、システム全体のアーキテクチャの観点から審査・承認せよ。
- その後、競合があれば解消し、合意に基づいて `docs/` 内の関連ファイルを全て更新せよ。

### Phase 3: 実装・テスト計画書の作成 (implementation_plan.md)
- エンジニア向けに `implementation_plan.md` を作成せよ。
- **【最重要】** `docs/workflow/test_scenarios.md` を更新し、エンジニアが機械的に実装・検証できるレベルの具体的なテスト手順を定義せよ。
- `implementation_plan.md` は以下の項目を必須とする：概要、影響範囲、ステップ別手順（**エンジニアが随時更新できるチェックリスト形式のタスク一覧**）、**合格基準(Acceptance Criteria)**、完了定義。