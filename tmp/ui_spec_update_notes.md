# UI Spec Update Request for Architect

Regarding the recent implementation of Phase 9/10/11, please update `docs/ui_spec.md` with the following changes to ensure consistency with the current codebase:

## 1. Talisman Management (鑑定護石管理)
- **New Feature: Edit Functionality**
    - Added an "Edit (✏️)" button to each talisman card in the grid view.
    - Added a dedicated "Edit Talisman" dialog (`st.dialog`) that allows users to modify rarity, skills, and slots.
    - The dialog includes real-time validation against `talisman_master.json`.
    - **UX Rule**: Edits are recorded in the global Undo/Redo history (integrated with `push_action`).

## 2. Skills Lottery (スキル抽選結果)
- **Auto-Deletion Logic**: 
    - When a lottery's `remaining_count` reaches 0 (either via manual decrement or "Apply to Weapon"), the record is automatically removed from the tracking list.
    - Updated UI behavior to reflect this "completion = removal" flow.

## 3. Global State & Performance
- **Undo/Redo Extension**:
    - The global Undo/Redo toolbar now fully supports Talisman operations (Add/Delete/Update).
- **Cache Invalidation**:
    - Explicitly documented that any data mutation (Lottery, Trackers, Talismans) triggers an immediate cache clear (`load_*.clear()`) to maintain multi-page consistency.

Please integrate these into the appropriate sections of `docs/ui_spec.md` and ensure alignment with the established design system.
