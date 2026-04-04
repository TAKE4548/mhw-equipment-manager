import pandas as pd
import time
from src.database.storage_manager import load_data, save_data

UPGRADES_TABLE = "upgrades"
UPGRADES_COLUMNS = ["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"]

def register_upgrade(weapon_type: str, element: str, series_skill: str, group_skill: str, count: int) -> int:
    """Registers a new skill upgrade in storage and returns its ID."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df is None: return None
    
    # Generate unique ID
    new_id = int(time.time() * 1000)
    
    new_row = {
        "id": new_id,
        "weapon_type": weapon_type,
        "element": element,
        "series_skill": series_skill,
        "group_skill": group_skill,
        "remaining_count": count
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(UPGRADES_TABLE, df)
    return new_id

def get_active_upgrades():
    """Returns active upgrades from storage as a DataFrame. Returns None if loading."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df is None: return None
    
    if df.empty:
        return pd.DataFrame(columns=UPGRADES_COLUMNS)
    
    # Filter and sort
    active_df = df[df["remaining_count"] > 0].copy()
    active_df = active_df.sort_values(by="remaining_count", ascending=True)
    return active_df

def execute_upgrade(record_id: int, decrement: int = 1) -> bool:
    """Decrements remaining_count by decrement in storage."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df is None or df.empty: return False
    
    # Update the specific row
    idx = df[df["id"] == record_id].index
    if not idx.empty:
        df.loc[idx, "remaining_count"] = df.loc[idx, "remaining_count"].apply(lambda x: max(0, int(x) - decrement))
        save_data(UPGRADES_TABLE, df)
        return True
    return False

def execute_all_upgrades(decrement: int) -> bool:
    """Decrements remaining_count by decrement for all active records in storage."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df is None or df.empty: return False
    
    # Update all active rows
    active_mask = df["remaining_count"] > 0
    df.loc[active_mask, "remaining_count"] = df.loc[active_mask, "remaining_count"].apply(lambda x: max(0, int(x) - decrement))
    
    save_data(UPGRADES_TABLE, df)
    return True

def delete_upgrade(record_id: int) -> bool:
    """Removes a specific upgrade record from storage."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df is None or df.empty: return False
    
    idx = df[df["id"] == record_id].index
    if not idx.empty:
        df = df.drop(idx)
        save_data(UPGRADES_TABLE, df)
        return True
    return False
