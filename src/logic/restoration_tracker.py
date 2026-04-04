import pandas as pd
import streamlit as st
import uuid
from src.database.storage_manager import load_data, save_data

TRACKER_TABLE = "trackers"
TRACKER_COLUMNS = [
    "id", "weapon_id", "remaining_count",
    "target_rest_1_type", "target_rest_1_level",
    "target_rest_2_type", "target_rest_2_level",
    "target_rest_3_type", "target_rest_3_level",
    "target_rest_4_type", "target_rest_4_level",
    "target_rest_5_type", "target_rest_5_level"
]

def record_history(action_type: str, prev_data: pd.DataFrame, next_data: pd.DataFrame):
    st.session_state.history_undo.append({
        'action_type': action_type,
        'prev': prev_data.copy(),
        'next': next_data.copy()
    })
    st.session_state.history_redo = []

def undo_action() -> bool:
    if not st.session_state.history_undo:
        return False
    action = st.session_state.history_undo.pop()
    st.session_state.history_redo.append(action)
    save_data(TRACKER_TABLE, action['prev'])
    return True

def redo_action() -> bool:
    if not st.session_state.history_redo:
        return False
    action = st.session_state.history_redo.pop()
    st.session_state.history_undo.append(action)
    save_data(TRACKER_TABLE, action['next'])
    return True

def load_trackers() -> pd.DataFrame:
    df = load_data(TRACKER_TABLE, required_columns=TRACKER_COLUMNS)
    if "remaining_count" in df.columns:
        df["remaining_count"] = pd.to_numeric(df["remaining_count"], errors="coerce").fillna(0).astype(int)
    return df

def register_tracker(weapon_id: str, remaining_count: int, target_bonuses: list[dict]) -> bool:
    df = load_trackers()
    prev_df = df.copy()
    new_id = str(uuid.uuid4())
    new_row = {"id": new_id, "weapon_id": weapon_id, "remaining_count": remaining_count}
    for i in range(5):
        rt, rl = f"target_rest_{i+1}_type", f"target_rest_{i+1}_level"
        if i < len(target_bonuses):
            new_row[rt] = target_bonuses[i].get("type", "なし")
            new_row[rl] = target_bonuses[i].get("level", "なし")
        else:
            new_row[rt] = "なし"
            new_row[rl] = "なし"
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    if save_data(TRACKER_TABLE, df):
        record_history("REGISTER", prev_df, df)
        return True
    return False

def advance_all_trackers(decrement: int = 1) -> bool:
    df = load_trackers()
    if df.empty: return False
    prev_df = df.copy()
    df["remaining_count"] = df["remaining_count"].apply(lambda x: max(0, x - decrement))
    if save_data(TRACKER_TABLE, df):
        record_history("ADVANCE_ALL", prev_df, df)
        return True
    return False

def delete_tracker(tracker_id: str) -> bool:
    df = load_trackers()
    if df.empty: return False
    prev_df = df.copy()
    df = df[df["id"] != tracker_id]
    if save_data(TRACKER_TABLE, df):
        record_history("DELETE", prev_df, df)
        return True
    return False

def execute_apply_and_advance(tracker_id: str) -> bool:
    from src.logic.equipment_box import load_equipment, save_equipment
    trackers_df = load_trackers()
    eq_df = load_equipment()
    if trackers_df.empty or eq_df.empty: return False
    target_tracker = trackers_df[trackers_df["id"] == tracker_id]
    if target_tracker.empty: return False
    tracker_row = target_tracker.iloc[0]
    w_id = tracker_row["weapon_id"]
    idx = eq_df.index[eq_df['id'] == w_id].tolist()
    if idx:
        for i in range(1, 6):
            eq_df.at[idx[0], f"rest_{i}_type"] = tracker_row[f"target_rest_{i}_type"]
            eq_df.at[idx[0], f"rest_{i}_level"] = tracker_row[f"target_rest_{i}_level"]
        save_equipment(eq_df)
    return advance_all_trackers(1)
