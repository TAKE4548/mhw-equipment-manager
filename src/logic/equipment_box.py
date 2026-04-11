import pandas as pd
import uuid
import streamlit as st
import functools
from collections import Counter
from src.database.storage_manager import load_data, save_data, delete_record
from src.logic.history import push_action
from src.logic.master import get_master_data
from src.utils.exceptions import LogicValidationError

EQUIPMENT_TABLE = "weapons" # Matches Supabase table name
EQUIPMENT_COLUMNS = [
    "id", "weapon_name", "weapon_type", "element", 
    "current_series_skill", "current_group_skill",
    "enhancement_type",
    "p_bonus_1", "p_bonus_2", "p_bonus_3",
    "rest_1_type", "rest_1_level",
    "rest_2_type", "rest_2_level",
    "rest_3_type", "rest_3_level",
    "rest_4_type", "rest_4_level",
    "rest_5_type", "rest_5_level",
    "is_locked"
]

ATTRIBUTE_COLORS = {
    "火": "#e74c3c", "水": "#3498db", "雷": "#f1c40f", "氷": "#ecf0f1",
    "龍": "#9b59b6", "毒": "#8e44ad", "麻痺": "#f39c12", "睡眠": "#bdc3c7",
    "爆破": "#e67e22", "無": "#95a5a6"
}

ABBR_MAP = {
    "基礎攻撃力増強": "攻撃", "基礎攻撃力強化": "攻撃",
    "会心率増強": "会心", "会心率強化": "会心",
    "属性強化": "属性", "切れ味強化": "切れ味", "装填強化": "装填"
}

NORM_TYPE_MAP = {
    "基礎攻撃": "基礎攻撃力増強", "会心": "会心率増強",
    "属性": "属性強化", "切れ味(近接)": "切れ味強化", "装填数(遠隔)": "装填強化"
}
REST_TYPE_MAP = { "基礎攻撃": "基礎攻撃力強化", "会心": "会心率強化" }
NORM_LV_MAP = {
    "1": "Ⅰ", "2": "Ⅱ", "3": "Ⅲ", "1.0": "Ⅰ", "2.0": "Ⅱ", "3.0": "Ⅲ",
    "無印": "無印", "EX": "EX", "なし": "なし"
}

def normalize_bonus(b_type, b_level=None, is_restoration=False):
    """Maps old terminology and ensures Roman numerals. Returns (type, level) tuple."""
    nt = REST_TYPE_MAP.get(b_type, b_type) if is_restoration else NORM_TYPE_MAP.get(b_type, b_type)
    nl_raw = str(b_level).strip() if b_level and b_level != "なし" else "なし"
    if nl_raw.endswith(".0"): nl_raw = nl_raw[:-2]
    nl = NORM_LV_MAP.get(nl_raw, nl_raw)
    return nt, nl

@functools.lru_cache(maxsize=128)
def get_abbr_item(item: str) -> str:
    """Helper to apply abbreviation to a single item name."""
    if not item or item == "なし": return "なし"
    res = item.replace(".0", "")
    for old, new in NORM_LV_MAP.items():
        if res.endswith(old) and not old.endswith(".0"):
            res = res[:-len(old)] + new
            break
    for full, short in ABBR_MAP.items():
        if res.startswith(full): return f"{short}{res[len(full):]}"
    return res

def get_weapon_label(weapon_id: str, df: pd.DataFrame) -> str:
    """Returns a readable label for a weapon from the equipment dataframe."""
    row = df[df['id'].astype(str) == str(weapon_id)]
    if row.empty:
        return "Unknown Weapon"
    row = row.iloc[0]
    name = row['weapon_name'] if row['weapon_name'] and not str(row['weapon_name']).startswith("無銘の") else row['weapon_type']
    return f"{name} ({row['element']})"

def format_bonus_summary(items: list[str]) -> str:
    """Converts a list of bonus strings using aggregation."""
    items = [i for i in items if i and i != "なし"]
    if not items: return "なし"
    counts = Counter(items); parts = []
    for item, count in counts.items():
        abbr = get_abbr_item(item)
        parts.append(f"{abbr}×{count}" if count > 1 else abbr)
    return " / ".join(parts)

def format_bonus_list(items: list[str]) -> str:
    return " / ".join([get_abbr_item(i) for i in items if i and i != "なし"])

def validate_restoration_bonuses(bonuses: list[dict]):
    """Checks for illegal restoration bonus combinations."""
    combos = [(b.get('type', 'なし'), b.get('level', 'なし')) for b in bonuses if b.get('type', 'なし') != "なし"]
    counts = Counter(combos)
    for (t, lv), count in counts.items():
        if count > 2:
            label = f"{get_abbr_item(t)}[{lv}]" if lv != "無印" else get_abbr_item(t)
            return False, f"Validation Error: Bonus {label} repeated 3+ times."
    return True, ""

