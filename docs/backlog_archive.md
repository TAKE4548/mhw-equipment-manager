# Project Backlog Archive (MHW Equipment Manager)

このファイルは、完了済み（done）となった古いバックログ項目を記録するためのアーカイブです。
最新のステータスや実行中のタスクについては `docs/backlog.md` を参照してください。

---

### REQ-001: 強化厳選 UI の改善 (武器選択ボタンのデザイン刷新)
- **Status**: done (2026-04-07)
- **Type**: enhancement
- **Priority**: high
- **Description**: 復元ボーナスの強化厳選画面において、武器を選択するボタンのデザインが「ダサい」との指摘。現状の標準的な Streamlit ボタンから、よりプレミアムで直感的なデザインに変更する。
- **Acceptance Criteria**:
    - 武器選択 UI が視覚的に強化されている（カード全体がクリック可能、またはスタイリッシュな選択ボタン）。
    - 選択状態が明確に区別できる（ボーダーの発光、影の変化など）。
    - ホバーエフェクトなどのマイクロインタラクションが追加されている。

### REQ-002: 武器選択 UI のさらなる洗練 (CARD_ACTION_RATIO 方式への統合)
- **Status**: done (2026-04-07)
- **Type**: enhancement
- **Priority**: high
- **Description**: 武器選択 UI を、v14 HUD デザインシステムに統合。
- **Decision (59b52e94)**: 完全なクリッカブルカードよりも、垂直同期と安定性を優先し、`CARD_ACTION_RATIO` (11.5:1) を用いた「同期型アクションボタン」を最終解として採用。
- **Acceptance Criteria**:
    - 武器カードとアクションボタン（❯/✔）が全ページで垂直に整列している。
    - 選択されたカードにゴールド発光ボーダーが適用されている。

### REQ-003: カード一覧の操作ボタン（⋮）とカードの水平位置揃え
- **Status**: done (2026-04-07)
- **Type**: enhancement
- **Priority**: P3
- **Description**: 一覧ページにおけるカードと右端の操作ボタンの垂直中央同期。
- **Decision (59b52e94)**: `CARD_ACTION_RATIO` による比率固定と、`vertical_alignment="center"` により、Streamlit の内部構造に左右されない視覚的な一致を達成。
- **Acceptance Criteria**:
    - 任意のリスト行で、カードと `⋮` ボタンの垂直中心線が視覚的に一致している。

### REQ-004: Undo/Redo 履歴管理の一貫性修正 (History Architecture Consistency)
- **Status**: done (2026-04-08)
- **Type**: bug
- **Priority**: high
- **Problem**: `0_skill_lottery.py` や `src/components/tables.py` で、共通の `push_action` ロジックを介さず Session State を直接操作しており、正常に Undo が動作しない、もしくはエラーになる可能性がある。
- **Acceptance Criteria**:
    - すべての履歴操作ポイントで `src.logic.history.push_action()` を使用する。
    - 各ページで Undo/Redo を実行し、データが正しく復元されることを確認する。

### REQ-007: UI のスリム化と視覚的密度の最適化 (Lean UI Design)
- **Status**: done (2026-04-09)
- **Type**: enhancement
- **Priority**: high
- **Source**: "ページレイアウト的にややスリム差に欠ける気がしている。Undo/Redoのボタンデザインとかセパレータが多すぎる感じとか"
- **Acceptance criteria**:
    - Undo/Redo がタイトル横のコンパクトなツールバーに集約されている。
    - 不要な `st.divider()` が排除され、薄いボーダーや適切な余白による区切りに変更されている。
    - ウィジェット間の余白が CSS により最適化（圧縮）されている。

### REQ-009: ページ構成とナビゲーションの再設計 (UX Consultation)
- **Status**: done (2026-04-09)
- **Type**: enhancement
- **Priority**: high
- **Source**: "Homeをダッシュボードにしているが、ダッシュボードの使い道がそこまで重要ではないので、ページナビゲーションなどどのようなページ構成が使いやすいかUXデザイナーと相談して設定したい。"
- **Requirement**: ユーザーの主要なタスク（武器登録→抽選確認→厳選）に基づいた最適なページ構成とナビゲーションを再設計する。
- **Acceptance Criteria**:
    - 主要なワークフローに最適化されたページ階層（グルーピング）が定義されている。
    - Home 画面が「分析結果」ではなく、主要なアクションへの「ポータル（クイックアクセス）」として機能している。
    - ナビゲーションの順序やアイコンが直感的である。
