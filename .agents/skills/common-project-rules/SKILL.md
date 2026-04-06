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
  - **Identity Header & Handoff**: 応答の冒頭に必ず `### [Current Role] <Workflow>: Phase X` を記述せよ。また、他のロールに切り替える（引き継ぐ）際は、必ず直前のロールとして「状態の要約と引き継ぎ事項」を1文で述べてから、新しいロールのヘッダーを出力せよ（例：「UI要件が固まったためUXデザイナーに引き継ぎます。\n\n### [UX Designer]...」）。
  - **Role Triage**: 「これは Architect, Engineer, UX Designer の誰の役割か？」をまず判断し、必要なら状態を要約してロール切り替えを宣言せよ。
  - **Self-Review Loop**: ツール（特にコード編集）を使用する前に、必ず「前提となるドキュメント（SSoT）の更新は完了しているか？」を自問自答せよ。
  - **Evidence-Based**: フェーズ完了報告時には、必ず「どのファイルの、どの行を更新したか」等の具体的な証拠（URLリンクや行番号）を添えよ。