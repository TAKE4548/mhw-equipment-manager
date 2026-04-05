import pandas as pd
import uuid
import json
import os
import streamlit as st
from src.database.storage_manager import load_data, save_data
from src.logic.history import push_action

TALISMANS_TABLE = "talismans"
TALISMANS_COLUMNS = [
    "id", "rarity",
    "skill_1_name", "skill_1_level",
    "skill_2_name", "skill_2_level",
    "skill_3_name", "skill_3_level",
    "weapon_slot_level",
    "armor_slot_1_level", "armor_slot_2_level", "armor_slot_3_level",
    "is_favorite"
]

@st.cache_data
def load_talisman_master() -> dict:
    # Use absolute path resolution for robustness across different execution contexts
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(current_dir, "..", "data", "talisman_master.json"))
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # In a real app, we might log this. In Streamlit, st.error could be used but we're in logic.
        print(f"Error loading talisman master data: {e}")
        return {"groups": {}, "rarity_patterns": {}}

@st.cache_data
def load_talismans(user_id: str = "local") -> pd.DataFrame:
    """
    Loads all talismans from storage.
    Cached per user_id to ensure multi-user isolation.
    """

    df = load_data(TALISMANS_TABLE, required_columns=TALISMANS_COLUMNS)
    # Ensure types
    for i in range(1, 4):
        c = f"skill_{i}_level"
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
    for c in ["weapon_slot_level", "armor_slot_1_level", "armor_slot_2_level", "armor_slot_3_level"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
    if "is_favorite" in df.columns:
        df["is_favorite"] = df["is_favorite"].fillna(False).astype(bool)
    return df

def save_talismans(df: pd.DataFrame) -> bool:
    return save_data(TALISMANS_TABLE, df)

def parse_master_slot(s: str) -> list[int]:
    """Parses a pattern like '[1]①①' or '①ーー' into [W, A1, A2, A3]."""
    w = 0
    a = [0, 0, 0]
    s_iter = s
    if s_iter.startswith("["):
        idx = s_iter.find("]")
        if idx != -1:
            w = int(s_iter[1:idx])
            s_iter = s_iter[idx+1:]
    
    char_map = {"ー": 0, "①": 1, "②": 2, "③": 3, "④": 4}
    # Parse up to 3 remaining armor slot characters
    for i in range(min(3, len(s_iter))):
        a[i] = char_map.get(s_iter[i], 0)
    return [w, a[0], a[1], a[2]]

def get_skill_groups(skill_name: str, skill_level: int = None) -> list[str]:
    master = load_talisman_master()
    groups = master.get("groups", {})
    found = []
    for g_n, g_skills in groups.items():
        if skill_name in g_skills:
            if skill_level is None or int(g_skills[skill_name]) == skill_level:
                found.append(g_n)
    return found

def get_valid_skill_names(rarity: int, prev_skills: list[tuple[str, int]]) -> list[str]:
    """Returns unique skill names that can appear in the next slot."""
    master = load_talisman_master()
    r_str = str(rarity)
    patterns = master.get("rarity_patterns", {}).get(r_str, [])
    
    # 1. Determine current group paths based on fixed (name, level) choices
    current_paths = [[]]
    for p_sk_name, p_sk_lvl in prev_skills:
        next_paths = []
        for path in current_paths:
            for g in get_skill_groups(p_sk_name, p_sk_lvl):
                next_paths.append(path + [g])
        current_paths = next_paths
        
    # 2. Find valid next groups from patterns
    valid_next_groups = set()
    for pat in patterns:
        for sp in pat.get("skill_patterns", []):
            for current_path in current_paths:
                if current_path == sp[:len(current_path)]:
                    if len(current_path) < len(sp):
                        valid_next_groups.add(sp[len(current_path)])
                        
    # 3. Collect unique skill names from those groups
    names = set()
    groups_dict = master.get("groups", {})
    for g_n in valid_next_groups:
        for s_n in groups_dict.get(g_n, {}).keys():
            names.add(s_n)
    return sorted(list(names))

def get_valid_levels_for_skill(rarity: int, prev_skills: list[tuple[str, int]], target_skill: str) -> list[int]:
    """Returns available levels for the target_skill in the next slot."""
    master = load_talisman_master()
    r_str = str(rarity)
    patterns = master.get("rarity_patterns", {}).get(r_str, [])
    
    current_paths = [[]]
    for p_sk_name, p_sk_lvl in prev_skills:
        next_paths = []
        for path in current_paths:
            for g in get_skill_groups(p_sk_name, p_sk_lvl):
                next_paths.append(path + [g])
        current_paths = next_paths
        
    valid_next_groups = set()
    for pat in patterns:
        for sp in pat.get("skill_patterns", []):
            for current_path in current_paths:
                if current_path == sp[:len(current_path)]:
                    if len(current_path) < len(sp):
                        valid_next_groups.add(sp[len(current_path)])
    
    levels = set()
    groups_dict = master.get("groups", {})
    for g_n in valid_next_groups:
        g_s = groups_dict.get(g_n, {})
        if target_skill in g_s:
            levels.add(int(g_s[target_skill]))
    return sorted(list(levels))

def get_valid_slot_levels(rarity: int, skills: list[tuple[str, int]], current_slots: list[int]) -> list[int]:
    """Returns available levels for the next slot position (0 to 2 for index in [W, A1, A2, A3])."""
    master = load_talisman_master()
    r_str = str(rarity)
    patterns = master.get("rarity_patterns", {}).get(r_str, [])
    
    # Identify valid group paths for selected skills
    current_paths = [[]]
    for p_sk_name, p_sk_lvl in skills:
        next_paths = []
        for path in current_paths:
            for g in get_skill_groups(p_sk_name, p_sk_lvl):
                next_paths.append(path + [g])
        current_paths = next_paths
        
    # Find all possible slot configurations for these skill patterns
    valid_slot_patterns = []
    for pat in patterns:
        matched = False
        if not skills:
            matched = True
        else:
            for sp in pat.get("skill_patterns", []):
                for cp in current_paths:
                    if cp == sp[:len(cp)]:
                        matched = True; break
                if matched: break
        
        if matched:
            for s_str in pat.get("slots", []):
                valid_slot_patterns.append(parse_master_slot(s_str))
                
    # Filter based on current slot selection
    # current_slots is a list of levels for Slot1, Slot2... we need to calculate for the next index.
    next_idx = len(current_slots) # 0, 1, or 2 (maps to 3 dropdowns)
    
    # Mapping for Rarity 8: [W, A1, A2]
    # Mapping for others: [A1, A2, A3]
    # Note: parse_master_slot returns [W, A1, A2, A3]
    
    allowed = set()
    for p in valid_slot_patterns:
        # Check prefix match
        # If Rarity 8: p[0] is W, p[1] is A1, p[2] is A2. p[3] is always 0.
        # If Others: p[0] is always 0, p[1] is A1, p[2] is A2, p[3] is A3.
        
        p_mapped = []
        if int(rarity) == 8:
            p_mapped = [p[0], p[1], p[2]]
        else:
            p_mapped = [p[1], p[2], p[3]]
            
        if p_mapped[:len(current_slots)] == current_slots:
            allowed.add(p_mapped[next_idx])
            
    return sorted(list(allowed))

def get_all_valid_slot_patterns(rarity: int, skills: list[tuple[str, int]]) -> list[list[int]]:
    """Returns all 3-slot combinations allowed for current context."""
    master = load_talisman_master()
    r_str = str(rarity)
    patterns = master.get("rarity_patterns", {}).get(r_str, [])
    
    current_paths = [[]]
    for p_sk_name, p_sk_lvl in skills:
        next_paths = []
        for path in current_paths:
            for g in get_skill_groups(p_sk_name, p_sk_lvl):
                next_paths.append(path + [g])
        current_paths = next_paths
        
    results = []
    for pat in patterns:
        matched = False
        if not skills: matched = True
        else:
            for sp in pat.get("skill_patterns", []):
                for cp in current_paths:
                    if cp == sp[:len(cp)]:
                        matched = True; break
                if matched: break
        if matched:
            for s_str in pat.get("slots", []):
                p = parse_master_slot(s_str)
                if int(rarity) == 8:
                    results.append([p[0], p[1], p[2]])
                else:
                    results.append([p[1], p[2], p[3]])
    return results

def validate_talisman(rarity: int, skills: list, slots: list) -> tuple[bool, str]:
    """
    skills: [{"name": "砲術", "level": 2}, ...]
    slots: [weapon_slot, armor_1, armor_2, armor_3]
    """
    master = load_talisman_master()
    rarity_str = str(rarity)
    
    if rarity_str not in master.get("rarity_patterns", {}):
        return False, f"Invalid rarity: {rarity}"
        
    patterns = master["rarity_patterns"][rarity_str]
    groups = master.get("groups", {})
    
    # 1. Map provided skills to their respective Groups and validate Level
    provided_groups = []
    for skill in skills:
        s_name = skill.get("name")
        s_lvl = int(skill.get("level", 0))
        if not s_name:
            continue
            
        found_group = None
        for g_name, g_skills in groups.items():
            if s_name in g_skills and int(g_skills[s_name]) == s_lvl:
                found_group = g_name
                break
                
        if not found_group:
            # Generate a helpful error message if it exists but level is wrong
            valid_levels = []
            for g_name, g_skills in groups.items():
                if s_name in g_skills:
                    valid_levels.append(str(g_skills[s_name]))
            if valid_levels:
                return False, f"スキル「{s_name}」のレベル({s_lvl})が不正です。有効なレベル: {', '.join(valid_levels)}"
            return False, f"スキル「{s_name}」はマスタ定義に存在しません。"
        provided_groups.append(found_group)
    
    if not provided_groups:
        return False, "最低1つのスキルを指定してください。"

    # 2. Match Skill Pattern sequence
    valid_slots_for_matched_patterns = set()
    skill_sequence_matched = False
    
    for pat in patterns:
        spatterns = pat.get("skill_patterns", [])
        for sp in spatterns:
            # Check if provided sequence matches exactly, or is a valid partial prefix
            # Example: sp = ["A", "B", "C"], provided = ["A", "B"] is OK. provided = ["A", "B", "C"] is OK.
            if provided_groups == sp[:len(provided_groups)]:
                skill_sequence_matched = True
                valid_slots_for_matched_patterns.update(pat.get("slots", []))
                
    if not skill_sequence_matched:
        return False, f"スキルグループの組み合わせ {provided_groups} はレア度 {rarity} に存在しません。"

    # 3. Explicit architectural rule checks
    provided_parsed = [int(slots[0]), int(slots[1]), int(slots[2]), int(slots[3])]
    if int(rarity) != 8 and provided_parsed[0] > 0:
        return False, f"武器スロットはレア度8でのみ設定可能です。"
        
    # 4. Match Slots against master
    slot_match = False
    for vs in valid_slots_for_matched_patterns:
        if parse_master_slot(vs) == provided_parsed:
            slot_match = True
            break
            
    if not slot_match:
        return False, f"スロット構成 {provided_parsed} は、指定したスキル構成で出現し得ないパターンです。"

    return True, ""


def add_talisman(rarity: int, skills: list, slots: list, user_id: str = "local") -> str:
    df = load_talismans(user_id)
    prev_df = df.copy()
    
    new_id = str(uuid.uuid4())
    new_row = {
        "id": new_id,
        "rarity": int(rarity),
        "weapon_slot_level": int(slots[0]),
        "armor_slot_1_level": int(slots[1]),
        "armor_slot_2_level": int(slots[2]),
        "armor_slot_3_level": int(slots[3]),
        "is_favorite": False
    }
    
    for i in range(3):
        if i < len(skills):
            new_row[f"skill_{i+1}_name"] = skills[i].get("name", "")
            new_row[f"skill_{i+1}_level"] = int(skills[i].get("level", 0))
        else:
            new_row[f"skill_{i+1}_name"] = ""
            new_row[f"skill_{i+1}_level"] = 0
            
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    if save_talismans(df):
        load_talismans.clear()
        push_action("ADD_TALISMAN", TALISMANS_TABLE, prev_df, df)
        return new_id
    return None

def delete_talisman(talisman_id: str, user_id: str = "local") -> bool:
    df = load_talismans(user_id)
    idx = df[df["id"].astype(str) == str(talisman_id)].index
    if not idx.empty:
        prev_df = df.copy()
        df = df.drop(idx)
        if save_talismans(df):
            load_talismans.clear()
            push_action("DELETE_TALISMAN", TALISMANS_TABLE, prev_df, df)
            return True
    return False

def update_talisman(talisman_id: str, rarity: int, skills: list, slots: list, user_id: str = "local") -> bool:
    """Updates an existing talisman and records history."""
    df = load_talismans(user_id)
    idx = df[df["id"].astype(str) == str(talisman_id)].index
    if idx.empty: return False
    
    prev_df = df.copy()
    df.at[idx[0], "rarity"] = rarity
    df.at[idx[0], "weapon_slot_level"] = int(slots[0])
    df.at[idx[0], "armor_slot_1_level"] = int(slots[1])
    df.at[idx[0], "armor_slot_2_level"] = int(slots[2])
    df.at[idx[0], "armor_slot_3_level"] = int(slots[3])
    
    for i in range(3):
        if i < len(skills):
            df.at[idx[0], f"skill_{i+1}_name"] = skills[i].get("name", "")
            df.at[idx[0], f"skill_{i+1}_level"] = int(skills[i].get("level", 0))
        else:
            df.at[idx[0], f"skill_{i+1}_name"] = ""
            df.at[idx[0], f"skill_{i+1}_level"] = 0
            
    if save_talismans(df):
        load_talismans.clear()
        push_action("UPDATE_TALISMAN", TALISMANS_TABLE, prev_df, df)
        return True
    return False

def toggle_favorite(talisman_id: str, user_id: str = "local") -> bool:
    df = load_talismans(user_id)
    idx = df[df["id"].astype(str) == str(talisman_id)].index
    if not idx.empty:
        curr = df.at[idx[0], "is_favorite"]
        if pd.isna(curr): curr = False
        df.at[idx[0], "is_favorite"] = not bool(curr)
        # We don't record undo history just for toggling favorite flag.
        if save_talismans(df):
            load_talismans.clear()
            return True
    return False

def get_all_skills_flat() -> list:
    """Returns a flat, sorted list of all skill names from master."""
    master = load_talisman_master()
    groups = master.get("groups", {})
    all_skills = set()
    for g_skills in groups.values():
        for s in g_skills.keys():
            all_skills.add(s)
    return sorted(list(all_skills))

def get_skill_level_from_master(skill_name: str) -> int:
    """Returns the mandatory fixed level for a skill from master."""
    master = load_talisman_master()
    groups = master.get("groups", {})
    for g_skills in groups.values():
        if skill_name in g_skills:
            return int(g_skills[skill_name])
    return 1
