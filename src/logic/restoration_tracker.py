import pandas as pd
import uuid
import streamlit as st
from src.database.gsheets_manager import load_data, save_data
from src.logic.equipment_box import load_equipment, save_equipment

TRACKER_WORKSHEET = "RestorationTracker"
TRACKER_COLUMNS = [
    "id", "weapon_id", "remaining_count", 
    "target_rest_1_type", "target_rest_1_level",
    "target_rest_2_type", "target_rest_2_level",
    "target_rest_3_type", "target_rest_3_level",
    "target_rest_4_type", "target_rest_4_level",
    "target_rest_5_type", "target_rest_5_level"
]

# --- History Management ---

def push_history():
    """Saves current state of Equipment and Trackers to undo stack."""
    if 'history_undo' not in st.session_state:
        st.session_state.history_undo = []
    if 'history_redo' not in st.session_state:
        st.session_state.history_redo = []
        
    eq_df = load_equipment().copy()
    tr_df = load_trackers().copy()
    
    st.session_state.history_undo.append((eq_df, tr_df))
    # Cap history at 5
    if len(st.session_state.history_undo) > 5:
        st.session_state.history_undo.pop(0)
    # Clear redo on new action
    st.session_state.history_redo = []

def undo_action():
    if not st.session_state.get('history_undo'):
        return False
        
    current_eq = load_equipment().copy()
    current_tr = load_trackers().copy()
    st.session_state.history_redo.append((current_eq, current_tr))
    
    prev_eq, prev_tr = st.session_state.history_undo.pop()
    save_equipment(prev_eq)
    save_trackers(prev_tr)
    return True

def redo_action():
    if not st.session_state.get('history_redo'):
        return False
        
    current_eq = load_equipment().copy()
    current_tr = load_trackers().copy()
    st.session_state.history_undo.append((current_eq, current_tr))
    
    next_eq, next_tr = st.session_state.history_redo.pop()
    save_equipment(next_eq)
    save_trackers(next_tr)
    return True

# --- Tracker Logic ---

def load_trackers() -> pd.DataFrame:
    df = load_data(worksheet=TRACKER_WORKSHEET, required_columns=TRACKER_COLUMNS)
    if "remaining_count" in df.columns:
        df["remaining_count"] = pd.to_numeric(df["remaining_count"], errors="coerce").fillna(0).astype(int)
    return df

def save_trackers(df: pd.DataFrame) -> bool:
    return save_data(df, worksheet=TRACKER_WORKSHEET)

def register_tracker(weapon_id: str, count: int, rest_bonuses: list[dict]) -> str:
    push_history()
    df = load_trackers()
    new_id = str(uuid.uuid4())
    new_row = {
        "id": new_id,
        "weapon_id": weapon_id,
        "remaining_count": count
    }
    
    for i in range(5):
        if i < len(rest_bonuses):
            new_row[f"target_rest_{i+1}_type"] = rest_bonuses[i].get("type", "なし")
            new_row[f"target_rest_{i+1}_level"] = rest_bonuses[i].get("level", "なし")
        else:
            new_row[f"target_rest_{i+1}_type"] = "なし"
            new_row[f"target_rest_{i+1}_level"] = "なし"
            
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    if save_trackers(df):
        return new_id
    return None

def advance_all_trackers(amount: int = 1) -> bool:
    """Decrements remaining_count for ALL trackers and removes those that are skipped (count <= 0)."""
    push_history()
    df = load_trackers()
    if df.empty:
        return False
        
    df["remaining_count"] = df["remaining_count"] - amount
    # According to user: records with count <= 0 are skipped and should be deleted
    df = df[df["remaining_count"] > 0]
    
    return save_trackers(df)

def execute_apply_and_advance(tracker_id: str) -> bool:
    """Applies the target bonus to the weapon and advances the global table by N, skipping pass-over rows."""
    tr_df = load_trackers()
    if tr_df.empty: return False
    
    target_row = tr_df[tr_df['id'] == tracker_id]
    if target_row.empty: return False
    
    push_history()
    
    row = target_row.iloc[0]
    weapon_id = row['weapon_id']
    n_advance = int(row['remaining_count'])
    
    # 1. Update Weapon in EquipmentBox
    eq_df = load_equipment()
    eq_idx = eq_df.index[eq_df['id'] == weapon_id].tolist()
    if eq_idx:
        idx = eq_idx[0]
        for i in range(1, 6):
            eq_df.at[idx, f'rest_{i}_type'] = row[f'target_rest_{i}_type']
            eq_df.at[idx, f'rest_{i}_level'] = row[f'target_rest_{i}_level']
        save_equipment(eq_df)
    
    # 2. Advance all trackers by N and purge those <= 0
    tr_df["remaining_count"] = tr_df["remaining_count"] - n_advance
    tr_df = tr_df[tr_df["remaining_count"] > 0]
    
    return save_trackers(tr_df)

def delete_tracker(tracker_id: str) -> bool:
    push_history()
    df = load_trackers()
    if df.empty: return False
    df = df[df["id"] != tracker_id]
    return save_trackers(df)
