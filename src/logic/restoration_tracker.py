import pandas as pd
import streamlit as st
import uuid
from src.database.storage_manager import load_data, save_data
from src.logic.history import push_action
from src.logic.equipment_box import load_equipment, save_equipment

TRACKER_TABLE = "trackers"
TRACKER_COLUMNS = [
    "id", "weapon_id", "remaining_count",
    "target_rest_1_type", "target_rest_1_level",
    "target_rest_2_type", "target_rest_2_level",
    "target_rest_3_type", "target_rest_3_level",
    "target_rest_4_type", "target_rest_4_level",
    "target_rest_5_type", "target_rest_5_level"
]

@st.cache_data
def load_trackers() -> pd.DataFrame:
    """Loads all restoration trackers from the database."""
    df = load_data(TRACKER_TABLE, required_columns=TRACKER_COLUMNS)
    if not df.empty and "remaining_count" in df.columns:
        df["remaining_count"] = pd.to_numeric(df["remaining_count"], errors="coerce").fillna(0).astype(int)
    return df

def save_trackers(df: pd.DataFrame) -> bool:
    """Saves restoration trackers to the database."""
    return save_data(TRACKER_TABLE, df)

def register_tracker(weapon_id: str, remaining_count: int, target_bonuses: list[dict]) -> bool:
    """Registers a new restoration tracker and records history."""
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
    if save_trackers(df):
        load_trackers.clear()
        push_action("REGISTER_TRACKER", TRACKER_TABLE, prev_df, df)
        return True
    return False

def advance_all_trackers(decrement: int) -> bool:
    """Decrements all trackers and removes those that reach 0."""
    df = load_trackers()
    if df.empty: return True
    
    prev_df = df.copy()
    df["remaining_count"] = df["remaining_count"].apply(lambda x: max(0, int(x) - decrement))
    # Auto-remove completed trackers
    df = df[df["remaining_count"] > 0]
    
    if save_trackers(df):
        load_trackers.clear()
        push_action("ADVANCE_ALL", TRACKER_TABLE, prev_df, df)
        return True
    return False

def execute_apply_and_advance(tracker_id: str) -> bool:
    """Applies target bonuses to weapon and advances all trackers."""
    df = load_trackers()
    idx = df[df["id"].astype(str) == str(tracker_id)].index
    if idx.empty: return False
    
    row = df.loc[idx[0]]
    eq_df = load_equipment()
    
    w_idx = eq_df[eq_df["id"].astype(str) == str(row["weapon_id"])].index
    if not w_idx.empty:
        prev_eq_df = eq_df.copy()
        for i in range(1, 6):
            eq_df.at[w_idx[0], f"rest_{i}_type"] = row[f"target_rest_{i}_type"]
            eq_df.at[w_idx[0], f"rest_{i}_level"] = row[f"target_rest_{i}_level"]
        if save_equipment(eq_df):
            load_equipment.clear()
            push_action("APPLY_UPGRADE", "equipment", prev_eq_df, eq_df)
        
    return advance_all_trackers(int(row["remaining_count"]))

def delete_tracker(tracker_id: str) -> bool:
    """Deletes a tracker record and records history."""
    df = load_trackers()
    idx = df[df["id"].astype(str) == str(tracker_id)].index
    if not idx.empty:
        prev_df = df.copy()
        df = df.drop(idx)
        if save_trackers(df):
            load_trackers.clear()
            push_action("DELETE_TRACKER", TRACKER_TABLE, prev_df, df)
            return True
    return False

def update_tracker(tracker_id: str, remaining_count: int, target_bonuses: list[dict]) -> bool:
    """Updates an existing tracker and records history."""
    df = load_trackers()
    idx = df[df["id"].astype(str) == str(tracker_id)].index
    if idx.empty: return False
    
    prev_df = df.copy()
    df.at[idx[0], "remaining_count"] = remaining_count
    for i in range(5):
        rt, rl = f"target_rest_{i+1}_type", f"target_rest_{i+1}_level"
        if i < len(target_bonuses):
            df.at[idx[0], rt] = target_bonuses[i].get("type", "なし")
            df.at[idx[0], rl] = target_bonuses[i].get("level", "なし")
        else:
            df.at[idx[0], rt] = "なし"
            df.at[idx[0], rl] = "なし"
    
    if save_trackers(df):
        load_trackers.clear()
        push_action("UPDATE_TRACKER", TRACKER_TABLE, prev_df, df)
        return True
    return False
