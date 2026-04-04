import pandas as pd
import uuid
import streamlit as st
from collections import Counter
from src.database.storage_manager import load_data, save_data

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
    "火": "#e74c3c", # Darker red
    "水": "#3498db", # Blue
    "雷": "#f1c40f", # yellow
    "氷": "#ecf0f1", # almost white
    "龍": "#9b59b6", # purple
    "毒": "#8e44ad", # dark purple
    "麻痺": "#f39c12", # orange
    "睡眠": "#bdc3c7", # silver
    "爆破": "#e67e22", # orange-red
    "無": "#95a5a6" # grey
}

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
    "1.0": "Ⅰ", "2.0": "Ⅱ", "3.0": "Ⅲ",
    "無印": "無印", "EX": "EX", "なし": "なし"
}

def normalize_bonus(b_type, b_level=None, is_restoration=False):
    """Maps old terminology to new labels and ensures Roman numerals."""
    nt = b_type
    if is_restoration and b_type in REST_TYPE_MAP:
        nt = REST_TYPE_MAP[b_type]
    else:
        nt = NORM_TYPE_MAP.get(b_type, b_type)
    
    if b_level is None or b_level == "なし":
        return nt, "なし"
    
    nl_raw = str(b_level).strip()
    if nl_raw.endswith(".0"):
        nl_raw = nl_raw[:-2]
        
    nl = NORM_LV_MAP.get(nl_raw, nl_raw)
    return nt, nl

def get_abbr_item(item: str) -> str:
    """Helper to apply abbreviation to a single item name + level string."""
    if not item or item == "なし":
        return "なし"
    
    res = item.strip()
    if ".0" in res:
        res = res.replace(".0", "")
        
    for old, new in NORM_LV_MAP.items():
        if res.endswith(old) and not old.endswith(".0"):
            res = res[:-len(old)] + new
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
    counts = Counter(items)
    parts = []
    for item, count in counts.items():
        abbr = get_abbr_item(item)
        if count > 1:
            parts.append(f"{abbr}×{count}")
        else:
            parts.append(abbr)
    return " / ".join(parts)

def format_bonus_list(items: list[str]) -> str:
    """Simple joined list with abbreviations."""
    return " / ".join([get_abbr_item(i) for i in items if i and i != "なし"])

def get_weapon_label(weapon_id: str, df: pd.DataFrame) -> str:
    """Returns a readable label for a weapon from the equipment dataframe."""
    row = df[df['id'] == weapon_id]
    if row.empty:
        return "Unknown Weapon"
    row = row.iloc[0]
    name = row['weapon_name'] if row['weapon_name'] and not row['weapon_name'].startswith("無銘の") else row['weapon_type']
    return f"{name} ({row['element']})"

def validate_restoration_bonuses(bonuses: list[dict]):
    """Checks for illegal restoration bonus combinations (max 2 per type)."""
    types = [b['type'] for b in bonuses if b['type'] != "なし"]
    counts = Counter(types)
    for t, count in counts.items():
        if count > 2:
            tl_key = t
            for old, new in ABBR_MAP.items():
                if t.startswith(old):
                    tl_key = new
                    break
            return False, f"強化済みのボーナス「{tl_key}」が3枠以上重複することはあり得ません（最大2枠まで）。"
    return True, ""

def load_equipment():
    # Primary data load
    df = load_data(EQUIPMENT_TABLE, required_columns=EQUIPMENT_COLUMNS)
    
    # FORCED PERSISTENCE: If we are midway through a session, don't return None even if handshake is flickering
def load_equipment() -> pd.DataFrame:
    df = load_data(EQUIPMENT_TABLE, required_columns=EQUIPMENT_COLUMNS)
    if not df.empty:
        for idx, row in df.iterrows():
            for i in range(1, 4):
                col = f"p_bonus_{i}"
                t, _ = normalize_bonus(row[col])
                df.at[idx, col] = t
            for i in range(1, 6):
                tc, lc = f"rest_{i}_type", f"rest_{i}_level"
                nt, nl = normalize_bonus(row[tc], row[lc], is_restoration=True)
                df.at[idx, tc] = nt
                df.at[idx, lc] = nl
    return df

def save_equipment(df: pd.DataFrame) -> bool:
    return save_data(EQUIPMENT_TABLE, df)

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
        rt, rl = f"rest_{i+1}_type", f"rest_{i+1}_level"
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
    if df.empty: return False
    idx = df.index[df['id'] == eq_id].tolist()
    if not idx: return False
    df.at[idx[0], 'current_series_skill'] = new_series
    df.at[idx[0], 'current_group_skill'] = new_group
    return save_equipment(df)

def delete_equipment(eq_id: str) -> bool:
    df = load_equipment()
    if df.empty: return False
    df = df[df['id'] != eq_id]
    return save_equipment(df)
