# UI - Logic Interface Contracts

Because this is a Streamlit application, we define the contract between the `app.py`/`pages/` (View) and `src/logic/` (Controller/Model).

## `src/logic/equipment.py`

### `register_upgrade(weapon_type: str, element: str, series_skill: str, group_skill: str, count: int) -> int`
Registers a new skill upgrade in the SQLite database. Returns the new record ID.

### `execute_upgrade(record_id: int, decrement: int = 1) -> bool`
Decrements the `remaining_count` for the given record by `decrement`. Returns True if successful. If count reaches 0, the record is removed or marked as completed.

### `get_active_upgrades() -> pd.DataFrame`
Retrieves all active skill upgrades (`remaining_count` > 0) as a Pandas DataFrame for easy rendering in Streamlit.

## `src/logic/history.py`

### `undo_last_action() -> bool`
Pops the last action from the undo stack, reverses its effect in the database, and pushes it to the redo stack.

### `redo_last_action() -> bool`
Pops the last action from the redo stack, applies its effect in the database, and pushes it to the undo stack.
