# High-Level Design: REQ-017 Favorite Protection for Weapons

## Goal
Implement a protection mechanism to prevent accidental deletion of favorite weapons, ensuring data safety for high-value equipment.

## Proposed Changes

### 1. Data Model (Schema Update)
Add `is_favorite` boolean field to the `weapons` table.

- **File**: [storage_manager.py](file:///c:/Users/audih/ws/hogehoge/mhw-equipment-manager/src/database/storage_manager.py)
    - Update `columns_map["weapons"]` to include `"is_favorite"`.

### 2. Logic Layer
Handle the new field in CRUD operations and provide a toggle function.

- **File**: [equipment_box.py](file:///c:/Users/audih/ws/hogehoge/mhw-equipment-manager/src/logic/equipment_box.py)
    - Update `EQUIPMENT_COLUMNS` to include `"is_favorite"`.
    - Implement `toggle_favorite(equipment_id, user_id)` function.
    - Update `add_equipment` (default to `False`) and `update_equipment` (persist current value).

### 3. UI Layer (UX-12)
Provide a way to mark favorites and intercept deletion.

- **File**: [list.py](file:///c:/Users/audih/ws/hogehoge/mhw-equipment-manager/src/components/box/list.py)
    - Add a favorite toggle button (⭐ icon) to the item menu (`⋮` popover).
    - Modify the "Delete" button logic:
        - If `is_favorite` is `False`: Delete normally.
        - If `is_favorite` is `True`: Trigger `confirm_delete_dialog`.

- **File**: [dialogs.py](file:///c:/Users/audih/ws/hogehoge/mhw-equipment-manager/src/components/box/dialogs.py)
    - Add `confirm_delete_dialog`: A Streamlit `@st.dialog` that clearly warns the user they are about to delete a favorite item and requires a final click to confirm.

## Verification Plan

### Automated/Manual Tests
- Register a weapon and mark it as favorite.
- Attempt to delete the favorite weapon -> Verify confirmation dialog appears.
- Cancel deletion -> Verify weapon remains.
- Confirm deletion in dialog -> Verify weapon is deleted.
- Unmark favorite -> Verify normal deletion works.
