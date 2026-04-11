---
name: dev
description: >
  Formal development session workflow. Tracks progress via session.md. (v1.5)
---

# Development Workflow (/dev)

## Step 0: Session Initialization [Role: Dev Coordinator]
- **Deterministic Check**: Run `.agents/scripts/` 以下の全ての Linter (backlog, asset, doc_link) を実行します。不備がある場合は、継続する前に修正を提案してください。
- Read `docs/session.md` and `docs/backlog.md`.
- **Resumption Logic**: `docs/session.md` が `active` の場合、再開するか新規に開始するかをユーザーに確認してください。
- **Protocol**: `active` への移行と対象 REQ を `session.md` に記録します。

## Step 1: Item Selection & Setup [Role: Dev Coordinator]
- `ready` または `fix-needed` アイテムを提示し、ユーザーが REQ を選択します。
- **Git Setup**: `git checkout -b <feat/fix>/REQ-XXX` を実行します。
- **Path Selection**: 新機能/大規模修正なら Step 3（Architect）、軽微なUIなら Step 4（UX）等を選択します。

## Step 2: Handoff Verification [Role: Dev Coordinator]
- REQ の AC が明確であることを確認し、次ロールへハンドオフします。

## Step 3: High-Level Design [Role: Architect]
- **UX Strategy Integration**: UI/UX 関連の場合、この段階で **UX Designer** と協議し、ユーザー体験の骨子を固めます。
- インパクト分析を行い、設計（`docs/designs/*.md` 等）と `implementation_plan.md` を作成します。
- **Trade-off Disclosure**: プラン内に「弊害・制約」セクションを設けることが必須です。
- **UX Review**: 設計完了後、UX Designer による監査フィードバックを受けます。

## Step 4: UI/UX Specification [Role: UX Designer]
- *Condition: UI変更がある場合のみ。*
- 具体的なビジュアル仕様（`docs/ui_spec.md`）を作成します。
- 専門家として、ユーザーの要望に対する改善案や異論を積極的に提示してください。

## Step 5: Approval Gate [Role: Dev Coordinator]
- 設計案とプランをユーザーに提示します。
- **MANDATORY TURN-END**: ユーザーの明示的な承認を待つため、ターンを終了してください。

## Step 6: Implementation [Role: Engineer]
- コード実装、ユニットテスト、およびブラウザ検証を実施します。
- **Evidence Management**: 証跡画像をリポジトリ外の `.gemini/` 配下に保存し、Walkthrough でリンクします。
- **AC Checklist**: 完了報告にはテーブル形式の AC 判定を含めてください。

## Step 7: Verification & Review [Role: Tester/Reviewer]
- **Red Teaming**: 「どうすれば壊れるか」の視点で実装を監査し、AC検証テーブルを提示します。
- **Verdict**: PASS / FAIL / CONCERNS を発行し、不備があれば Step 6 へ差し戻します。
- **MANDATORY TURN-END**: 判定後は直ちにターンを終了してください。

## Step 8: Finalization & SSoT [Role: Dev Coordinator]
- **Linter Final Check**: 完了前に再度全ての Linter スクリプトを実行し、整合性を確認します。
- **Backlog Sync**: Status を `done` にし、完了日 `(YYYY-MM-DD)` を追記します。
- **SSoT Sync**: 設計ドキュメントと実装の最終的な整合性をとります。
- **Session Exit**: `session.md` を `inactive` にリセットし、セッションを閉じます。
- Walkthrough 提示とブランチのマージ案内を行い、セッションを完了します。

---

## Escalation Path (IMPASSE Branch)
- Step 3 または 6 で `[IMPASSE]` が発生した場合、Coordinator はセッションを `escalated` に変更し、ユーザーと対策（要件緩和、アーカイブ等）を協議してください。
