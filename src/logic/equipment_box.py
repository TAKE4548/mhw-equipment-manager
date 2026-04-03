import pandas as pd
import uuid
import streamlit as st
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

def validate_restoration_bonuses(bonuses: list[dict]) -> tuple[bool, str]:
    """
    Validates that exact Type+Level combination does not exceed 2, EXCEPT for unenhanced levels (1 or 無印)
    which can take up to 5 slots.
    """
    type_level_counts = {}
    for b in bonuses:
        b_type = b.get("type", "なし")
        b_level = str(b.get("level", "なし"))
        
        if b_type != "なし":
            tl_key = f"{b_type} [{b_level}]"
            type_level_counts[tl_key] = type_level_counts.get(tl_key, 0) + 1
            
            # 初期レベル（レベル1 または 無印）は3枠以上の重複が存在し得るためスルー
            if b_level in ["1", "無印"]:
                continue
                
            if type_level_counts[tl_key] > 2:
                return False, f"強化済みのボーナス「{tl_key}」が3枠以上重複することはシステム上あり得ません（最大2枠まで）。"
    return True, ""

def load_equipment() -> pd.DataFrame:
    df = load_data(worksheet=EQUIPMENT_WORKSHEET, required_columns=EQUIPMENT_COLUMNS)
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
