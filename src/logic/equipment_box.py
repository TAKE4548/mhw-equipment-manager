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
# We'll detect if it's a restoration field by its column name or context.
REST_TYPE_MAP = {
    "基礎攻撃": "基礎攻撃力強化",
    "会心": "会心率強化"
}

NORM_LV_MAP = {
    "1": "Ⅰ",
    "2": "Ⅱ",
    "3": "Ⅲ",
    "無印": "無印",
    "EX": "EX",
    "なし": "なし"
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

def format_bonus_summary(items: list[str]) -> str:
    """Converts a list of bonus strings like ['攻撃Ⅰ', '攻撃Ⅰ'] to '攻撃Ⅰx2'."""
    items = [i for i in items if i and i != "なし"]
    if not items:
        return "なし"
    counts = Counter(items)
    # Maintain some order? Sort by standard priority if needed, but alphabetical is fine
    parts = []
    for item in sorted(counts.keys()):
        parts.append(f"{item}x{counts[item]}")
    return "、".join(parts)

def get_weapon_label(row) -> str:
    """Generates a detailed summary label for the weapon."""
    w_type = row.get("weapon_type", "")
    element = row.get("element", "")
    enhancement = row.get("enhancement_type", "なし")
    if enhancement == "なし": enhancement = ""
    
    # Process Production Bonuses
    pbs = []
    for i in range(1, 4):
        val = row.get(f"p_bonus_{i}", "なし")
        if val != "なし":
            norm_t, _ = normalize_bonus(val)
            pbs.append(norm_t)
    pb_str = format_bonus_summary(pbs)
    
    # Process Restoration Bonuses
    rbs = []
    for i in range(1, 6):
        rt = row.get(f"rest_{i}_type", "なし")
        rl = row.get(f"rest_{i}_level", "なし")
        if rt != "なし":
            nt, nl = normalize_bonus(rt, rl, is_restoration=True)
            # Level "無印" is not displayed as suffix
            suffix = nl if nl and nl != "無印" else ""
            rbs.append(f"{nt}{suffix}")
    rb_str = format_bonus_summary(rbs)
    
    series = row.get("current_series_skill", "なし")
    group = row.get("current_group_skill", "なし")
    
    # Combine
    parts = [w_type, element, enhancement, pb_str, rb_str, series, group]
    return " ".join([p for p in parts if p and p != "なし"])

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
