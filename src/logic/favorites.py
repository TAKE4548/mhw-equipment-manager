import pandas as pd
import uuid
import streamlit as st
from src.database.storage_manager import load_data, save_data
from src.logic.history import push_action

FAVORITES_TABLE = "favorites"
FAVORITES_COLUMNS = ["id", "favorite_type", "skill_value"]

@st.cache_data
def get_favorites(user_id: str) -> pd.DataFrame:
    """Returns the favorites dataframe from storage. Cached by user_id."""
    return load_data(FAVORITES_TABLE, required_columns=FAVORITES_COLUMNS)

def add_favorite(fav_type: str, skill_val: str) -> bool:
    """Adds a skill to favorites if not already present."""
    from src.components.auth import get_current_user_id
    user_id = get_current_user_id()
    df = get_favorites(user_id)
    # Check if already exists
    if not df.empty and not df[(df['favorite_type'] == fav_type) & (df['skill_value'] == skill_val)].empty:
        return True
    
    prev_df = df.copy()
    new_row = {
        "id": str(uuid.uuid4()),
        "favorite_type": fav_type,
        "skill_value": skill_val
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    success = save_data(FAVORITES_TABLE, df)
    if success:
        get_favorites.clear()
        push_action("ADD_FAVORITE", FAVORITES_TABLE, prev_df, df)
    return success

def remove_favorite(fav_type: str, skill_val: str) -> bool:
    """Removes a skill from favorites."""
    from src.components.auth import get_current_user_id
    user_id = get_current_user_id()
    df = get_favorites(user_id)
    if df.empty: return True
    
    prev_df = df.copy()
    # Filtering out the record
    df = df[~((df['favorite_type'] == fav_type) & (df['skill_value'] == skill_val))]
    success = save_data(FAVORITES_TABLE, df)
    if success:
        get_favorites.clear()
        push_action("REMOVE_FAVORITE", FAVORITES_TABLE, prev_df, df)
    return success

def is_favorite(fav_type: str, skill_val: str) -> bool:
    """Checks if a skill is in favorites."""
    from src.components.auth import get_current_user_id
    user_id = get_current_user_id()
    df = get_favorites(user_id)
    if df.empty: return False
    return not df[(df['favorite_type'] == fav_type) & (df['skill_value'] == skill_val)].empty

def get_favorite_list(fav_type: str) -> list:
    """Returns a simple list of favorite values for a specific type."""
    from src.components.auth import get_current_user_id
    user_id = get_current_user_id()
    df = get_favorites(user_id)
    if df.empty: return []
    return df[df['favorite_type'] == fav_type]['skill_value'].tolist()

def prepare_skill_choices(master_skills: list[dict], fav_list: list[str], key_name: str) -> tuple[list[dict], list[str]]:
    """
    Sorts master skills so favorites come first.
    Returns (sorted_skills, labels_with_stars).
    """
    fav_items = [s for s in master_skills if s[key_name] in fav_list]
    other_items = [s for s in master_skills if s[key_name] not in fav_list]
    sorted_skills = fav_items + other_items
    
    labels = []
    for s in sorted_skills:
        val = s[key_name]
        is_fav = val in fav_list
        prefix = "⭐ " if is_fav else ""
        if val == "なし":
            labels.append("なし")
        else:
            name = s.get('skill_name', '')
            labels.append(f"{prefix}{val} ({name})")
            
    return sorted_skills, labels
