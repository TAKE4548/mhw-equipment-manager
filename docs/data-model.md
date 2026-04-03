# Data Model: MHWs Equipment Manager

## Entities

### `SkillUpgrade` (スキル強化レコード / Sheet: `SkillUpgrade`)
錬成（スキル付与）の目標を管理します。
- `id` (STRING/UUID): ユニークID
- `weapon_type` (TEXT): 武器種
- `element` (TEXT): 属性
- `series_skill` (TEXT): シリーズスキル部品名
- `group_skill` (TEXT): グループスキル名
- `remaining_count` (INTEGER): 残り回数

### `EquipmentBox` (所持武器台帳 / Sheet: `EquipmentBox`)
所持している巨戟アーティア武器の現在のステータスを管理します。
- `id` (STRING/UUID): ユニークID
- `weapon_name` (TEXT): 武器の識別名（任意）
- `weapon_type`, `element` (TEXT)
- `current_series_skill`, `current_group_skill` (TEXT)
- `enhancement_type` (TEXT): 巨戟強化種別（攻撃激化など）
- `p_bonus_1` ~ `3` (TEXT): 生産ボーナス3枠
- `rest_1_type` ~ `rest_5_level` (TEXT): 現在付与されている復元ボーナス5枠（種類とレベル）

### `RestorationTracker` (復元厳選トラッカー / Sheet: `RestorationTracker`)
未来の復元テーブルの抽選結果と目標を管理します。
- `id` (STRING/UUID): ユニークID
- `weapon_id` (STRING): `EquipmentBox.id` への参照
- `remaining_count` (INTEGER): 到達までの残り回数
- `target_rest_1_type` ~ `target_rest_5_level` (TEXT): 目標とする5枠の構成

## Storage (ストレージ)
- **Primary**: Google Spreadsheets (per-user dynamic URL).
- **Secondary**: Local SQLite is deprecated and replaced by GSheets for cloud compatibility.

### `ActionHistory` (アクション履歴)
Not stored in SQLite. Stored in Streamlit's `st.session_state` as an in-memory stack to support Undo/Redo during the current session.
- `action_type` (TEXT): "REGISTER", "EXECUTE", "REMOVE"
- `target_id` (INTEGER): Reference to the `SkillUpgrade.id`
- `previous_state` (DICT): The state of the record before the action (used for Undo).

## Master Data (マスタデータ)

### `master_data.json`
Located at `src/data/master_data.json`.
- `weapon_types` / `elements`: 基本マスタ
- `series_skills` / `group_skills`: スキル名称の定義
- `production_bonuses`: 基礎攻撃, 会心
- `kyogeki_enhancements`: 攻撃激化, 会心激化, 属性激化
- `restoration_bonuses`: ボーナス種別ごとのレベル定義（1〜3, EX, 無印）

## Relationships
- Single user local database, so no explicit User foreign keys are needed for MVP.
