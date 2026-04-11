import pandas as pd
from typing import List, Dict, Tuple, Optional

def get_talisman_skills(row: pd.Series) -> Dict[str, int]:
    """Extracts non-empty skills and their levels from a talisman row."""
    skills = {}
    for i in range(1, 4):
        name = row.get(f"skill_{i}_name", "")
        level = row.get(f"skill_{i}_level", 0)
        if name and str(name).strip() and int(level) > 0:
            skills[str(name).strip()] = int(level)
    return skills

def get_talisman_slots(row: pd.Series) -> List[int]:
    """Extracts all slots (weapon + 3 armor) and returns them sorted descending."""
    slots = [
        int(row.get("weapon_slot_level", 0)),
        int(row.get("armor_slot_1_level", 0)),
        int(row.get("armor_slot_2_level", 0)),
        int(row.get("armor_slot_3_level", 0))
    ]
    return sorted(slots, reverse=True)

def compare_talismans(t1: pd.Series, t2: pd.Series) -> str:
    """
    Compares two talismans and returns the relationship of t1 relative to t2.
    Returns: 'EQUIVALENT', 'SUPERIOR', 'INFERIOR', or 'INCOMPARABLE'.
    
    Rules for Superior (t1 > t2):
    1. Skill Coverage: Skills(t2) subset of Skills(t1) AND for all common skills, Lvl(t1) >= Lvl(t2).
    2. Slot Coverage: SortedSlots(t1)[i] >= SortedSlots(t2)[i] for all i.
    3. Strict Improvement: At least one skill level is higher OR has extra skills OR a slot is higher.
    """
    s1 = get_talisman_skills(t1)
    s2 = get_talisman_skills(t2)
    sl1 = get_talisman_slots(t1)
    sl2 = get_talisman_slots(t2)

    # 1. Skill check
    # t1 is at least as good as t2 in skills if:
    # - t1 has ALL skills that t2 has
    # - t1's levels are >= t2's levels
    t1_skill_no_worse = True
    for name, lvl in s2.items():
        if name not in s1 or s1[name] < lvl:
            t1_skill_no_worse = False
            break
            
    # t2 is at least as good as t1 in skills
    t2_skill_no_worse = True
    for name, lvl in s1.items():
        if name not in s2 or s2[name] < lvl:
            t2_skill_no_worse = False
            break

    # 2. Slot check
    t1_slot_no_worse = all(sl1[i] >= sl2[i] for i in range(4))
    t2_slot_no_worse = all(sl2[i] >= sl1[i] for i in range(4))

    # 3. Determine relationship
    if t1_skill_no_worse and t1_slot_no_worse and t2_skill_no_worse and t2_slot_no_worse:
        return 'EQUIVALENT'
    
    if t1_skill_no_worse and t1_slot_no_worse:
        return 'SUPERIOR'
        
    if t2_skill_no_worse and t2_slot_no_worse:
        return 'INFERIOR'
        
    return 'INCOMPARABLE'

def find_redundant_talismans(df: pd.DataFrame) -> List[Dict]:
    """
    Identifies talismans that have a better or equivalent counterpart in the collection.
    Returns a list of dictionaries with redundant talisman info.
    """
    if df.empty:
        return []

    redundant = []
    # Identify non-deleted (real) IDs
    talismans = df.to_dict('records')
    
    for i, t_curr in enumerate(talismans):
        curr_series = pd.Series(t_curr)
        superiors = []
        equivalents = []
        
        for j, t_other in enumerate(talismans):
            if i == j:
                continue
            
            other_series = pd.Series(t_other)
            rel = compare_talismans(other_series, curr_series)
            
            if rel == 'SUPERIOR':
                superiors.append(t_other['id'])
            elif rel == 'EQUIVALENT':
                # For equivalent ones, we mark the one with "later" index as redundant to avoid deleting both.
                if j < i:
                    equivalents.append(t_other['id'])
        
        if superiors or equivalents:
            redundant.append({
                "talisman": t_curr,
                "reason": "SUPERIOR" if superiors else "EQUIVALENT",
                "superior_ids": superiors,
                "equivalent_ids": equivalents
            })
            
    return redundant