@st.cache_data
def load_equipment(user_id: str = "local") -> pd.DataFrame:
    """
    Loads equipment and applies auto-normalization.
    Cached per user_id to ensure multi-user isolation.
    """

    df = load_data(EQUIPMENT_TABLE, required_columns=EQUIPMENT_COLUMNS)
    if not df.empty:
        for idx, row in df.iterrows():
            for i in range(1, 4):
                col = f"p_bonus_{i}"
                nt, _ = normalize_bonus(row[col])
                df.at[idx, col] = nt
            for i in range(1, 6):
                tc, lc = f"rest_{i}_type", f"rest_{i}_level"
                nt, nl = normalize_bonus(row[tc], row[lc], is_restoration=True)
                df.at[idx, tc] = nt; df.at[idx, lc] = nl
        
        # Migration from is_favorite to is_locked
        if "is_favorite" in df.columns:
            if "is_locked" not in df.columns:
                df["is_locked"] = df["is_favorite"]
        
        if "is_locked" in df.columns:
            df["is_locked"] = df["is_locked"].fillna(False).astype(bool)
    return df

def save_equipment(df: pd.DataFrame) -> bool:
    return save_data(EQUIPMENT_TABLE, df)

def add_equipment(weapon_name: str, weapon_type: str, element: str, 
                  current_series_skill: str, current_group_skill: str, enhancement_type: str,
                  p_bonuses: list, restoration_bonuses: list, user_id: str = "local"):
    """Adds a new equipment and records history."""
    # 0. Validation
    if not weapon_type or not element:
        raise LogicValidationError("武器種と属性は必須項目です。")
    
    master = get_master_data()
    if weapon_type not in master.get("weapon_types", []):
        raise LogicValidationError(f"無効な武器種です: {weapon_type}")
    if element not in master.get("elements", []):
        raise LogicValidationError(f"無効な属性です: {element}")
        
    is_v, msg = validate_restoration_bonuses(restoration_bonuses)
    if not is_v:
        raise LogicValidationError(msg)

    df = load_equipment(user_id); prev_df = df.copy()
    new_id = str(uuid.uuid4())
    new_row = {
        "id": new_id, "weapon_type": weapon_type, "element": element,
        "weapon_name": weapon_name or f"無銘の{weapon_type}", "enhancement_type": enhancement_type,
        "current_series_skill": current_series_skill, "current_group_skill": current_group_skill,
        "is_locked": False
    }
    for i, pb in enumerate(p_bonuses):
        if i < 3: new_row[f"p_bonus_{i+1}"] = pb
    for i, bonus in enumerate(restoration_bonuses):
        if i < 5:
            new_row[f"rest_{i+1}_type"] = bonus.get("type", "なし")
            new_row[f"rest_{i+1}_level"] = bonus.get("level", "なし")
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    if save_equipment(df):
        load_equipment.clear()
        push_action("ADD_EQUIPMENT", EQUIPMENT_TABLE, prev_df, df)
        return new_id
    return None

def delete_equipment(equipment_id: str, user_id: str = "local") -> bool:
    """Deletes equipment and records history. Cascades to associated trackers."""
    df = load_equipment(user_id)
    idx = df[df["id"].astype(str) == str(equipment_id)].index
    if not idx.empty:
        prev_df = df.copy(); df = df.drop(idx)
        if save_equipment(df):
            # 1. Cascade Delete: Remove trackers referencing this weapon
            from src.logic.restoration_tracker import load_trackers, save_trackers, TRACKER_TABLE
            t_df = load_trackers(user_id)
            if not t_df.empty:
                t_idx = t_df[t_df["weapon_id"].astype(str) == str(equipment_id)].index
                if not t_idx.empty:
                    t_df = t_df.drop(t_idx)
                    if save_trackers(t_df):
                        load_trackers.clear()
            
            load_equipment.clear()
            push_action("DELETE_EQUIPMENT", EQUIPMENT_TABLE, prev_df, df)
            return True
    return False

def update_equipment_skills(equipment_id: str, series_skill: str, group_skill: str, user_id: str = "local") -> bool:
    df = load_equipment(user_id)
    idx = df[df["id"].astype(str) == str(equipment_id)].index
    if not idx.empty:
        prev_df = df.copy()
        df.at[idx[0], 'current_series_skill'] = series_skill
        df.at[idx[0], 'current_group_skill'] = group_skill
        if save_equipment(df):
            load_equipment.clear()
            push_action("UPDATE_SKILLS", EQUIPMENT_TABLE, prev_df, df)
            return True
    return False

