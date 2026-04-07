# Project Backlog (MHW Equipment Manager)

This document is the Single Source of Truth for all feature requests, bug reports, and ongoing development tasks.

## Status Definitions
- **new**: Just added, prioritized but not elaborated.
- **ready**: Requirements are structured and ready for development.
- **in-progress**: Currently being worked on in a `/dev` session.
- **fix-needed**: A recent regression was found, needs immediate attention.
- **needs-investigation**: Cannot be replicated or understood without further research.
- **done**: Successfully reviewed and merged.

---
## Backlog Items

### REQ-001: 強化厳選 UI の改善 (武器選択ボタンのデザイン刷新)
- **Status**: done (2026-04-07)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: high
- **Description**: 復元ボーナスの強化厳選画面において、武器を選択するボタンのデザインが「ダサい」との指摘。現状の標準的な Streamlit ボタンから、よりプレミアムで直感的なデザインに変更する。
- **Problem**: 武器選択ボタンが単調で、アプリケーション全体のモダンなデザインから浮いてしまっている。
- **Acceptance Criteria**:
    - 武器選択 UI が視覚的に強化されている（カード全体がクリック可能、またはスタイリッシュな選択ボタン）。
    - 選択状態が明確に区別できる（ボーダーの発光、影の変化など）。
    - ホバーエフェクトなどのマイクロインタラクションが追加されている。

### REQ-002: 武器選択 UI のさらなる洗練 (CARD_ACTION_RATIO 方式への統合)
- **Status**: done (2026-04-07)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: high
- **Description**: 武器選択 UI を、v14 HUD デザインシステムに統合。
- **Problem**: 選択ボタンが独立した要素として配置されており、カードデザインとの一体感が欠如していた。
- **Decision (59b52e94)**: 完全なクリッカブルカードよりも、垂直同期と安定性を優先し、`CARD_ACTION_RATIO` (11.5:1) を用いた「同期型アクションボタン」を最終解として採用。
- **Acceptance Criteria**:
    - 武器カードとアクションボタン（❯/✔）が全ページで垂直に整列している。
    - 選択されたカードにゴールド発光ボーダーが適用されている。

### REQ-003: カード一覧の操作ボタン（⋮）とカードの水平位置揃え
- **Status**: done (2026-04-07)
- **Current Step**: none
- **Type**: enhancement
- **Priority**: P3
- **Description**: 一覧ページにおけるカードと右端の操作ボタンの垂直中央同期。
- **Decision (59b52e94)**: `CARD_ACTION_RATIO` による比率固定と、`vertical_alignment="center"` により、Streamlit の内部構造に左右されない視覚的な一致を達成。
- **Acceptance Criteria**:
    - 任意のリスト行で、カードと `⋮` ボタンの垂直中心線が視覚的に一致している。

### REQ-004: Undo/Redo 履歴管理の一貫性修正 (History Architecture Consistency)
- **Status**: new
- **Type**: bug
- **Priority**: high
- **Problem**: `0_skill_lottery.py` や `src/components/tables.py` で、共通の `push_action` ロジックを介さず Session State を直接操作しており、正常に Undo が動作しない、もしくはエラーになる可能性がある。
- **Acceptance Criteria**:
    - すべての履歴操作ポイントで `src.logic.history.push_action()` を使用する。
    - 各ページで Undo/Redo を実行し、データが正しく復元されることを確認する。

### REQ-005: 表示用語の統一 (レベル表記のローマ数字適用)
- **Status**: new
- **Type**: enhancement
- **Priority**: mid
- **Problem**: `ui_spec.md` の規定（レベルはローマ数字 Ⅰ, Ⅱ, Ⅲ）に反し、登録フォームの選択肢等で算用数字 [1], [2], [3] が表示されたままになっている。
- **Acceptance Criteria**:
    - 復元ボーナスの選択肢ピッカーにおいて、常にローマ数字が表示されている。
    - 正規化関数 `normalize_bonus` が入力レイヤー（UI）で一貫して適用されている。

### REQ-006: フラグメント隔離の再評価 (Fragment Isolation Refinement)
- **Status**: new
- **Type**: maintenance
- **Priority**: low
- **Problem**: `0_skill_lottery.py` 等で、本来フラグメント内で完結すべき更新処理がページ全体の `st.rerun()` を誘発しており、パフォーマンス上のメリットが薄れている。
- **Acceptance Criteria**:
    - リスト更新等の操作が、可能な限りページ全体ではなくフラグメント単位の再描画で完結している。
