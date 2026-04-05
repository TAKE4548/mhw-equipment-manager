import streamlit as st
import pandas as pd
import uuid
from src.logic.master import get_master_data
from src.database.storage_manager import load_data, save_data

UPGRADES_TABLE = "upgrades"
UPGRADES_COLUMNS = ["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"]

def register_upgrade(weapon_type: str, element: str, series_skill: str, group_skill: str, count: int) -> str:
    """Registers a new skill upgrade in storage and returns its ID."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    new_id = str(uuid.uuid4())
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

def get_active_upgrades() -> pd.DataFrame:
    """Returns active upgrades from storage as a DataFrame."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df.empty:
        return pd.DataFrame(columns=UPGRADES_COLUMNS)
    active_df = df[df["remaining_count"] > 0].copy()
    active_df = active_df.sort_values(by="remaining_count", ascending=True)
    return active_df

def execute_upgrade(record_id: str, decrement: int = 1) -> bool:
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df.empty: return False
    idx = df[df["id"].astype(str) == str(record_id)].index
    if not idx.empty:
        df.loc[idx, "remaining_count"] = df.loc[idx, "remaining_count"].apply(lambda x: max(0, int(x) - decrement))
        save_data(UPGRADES_TABLE, df)
        return True
    return False

def execute_all_upgrades(decrement: int) -> bool:
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df.empty: return False
    active_mask = df["remaining_count"] > 0
    df.loc[active_mask, "remaining_count"] = df.loc[active_mask, "remaining_count"].apply(lambda x: max(0, int(x) - decrement))
    save_data(UPGRADES_TABLE, df)
    return True

def delete_upgrade(record_id: str) -> bool:
    from src.database.storage_manager import delete_record
    return delete_record(UPGRADES_TABLE, record_id)

def filter_upgrades(df: pd.DataFrame,
                    weapon_types: list = None,
                    elements: list = None,
                    series_skills: list = None,
                    group_skills: list = None,
                    sort_by: str = "残り回数順") -> pd.DataFrame:
    """Filters the upgrades dataframe."""
    if df.empty: return df
    
    filtered_df = df.copy()
    
    if weapon_types:
        filtered_df = filtered_df[filtered_df['weapon_type'].isin(weapon_types)]
    if elements:
        filtered_df = filtered_df[filtered_df['element'].isin(elements)]
    if series_skills:
        filtered_df = filtered_df[filtered_df['series_skill'].isin(series_skills)]
    if group_skills:
        filtered_df = filtered_df[filtered_df['group_skill'].isin(group_skills)]
        
    # --- MASTER DATA SORTING ---
    master = get_master_data()
    w_order = master.get("weapon_types", [])
    e_order = master.get("elements", [])
    
    # Temporarily convert to Categorical for sorting
    filtered_df['weapon_type'] = pd.Categorical(filtered_df['weapon_type'], categories=w_order, ordered=True)
    filtered_df['element'] = pd.Categorical(filtered_df['element'], categories=e_order, ordered=True)

    if sort_by == "武器種順":
        filtered_df = filtered_df.sort_values(by=["weapon_type", "element", "remaining_count"])
    elif sort_by == "属性順":
        filtered_df = filtered_df.sort_values(by=["element", "weapon_type", "remaining_count"])
    else: # 残り回数順 (Default)
        filtered_df = filtered_df.sort_values(by="remaining_count", ascending=True)
        
    return filtered_df
def update_upgrade(record_id: str, weapon_type: str, element: str, 
                   series_skill: str, group_skill: str, count: int) -> bool:
    """Updates an existing skill upgrade record."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df.empty: return False
    idx = df[df["id"].astype(str) == str(record_id)].index
    if not idx.empty:
        df.at[idx[0], "weapon_type"] = weapon_type
        df.at[idx[0], "element"] = element
        df.at[idx[0], "series_skill"] = series_skill
        df.at[idx[0], "group_skill"] = group_skill
        df.at[idx[0], "remaining_count"] = count
        save_data(UPGRADES_TABLE, df)
        return True
    return False