def update_equipment(record_id: str, weapon_name: str, weapon_type: str, element: str, 
                     series_skill: str, group_skill: str, enhancement_type: str,
                     p_bonuses: list, r_bonuses: list, user_id: str = "local") -> bool:
    """Updates all fields of an existing equipment record and records history."""
    # 0. Validation
    if not weapon_type or not element:
        raise LogicValidationError("武器種と属性は必須項目です。")
    
    master = get_master_data()
    if weapon_type not in master.get("weapon_types", []):
        raise LogicValidationError(f"無効な武器種です: {weapon_type}")
    if element not in master.get("elements", []):
        raise LogicValidationError(f"無効な属性です: {element}")
        
    is_v, msg = validate_restoration_bonuses(r_bonuses)
    if not is_v:
        raise LogicValidationError(msg)

    df = load_equipment(user_id)
    idx = df[df["id"].astype(str) == str(record_id)].index
    if idx.empty: return False
    
    prev_df = df.copy()
    df.at[idx[0], "weapon_name"] = weapon_name
    df.at[idx[0], "weapon_type"] = weapon_type
    df.at[idx[0], "element"] = element
    df.at[idx[0], "current_series_skill"] = series_skill
    df.at[idx[0], "current_group_skill"] = group_skill
    df.at[idx[0], "enhancement_type"] = enhancement_type
    
    # Update p_bonuses
    for i, pb in enumerate(p_bonuses):
        if i < 3: df.at[idx[0], f"p_bonus_{i+1}"] = pb
    
    # Update r_bonuses
    for i, rb in enumerate(r_bonuses):
        if i < 5:
            df.at[idx[0], f"rest_{i+1}_type"] = rb.get("type", "なし")
            df.at[idx[0], f"rest_{i+1}_level"] = rb.get("level", "なし")
    
    if save_equipment(df):
        load_equipment.clear()
        push_action("UPDATE_EQUIPMENT", EQUIPMENT_TABLE, prev_df, df)
        return True
    return False

def toggle_lock(equipment_id: str, user_id: str = "local") -> bool:
    """Toggles the lock status of a weapon."""
    df = load_equipment(user_id)
    idx = df[df["id"].astype(str) == str(equipment_id)].index
    if not idx.empty:
        curr = df.at[idx[0], "is_locked"]
        if pd.isna(curr): curr = False
        df.at[idx[0], "is_locked"] = not bool(curr)
        if save_equipment(df):
            load_equipment.clear()
            return True
    return False

def filter_equipment(df: pd.DataFrame, search_name: str = "", weapon_types: list = None, elements: list = None, 
                     enhancements: list = None, series_skills: list = None, group_skills: list = None,
                     production_bonuses: list = None, restoration_bonuses: list = None, 
                     sort_by: str = "新着順", **kwargs) -> pd.DataFrame:
    if df.empty: return df
    f_df = df.copy()
    if search_name: f_df = f_df[f_df['weapon_name'].str.contains(search_name, case=False, na=False)]
    if weapon_types: f_df = f_df[f_df['weapon_type'].isin(weapon_types)]
    if elements: f_df = f_df[f_df['element'].isin(elements)]
    if enhancements: f_df = f_df[f_df['enhancement_type'].isin(enhancements)]
    if series_skills: f_df = f_df[f_df['current_series_skill'].isin(series_skills)]
    if group_skills: f_df = f_df[f_df['current_group_skill'].isin(group_skills)]

    if production_bonuses:
        # Check if all selected production bonuses exist in the weapon's 3 slots (AND logic)
        target_pb_set = set(production_bonuses)
        def check_pb(row):
            w_pbs = set([row[f'p_bonus_{i}'] for i in range(1, 4) if row[f'p_bonus_{i}'] != "なし"])
            return target_pb_set.issubset(w_pbs)
        f_df = f_df[f_df.apply(check_pb, axis=1)]

    if restoration_bonuses:
        # Parse filter strings back into (Type, Level) tuples for robust matching
        # Format: "Type [Level]" or just "Type"
        target_tuples = []
        for s in restoration_bonuses:
            if " [" in s:
                parts = s.split(" [")
                target_tuples.append((parts[0], parts[1][:-1]))
            else:
                target_tuples.append((s, "無印"))
        target_set = set(target_tuples)

        # Check if all selected bonuses exist in the weapon's 5 slots (AND logic)
        def check_all_bonuses(row):
            weapon_bonuses = set()
            for i in range(1, 6):
                rt, rl = row[f'rest_{i}_type'], row[f'rest_{i}_level']
                if rt != "なし":
                    weapon_bonuses.add((rt, rl))
            return target_set.issubset(weapon_bonuses)
        
        f_df = f_df[f_df.apply(check_all_bonuses, axis=1)]
    
    master = get_master_data()
    w_order = master.get("weapon_types", []); e_order = master.get("elements", [])
    f_df['weapon_type'] = pd.Categorical(f_df['weapon_type'], categories=w_order, ordered=True)
    f_df['element'] = pd.Categorical(f_df['element'], categories=e_order, ordered=True)
    
    if sort_by == "武器種順": f_df = f_df.sort_values(by=["weapon_type", "element", "weapon_name"])
    elif sort_by == "属性順": f_df = f_df.sort_values(by=["element", "weapon_type", "weapon_name"])
    else: f_df = f_df.sort_index(ascending=False)
    return f_df
