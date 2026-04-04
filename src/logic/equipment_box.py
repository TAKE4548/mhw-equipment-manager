import pandas as pd
import uuid
import streamlit as st
from collections import Counter
from src.database.gsheets_manager import load_data, save_data

EQUIPMENT_WORKSHEET = "EquipmentBox"
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

# --- Normalization & Labeling Helpers ---

ABBR_MAP = {
    "基礎攻撃力増強": "攻撃",
    "基礎攻撃力強化": "攻撃",
    "会心率増強": "会心",
    "会心率強化": "会心",
    "属性強化": "属性",
    "切れ味強化": "切れ味",
    "装填強化": "装填"
}

def get_abbr(full_name):
    return ABBR_MAP.get(full_name, full_name)

NORM_TYPE_MAP = {
    # Production
    "基礎攻撃": "基礎攻撃力増強",
    "会心": "会心率増強",
    # Restoration
    "属性": "属性強化",
    "切れ味(近接)": "切れ味強化",
    "装填数(遠隔)": "装填強化"
}
# Special case for restoration types that shared the same old name as production
REST_TYPE_MAP = {
    "基礎攻撃": "基礎攻撃力強化",
    "会心": "会心率強化"
}

NORM_LV_MAP = {
    "1": "Ⅰ", "2": "Ⅱ", "3": "Ⅲ",
    "無印": "無印", "EX": "EX", "なし": "なし"
}

def normalize_bonus(b_type, b_level=None, is_restoration=False):
    """Maps old terminology to new labels."""
    nt = b_type
    if is_restoration and b_type in REST_TYPE_MAP:
        nt = REST_TYPE_MAP[b_type]
    else:
        nt = NORM_TYPE_MAP.get(b_type, b_type)
        
    nl = b_level
    if b_level:
        nl = NORM_LV_MAP.get(str(b_level), b_level)
    
    return nt, nl

def get_abbr_item(item: str) -> str:
    """Helper to apply abbreviation to a single item name + level string."""
    if not item or item == "なし":
        return "なし"
    
    # First, handle the level part if it's a numeric suffix like '1', '2', '3'
    # By mapping it to Roman numerals
    res = item
    for old, new in NORM_LV_MAP.items():
        if item.endswith(old) and old.isdigit():
            res = item[:-len(old)] + new
            break

    for full, short in ABBR_MAP.items():
        if res.startswith(full):
            return f"{short}{res[len(full):]}"
    return res

def format_bonus_summary(items: list[str]) -> str:
    """Converts a list of bonus strings using aggregation (e.g., '攻撃Ⅰx2')."""
    items = [i for i in items if i and i != "なし"]
    if not items:
        return "なし"
    
    abbr_items = [get_abbr_item(i) for i in items]
    counts = Counter(abbr_items)
    parts = []
    # Sort for consistent comparison
    for item in sorted(counts.keys()):
        parts.append(f"{item}x{counts[item]}")
    return "、".join(parts)

def format_bonus_list(items: list[str], separator=" | ") -> str:
    """Converts a list of bonus strings to a flat list (e.g., '攻撃 | 攻撃 | なし')."""
    if not items:
        return "なし"
    abbr_items = [get_abbr_item(i) for i in items]
    return separator.join(abbr_items)

# --- UI & Styling Helpers ---

ATTRIBUTE_COLORS = {
    "火": "#e74c3c", "水": "#3498db", "雷": "#f1c40f", "氷": "#ecf0f1", "龍": "#8e44ad",
    "毒": "#9b59b6", "麻痺": "#f39c12", "睡眠": "#95a5a6", "爆破": "#d35400", "無": "#7f8c8d"
}

def get_weapon_label(row) -> str:
    """Generates a compact summary label for use in selectboxes."""
    w_type = row.get("weapon_type", "なし")
    element = row.get("element", "なし")
    enhancement = row.get("enhancement_type", "なし")
    name = row.get("weapon_name", "")
    
    label = f"{w_type} | {element}"
    if enhancement != "なし":
        label += f" | {enhancement}"
    if name and not name.startswith("無銘の"):
        label = f"【{name}】 {label}"
    return label

