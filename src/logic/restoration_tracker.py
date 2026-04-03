import pandas as pd
import uuid
from src.database.gsheets_manager import load_data, save_data

TRACKER_WORKSHEET = "RestorationTracker"
TRACKER_COLUMNS = [
    "id", "weapon_id", "remaining_count", 
    "target_rest_1_type", "target_rest_1_level",
    "target_rest_2_type", "target_rest_2_level",
    "target_rest_3_type", "target_rest_3_level",
    "target_rest_4_type", "target_rest_4_level",
    "target_rest_5_type", "target_rest_5_level"
]

def load_trackers() -> pd.DataFrame:
    df = load_data(worksheet=TRACKER_WORKSHEET, required_columns=TRACKER_COLUMNS)
    if "remaining_count" in df.columns:
        df["remaining_count"] = pd.to_numeric(df["remaining_count"], errors="coerce").fillna(0).astype(int)
    return df

def save_trackers(df: pd.DataFrame) -> bool:
    return save_data(df, worksheet=TRACKER_WORKSHEET)

def register_tracker(weapon_id: str, count: int, rest_bonuses: list[dict]) -> str:
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

def advance_all_trackers() -> bool:
    """Decrements remaining_count for ALL trackers (simulates a single rollout across the global table)."""
    df = load_trackers()
    if df.empty:
        return False
        
    df["remaining_count"] = (df["remaining_count"] - 1).clip(lower=0)
    return save_trackers(df)

def delete_tracker(tracker_id: str) -> bool:
    df = load_trackers()
    if df.empty: return False
    df = df[df["id"] != tracker_id]
    return save_trackers(df)
