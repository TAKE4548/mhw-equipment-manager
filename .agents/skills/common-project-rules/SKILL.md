---
name: common-project-rules
description: Git形式、言語、命名規則など、プロジェクト全般で遵守すべき規律。
---
# Project Quality Standards

- **Language ( 言語 )**: 
  - ユーザーとの対話およびドキュメント(`docs/`)は**日本語**を使用せよ。
  - プログラムコード（変数名、関数名、コメント）は**英語**を使用せよ。

- **Git Standard**: 
  - コミットプレフィックス（`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`）を必須とする。
  - コミットメッセージは簡潔かつ変更内容が明確に伝わるように記述せよ。

- **Coding Convention**: 
  - **Python**: 変数・関数名は `snake_case` を使用せよ（PEP 8準拠）。
  - **JavaScript**: 変数・関数名は `camelCase` を使用せよ。
  - **DRY原則**: コードの重複を避け、再利用可能なコンポーネント化を常に意識せよ。
  - **Clean Code**: 将来のAIや他の開発者が理解しやすい、意図の明確な命名を心がけよ。

- **Meta-Processing Protocol ( 思考プロトコル )**:
  - **Identity Header**: 応答の冒頭に必ず `### [Current Role] <Workflow>: Phase X` を記述せよ。
  - **Role Triage**: ユーザーの要求に対し、「これは Architect, Engineer, UX Designer の誰の役割か？」をまず判断せよ。
  - **Phase Gate**: 前のフェーズが完了し、SSoT（`docs/`）が更新されていることを確認してから次のフェーズへ進め。
  - **Evidence-Based**: フェーズ完了報告時には、必ず「どのファイルの、どの行を更新したか」等の具体的な証跡を添えよ。