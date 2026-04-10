# High-Level Design: REQ-029 Weapon Lock Functionality

## Goal
Replace the "Favorite" star with a "Lock" mechanism that strictly prevents editing and deletion of protected weapons. Ensure clear visual feedback (locked icon and tooltips) for a premium "Safety First" experience.

## Proposed Changes

### 1. Data Model (Schema Refinement)
Rename `is_favorite` to `is_locked` in the `weapons` table.

- **File**: [storage_manager.py](file:///c:/Users/audih/ws/hogehoge/mhw-equipment-manager/src/database/storage_manager.py)
    - Update `columns_map["weapons"]`: `"is_favorite"` -> `"is_locked"`.
- **File**: [equipment_box.py](file:///c:/Users/audih/ws/hogehoge/mhw-equipment-manager/src/logic/equipment_box.py)
    - Update `EQUIPMENT_COLUMNS`: `"is_favorite"` -> `"is_locked"`.
    - Rename `toggle_favorite` -> `toggle_lock`.
    - Update `load_equipment`: Ensure `is_locked` is cast to bool and handle legacy `is_favorite` data if possible.

### 2. UI Layer (UX-12 Update)
Enforce strict operation blocking.

- **File**: [list.py](file:///c:/Users/audih/ws/hogehoge/mhw-equipment-manager/src/components/box/list.py)
    - **Visual**: Show 🔒 icon next to weapon name if `is_locked` is True.
    - **Actions**:
        - Toggle button in popover: Change labels/icons to "🔒 ロック" / "🔓 ロック解除".
        - Edit button: Set `disabled=row['is_locked']` and `help="ロック中のため編集できません"`.
        - Delete button: Set `disabled=row['is_locked']` and `help="ロック中のため削除できません"`.
- **File**: [dialogs.py](file:///c:/Users/audih/ws/hogehoge/mhw-equipment-manager/src/components/box/dialogs.py)
    - (Optional) Use `is_locked` in the edit dialog to disable fields if accessed directly (though the button will be disabled).

### 3. Migration Note
Since `is_favorite` was only just introduced, we will attempt to value-map `is_favorite` to `is_locked` during the next load, then fully transition.

## Verification Plan
1. **Toggle Lock**: Verify the 🔒 icon appears and buttons become disabled.
2. **Tooltip**: Hover over disabled buttons to verify the help text.
3. **Protection**: Try to click disabled buttons (should be impossible).
4. **Cloud Sync**: Document the need to rename the column in Supabase.
