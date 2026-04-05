import streamlit as st
import pandas as pd
import uuid
from src.logic.master import get_master_data
from src.database.storage_manager import load_data, save_data, delete_record
from src.logic.history import push_action
from src.logic.equipment_box import update_equipment_skills

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
    if save_data(UPGRADES_TABLE, df):
        push_action("REGISTER_UPGRADE", UPGRADES_TABLE, pd.DataFrame(columns=UPGRADES_COLUMNS), df)
        return new_id
    return None

def get_active_upgrades() -> pd.DataFrame:
    """Returns active upgrades from storage as a DataFrame."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df.empty:
        return pd.DataFrame(columns=UPGRADES_COLUMNS)
    active_df = df[df["remaining_count"] > 0].copy()
    active_df = active_df.sort_values(by="remaining_count", ascending=True)
    return active_df

def execute_upgrade(record_id: str, decrement: int = 1, weapon_id: str = None) -> bool:
    """Decrements count and optionally updates weapon skills."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df.empty: return False
    
    idx = df[df["id"].astype(str) == str(record_id)].index
    if not idx.empty:
        row = df.loc[idx[0]]
        # 1. Sync skills to weapon if weapon_id provided
        if weapon_id:
            update_equipment_skills(weapon_id, row['series_skill'], row['group_skill'])
            
        # 2. Proceed the count for ALL records (Shared Table Logic)
        return execute_all_upgrades(decrement)
    return False

def execute_all_upgrades(decrement: int = 1) -> bool:
    """Decrements remaining_count for all entries and records history."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df.empty: return True
    
    prev_df = df.copy()
    df["remaining_count"] = df["remaining_count"].apply(lambda x: max(0, int(x) - decrement))
    
    if save_data(UPGRADES_TABLE, df):
        push_action("EXECUTE_ALL", UPGRADES_TABLE, prev_df, df)
        return True
    return False

def delete_upgrade(record_id: str) -> bool:
    """Deletes an upgrade record and records history."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    idx = df[df["id"].astype(str) == str(record_id)].index
    if not idx.empty:
        prev_df = df.copy()
        df = df.drop(idx)
        if save_data(UPGRADES_TABLE, df):
            push_action("DELETE_UPGRADE", UPGRADES_TABLE, prev_df, df)
            return True
    return False

def filter_upgrades(df: pd.DataFrame,
                    weapon_types: list = None,
                    elements: list = None,
                    series_skills: list = None,
                    group_skills: list = None,
                    sort_by: str = "残り回数順") -> pd.DataFrame:
    """Filters the upgrades dataframe."""
    if df.empty: return df
    
    filtered_df = df.copy()
    if weapon_types: filtered_df = filtered_df[filtered_df['weapon_type'].isin(weapon_types)]
    if elements: filtered_df = filtered_df[filtered_df['element'].isin(elements)]
    if series_skills: filtered_df = filtered_df[filtered_df['series_skill'].isin(series_skills)]
    if group_skills: filtered_df = filtered_df[filtered_df['group_skill'].isin(group_skills)]
        
    master = get_master_data()
    w_order = master.get("weapon_types", [])
    e_order = master.get("elements", [])
    filtered_df['weapon_type'] = pd.Categorical(filtered_df['weapon_type'], categories=w_order, ordered=True)
    filtered_df['element'] = pd.Categorical(filtered_df['element'], categories=e_order, ordered=True)

    if sort_by == "武器種順":
        filtered_df = filtered_df.sort_values(by=["weapon_type", "element", "remaining_count"])
    elif sort_by == "属性順":
        filtered_df = filtered_df.sort_values(by=["element", "weapon_type", "remaining_count"])
    else: # 残り回数順
        filtered_df = filtered_df.sort_values(by="remaining_count", ascending=True)
    return filtered_df

def update_upgrade(record_id: str, weapon_type: str, element: str, 
                   series_skill: str, group_skill: str, count: int) -> bool:
    """Updates an existing skill upgrade record."""
    df = load_data(UPGRADES_TABLE, required_columns=UPGRADES_COLUMNS)
    if df.empty: return False
    idx = df[df["id"].astype(str) == str(record_id)].index
    if not idx.empty:
        prev_df = df.copy()
        df.at[idx[0], "weapon_type"] = weapon_type
        df.at[idx[0], "element"] = element
        df.at[idx[0], "series_skill"] = series_skill
        df.at[idx[0], "group_skill"] = group_skill
        df.at[idx[0], "remaining_count"] = count
        if save_data(UPGRADES_TABLE, df):
            push_action("UPDATE_UPGRADE", UPGRADES_TABLE, prev_df, df)
            return True
    return False
