import pandas as pd
import uuid
import streamlit as st
from collections import Counter
from src.database.storage_manager import load_data, save_data, delete_record
from src.logic.history import push_action
from src.logic.master import get_master_data

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
    "rest_5_type", "rest_5_level"
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

def load_equipment() -> pd.DataFrame:
    """Loads equipment and applies auto-normalization."""
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
    return df

def save_equipment(df: pd.DataFrame) -> bool:
    return save_data(EQUIPMENT_TABLE, df)

def add_equipment(weapon_name: str, weapon_type: str, element: str, 
                  current_series_skill: str, current_group_skill: str, enhancement_type: str,
                  p_bonuses: list, restoration_bonuses: list):
    """Adds a new equipment and records history."""
    df = load_equipment(); prev_df = df.copy()
    new_id = str(uuid.uuid4())
    new_row = {
        "id": new_id, "weapon_type": weapon_type, "element": element,
        "weapon_name": weapon_name or f"無銘の{weapon_type}", "enhancement_type": enhancement_type,
        "current_series_skill": current_series_skill, "current_group_skill": current_group_skill
    }
    for i, pb in enumerate(p_bonuses):
        if i < 3: new_row[f"p_bonus_{i+1}"] = pb
    for i, bonus in enumerate(restoration_bonuses):
        if i < 5:
            new_row[f"rest_{i+1}_type"] = bonus.get("type", "なし")
            new_row[f"rest_{i+1}_level"] = bonus.get("level", "なし")
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    if save_equipment(df):
        push_action("ADD_EQUIPMENT", EQUIPMENT_TABLE, prev_df, df)
        return new_id
    return None

def delete_equipment(equipment_id: str) -> bool:
    """Deletes equipment and records history."""
    df = load_equipment()
    idx = df[df["id"].astype(str) == str(equipment_id)].index
    if not idx.empty:
        prev_df = df.copy(); df = df.drop(idx)
        if save_equipment(df):
            push_action("DELETE_EQUIPMENT", EQUIPMENT_TABLE, prev_df, df)
            return True
    return False

def update_equipment_skills(equipment_id: str, series_skill: str, group_skill: str) -> bool:
    df = load_equipment()
    idx = df[df["id"].astype(str) == str(equipment_id)].index
    if not idx.empty:
        prev_df = df.copy()
        df.at[idx[0], 'current_series_skill'] = series_skill
        df.at[idx[0], 'current_group_skill'] = group_skill
        if save_equipment(df):
            push_action("UPDATE_SKILLS", EQUIPMENT_TABLE, prev_df, df)
            return True
    return False

def update_equipment(record_id: str, weapon_name: str, weapon_type: str, element: str, 
                     series_skill: str, group_skill: str, enhancement_type: str,
                     p_bonuses: list, r_bonuses: list) -> bool:
    """Updates all fields of an existing equipment record and records history."""
    df = load_equipment()
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
        push_action("UPDATE_EQUIPMENT", EQUIPMENT_TABLE, prev_df, df)
        return True
    return False

def filter_equipment(df: pd.DataFrame, search_name: str = "", weapon_types: list = None, elements: list = None, sort_by: str = "新着順", **kwargs) -> pd.DataFrame:
    if df.empty: return df
    f_df = df.copy()
    if search_name: f_df = f_df[f_df['weapon_name'].str.contains(search_name, case=False, na=False)]
    if weapon_types: f_df = f_df[f_df['weapon_type'].isin(weapon_types)]
    if elements: f_df = f_df[f_df['element'].isin(elements)]
    
    master = get_master_data()
    w_order = master.get("weapon_types", []); e_order = master.get("elements", [])
    f_df['weapon_type'] = pd.Categorical(f_df['weapon_type'], categories=w_order, ordered=True)
    f_df['element'] = pd.Categorical(f_df['element'], categories=e_order, ordered=True)
    
    if sort_by == "武器種順": f_df = f_df.sort_values(by=["weapon_type", "element", "weapon_name"])
    elif sort_by == "属性順": f_df = f_df.sort_values(by=["element", "weapon_type", "weapon_name"])
    else: f_df = f_df.sort_index(ascending=False)
    return f_df
