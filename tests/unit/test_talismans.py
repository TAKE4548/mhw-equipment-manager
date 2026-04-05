import pytest
from unittest.mock import patch
import pandas as pd
from src.logic.talismans import (
    validate_talisman, add_talisman, delete_talisman, toggle_favorite,
    load_talismans, get_valid_skill_names, get_valid_levels_for_skill, get_valid_slot_levels
)

def test_validate_talisman_ok_ts_tl_001():
    # TS-TL-001: マスタデータに基づくスキルバリデーション (OK)
    # 砲術 Lv2 (Grp B) - 攻撃 Lv1 (Grp A) - 無我の境地 Lv3 (Grp G)
    # Slots: [1]①ー => [1, 1, 0, 0]
    
    skills = [
        {"name": "砲術", "level": 2},
        {"name": "攻撃", "level": 1},
        {"name": "無我の境地", "level": 3}
    ]
    slots = [1, 1, 0, 0]
    
    # Rarity 8 using B-A-G
    is_valid, msg = validate_talisman(8, skills, slots)
    assert is_valid is True, f"Expected valid, got invalid: {msg}"

def test_validate_talisman_ng_level_mismatch_ts_tl_002():
    # TS-TL-002: グループ規定外のレベル
    # 無我の境地 (E=Lv1, F=Lv2, G=Lv3). Try Lv4 which is totally invalid.
    skills = [
        {"name": "砲術", "level": 2},
        {"name": "攻撃", "level": 1},
        {"name": "無我の境地", "level": 4}
    ]
    slots = [1, 1, 0, 0]
    is_valid, msg = validate_talisman(8, skills, slots)
    assert is_valid is False
    assert "レベル(4)が不正です" in msg

def test_validate_talisman_ng_pattern_mismatch_ts_tl_002():
    # TS-TL-002: 存在しないパターン
    # A - A - A in Rarity 8 (Rarity 8 only has B-x-x, C-x-x, D-x-x)
    skills = [
        {"name": "攻撃", "level": 1},
        {"name": "見切り", "level": 1},
        {"name": "砲術", "level": 1}
    ]
    slots = [1, 1, 0, 0]
    is_valid, msg = validate_talisman(8, skills, slots)
    assert is_valid is False
    assert "存在しません" in msg

def test_validate_talisman_ng_slot_mismatch_ts_tl_002():
    # Slots that don't match Rarity 8 B-A-G:
    # B-A-G allows [1]ーー, [1]①ー, [1]①①
    # Trying: [0, 3, 0, 0] => ③ーー
    skills = [
        {"name": "砲術", "level": 2},
        {"name": "攻撃", "level": 1},
        {"name": "無我の境地", "level": 3}
    ]
    slots = [0, 3, 0, 0]
    is_valid, msg = validate_talisman(8, skills, slots)
    assert is_valid is False
    assert "出現し得ないパターン" in msg

def test_get_valid_skill_names():
    # Rarity 8, NO prev skills
    # Group A contains Attack, Artillery, etc.
    names = get_valid_skill_names(8, [])
    assert "攻撃" in names
    assert "砲術" in names

def test_get_valid_levels_for_skill():
    # Rarity 8, "砲術" in Group A is Lv1, in Group B is Lv2, in Group C is Lv3.
    # For Rarity 8, first group must be B, C, or D.
    # Group B has Artillery Lv2, Group C has Artillery Lv3. Group D has none.
    levels = get_valid_levels_for_skill(8, [], "砲術")
    assert 2 in levels
    assert 3 in levels
    assert 1 not in levels

def test_get_valid_slot_levels():
    # Rarity 8, Skill: 砲術 Lv2 (Group B)
    # If Group B is first, slots allowed might be [1]①①, [1]①ー, etc.
    # Slot 1 (W) should allow 1
    levels = get_valid_slot_levels(8, [("砲術", 2)], [])
    assert 1 in levels
    
    # If Slot 1 is 1, Slot 2 (A1) levels:
    levels2 = get_valid_slot_levels(8, [("砲術", 2)], [1])
    # According to pattern [1]①ー, 1 is allowed.
    # According to pattern [1]ーー, 0 is allowed.
    assert 1 in levels2
    assert 0 in levels2

def test_validate_talisman_ng_rarity_weapon_slot_exclusivity():
    # Rarity 7 using B-A-G (valid for Rarity 7 as well), but applying weapon slot [1]
    skills = [
        {"name": "砲術", "level": 2},
        {"name": "攻撃", "level": 1},
        {"name": "無我の境地", "level": 3}
    ]
    # [1]ーー => slots: [1, 0, 0, 0]
    slots = [1, 0, 0, 0]
    is_valid, msg = validate_talisman(7, skills, slots)
    assert is_valid is False
    assert "武器スロットはレア度8でのみ設定可能" in msg

def test_validate_talisman_ng_unsupported_slot_string():
    # Rarity 8, but using slot [2, 2, 2, 2] which is completely unsupported
    skills = [
        {"name": "砲術", "level": 2},
        {"name": "攻撃", "level": 1},
        {"name": "無我の境地", "level": 3}
    ]
    slots = [2, 2, 2, 2]
    is_valid, msg = validate_talisman(8, skills, slots)
    assert is_valid is False
    assert "出現し得ないパターン" in msg

@patch('src.logic.talismans.save_talismans', return_value=True)
@patch('src.logic.talismans.load_talismans')
def test_add_and_delete_talisman(mock_load, mock_save):
    # Setup initial mock DB
    mock_load.return_value = pd.DataFrame(columns=[
        "id", "rarity", "skill_1_name", "skill_1_level", "skill_2_name", "skill_2_level", 
        "skill_3_name", "skill_3_level", "weapon_slot_level", "armor_slot_1_level", 
        "armor_slot_2_level", "armor_slot_3_level", "is_favorite"
    ])
    
    skills = [{"name": "砲術", "level": 2}, {"name": "攻撃", "level": 1}, {"name": "無我の境地", "level": 3}]
    tid = add_talisman(8, skills, [1, 1, 0, 0])
    
    assert tid is not None
    assert mock_save.called
    saved_df = mock_save.call_args[0][0]
    assert len(saved_df) == 1
    assert saved_df.iloc[0]["rarity"] == 8
    assert saved_df.iloc[0]["skill_1_name"] == "砲術"
    assert saved_df.iloc[0]["is_favorite"] is False

    # Mock DB contains the new item now
    mock_load.return_value = saved_df
    
    # Toggle favorite
    res = toggle_favorite(tid)
    assert res is True
    updated_df = mock_save.call_args[0][0]
    assert updated_df.iloc[0]["is_favorite"] is True

    # Delete
    res_del = delete_talisman(tid)
    assert res_del is True
    del_df = mock_save.call_args[0][0]
    assert len(del_df) == 0