# --- Core Logic ---

def validate_restoration_bonuses(bonuses: list[dict]) -> tuple[bool, str]:
    """
    Validates duplicates. Unenhanced (Ⅰ or 無印) can be up to 5. Enhanced max 2.
    """
    type_level_counts = {}
    for b in bonuses:
        b_type = b.get("type", "なし")
        # Normalize incoming validation data if it's old (though usually UI sends new)
        b_type, b_level = normalize_bonus(b_type, b.get("level", "なし"), is_restoration=True)
        
        if b_type != "なし":
            tl_key = f"{b_type} [{b_level}]"
            type_level_counts[tl_key] = type_level_counts.get(tl_key, 0) + 1
            
            if b_level in ["Ⅰ", "1", "無印"]: # Allow 1 for compat
                continue
                
            if type_level_counts[tl_key] > 2:
                return False, f"強化済みのボーナス「{tl_key}」が3枠以上重複することはあり得ません（最大2枠まで）。"
    return True, ""

def load_equipment() -> pd.DataFrame:
    df = load_data(worksheet=EQUIPMENT_WORKSHEET, required_columns=EQUIPMENT_COLUMNS)
    # Apply normalization to the dataframe for consistency in UI
    if not df.empty:
        for idx, row in df.iterrows():
            # Normalize Production
            for i in range(1, 4):
                col = f"p_bonus_{i}"
                t, _ = normalize_bonus(row[col])
                df.at[idx, col] = t
            # Normalize Restoration
            for i in range(1, 6):
                tc, lc = f"rest_{i}_type", f"rest_{i}_level"
                nt, nl = normalize_bonus(row[tc], row[lc], is_restoration=True)
                df.at[idx, tc] = nt
                df.at[idx, lc] = nl
    return df

def save_equipment(df: pd.DataFrame) -> bool:
    return save_data(df, worksheet=EQUIPMENT_WORKSHEET)

def register_equipment(weapon_name: str, weapon_type: str, element: str, 
                       current_series: str, current_group: str,
                       enhancement_type: str,
                       p_bonuses: list[str], rest_bonuses: list[dict]) -> str:
    df = load_equipment()
    
    new_id = str(uuid.uuid4())
    new_row = {
        "id": new_id,
        "weapon_name": weapon_name,
        "weapon_type": weapon_type,
        "element": element,
        "current_series_skill": current_series,
        "current_group_skill": current_group,
        "enhancement_type": enhancement_type,
        "p_bonus_1": p_bonuses[0] if len(p_bonuses) > 0 else "なし",
        "p_bonus_2": p_bonuses[1] if len(p_bonuses) > 1 else "なし",
        "p_bonus_3": p_bonuses[2] if len(p_bonuses) > 2 else "なし",
    }
    
    for i in range(5):
        rt = f"rest_{i+1}_type"
        rl = f"rest_{i+1}_level"
        if i < len(rest_bonuses):
            new_row[rt] = rest_bonuses[i].get("type", "なし")
            new_row[rl] = rest_bonuses[i].get("level", "なし")
        else:
            new_row[rt] = "なし"
            new_row[rl] = "なし"
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    if save_equipment(df):
        return new_id
    return None

def update_equipment_skills(eq_id: str, new_series: str, new_group: str) -> bool:
    df = load_equipment()
    if df.empty:
        return False
    
    idx = df.index[df['id'] == eq_id].tolist()
    if not idx:
        return False
    
    df.at[idx[0], 'current_series_skill'] = new_series
    df.at[idx[0], 'current_group_skill'] = new_group
    
    return save_equipment(df)

def delete_equipment(eq_id: str) -> bool:
    df = load_equipment()
    if df.empty:
        return False
    
    df = df[df['id'] != eq_id]
    return save_equipment(df)
