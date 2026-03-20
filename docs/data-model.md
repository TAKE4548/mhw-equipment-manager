# Data Model: MHWs Equipment Manager

## Entities

### `SkillUpgrade` (スキル強化レコード)
Represents a user's registered skill upgrade target.
- `id` (INTEGER PRIMARY KEY)
- `weapon_type` (TEXT, required): e.g., "大剣", "太刀"
- `element` (TEXT, required): e.g., "火", "水", "無"
- `series_skill` (TEXT, required): e.g., "火竜の奥義"
- `group_skill` (TEXT, required): e.g., "星"
- `remaining_count` (INTEGER, required): The number of upgrades left. Must be >= 0.

### `ActionHistory` (アクション履歴)
Not stored in SQLite. Stored in Streamlit's `st.session_state` as an in-memory stack to support Undo/Redo during the current session.
- `action_type` (TEXT): "REGISTER", "EXECUTE", "REMOVE"
- `target_id` (INTEGER): Reference to the `SkillUpgrade.id`
- `previous_state` (DICT): The state of the record before the action (used for Undo).

## Master Data (マスタデータ)

### `master_data.json`
Located at `src/data/master_data.json`.
- `weapon_types` (ARRAY of TEXT): List of weapon types.
- `elements` (ARRAY of TEXT): List of elemental types.
- `series_skills` (ARRAY of OBJECT): 
  - `skill_parts` (TEXT): The series part name (e.g., "闢獣の力").
  - `skill_name` (TEXT): The activated skill name (e.g., "力自慢").
- `group_skills` (ARRAY of OBJECT):
  - `group_name` (TEXT): The group name (e.g., "毛皮の昂揚").
  - `skill_name` (TEXT): The activated skill name (e.g., "不屈").

## Relationships
- Single user local database, so no explicit User foreign keys are needed for MVP.
