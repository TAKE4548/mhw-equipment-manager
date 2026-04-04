import pandas as pd
import time
from src.database.gsheets_manager import load_data, save_data

def register_upgrade(weapon_type: str, element: str, series_skill: str, group_skill: str, count: int) -> int:
    """Registers a new skill upgrade in Google Sheets and returns its ID."""
    df = load_data()
    
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
    
    if df.empty:
        df = pd.DataFrame([new_row])
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    save_data(df)
    return new_id

def get_active_upgrades() -> pd.DataFrame:
    """Returns active upgrades from Google Sheets as a DataFrame."""
    df = load_data()
    if df.empty:
        return pd.DataFrame(columns=["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"])
    
    # Filter and sort
    active_df = df[df["remaining_count"] > 0].copy()
    active_df = active_df.sort_values(by="remaining_count", ascending=True)
    return active_df

def execute_upgrade(record_id: int, decrement: int = 1) -> bool:
    """Decrements remaining_count by decrement in Google Sheets."""
    df = load_data()
    if df.empty:
        return False
    
    # Update the specific row
    idx = df[df["id"] == record_id].index
    if not idx.empty:
        df.loc[idx, "remaining_count"] = df.loc[idx, "remaining_count"].apply(lambda x: max(0, x - decrement))
        save_data(df)
        return True
    return False

def execute_all_upgrades(decrement: int) -> bool:
    """Decrements remaining_count by decrement for all active records in Google Sheets."""
    df = load_data()
    if df.empty:
        return False
    
    # Update all active rows
    active_mask = df["remaining_count"] > 0
    df.loc[active_mask, "remaining_count"] = df.loc[active_mask, "remaining_count"].apply(lambda x: max(0, x - decrement))
    
    save_data(df)
    return True

def delete_upgrade(record_id: int) -> bool:
    """Removes a specific upgrade record from Google Sheets."""
    df = load_data()
    if df.empty:
        return False
    
    idx = df[df["id"] == record_id].index
    if not idx.empty:
        df = df.drop(idx)
        save_data(df)
        return True
    return False
