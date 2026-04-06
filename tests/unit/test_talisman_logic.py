import pandas as pd
import pytest
from src.logic.talismans import filter_and_sort_talismans

@pytest.fixture
def sample_talismans():
    data = [
        {
            "id": "1", "rarity": 8, "is_favorite": True,
            "skill_1_name": "攻撃", "skill_1_level": 3,
            "skill_2_name": "達人", "skill_2_level": 2,
            "skill_3_name": "", "skill_3_level": 0,
            "weapon_slot_level": 3, "armor_slot_1_level": 1, "armor_slot_2_level": 1, "armor_slot_3_level": 0
        },
        {
            "id": "2", "rarity": 7, "is_favorite": False,
            "skill_1_name": "匠", "skill_1_level": 2,
            "skill_2_name": "攻撃", "skill_2_level": 1,
            "skill_3_name": "", "skill_3_level": 0,
            "weapon_slot_level": 0, "armor_slot_1_level": 3, "armor_slot_2_level": 2, "armor_slot_3_level": 1
        },
        {
            "id": "3", "rarity": 6, "is_favorite": False,
            "skill_1_name": "耳栓", "skill_1_level": 1,
            "skill_2_name": "", "skill_2_level": 0,
            "skill_3_name": "", "skill_3_level": 0,
            "weapon_slot_level": 0, "armor_slot_1_level": 1, "armor_slot_2_level": 0, "armor_slot_3_level": 0
        }
    ]
    return pd.DataFrame(data)

def test_filter_rarity_or(sample_talismans):
    # レア度 7 または 8
    result = filter_and_sort_talismans(sample_talismans, rarity=[7, 8])
    assert len(result) == 2
    assert set(result["id"]) == {"1", "2"}

def test_filter_skills_or(sample_talismans):
    # 「攻撃」または「耳栓」を含む
    result = filter_and_sort_talismans(sample_talismans, skills=["攻撃", "耳栓"])
    assert len(result) == 3 # 全て含まれる
    
    # 「匠」のみ
    result = filter_and_sort_talismans(sample_talismans, skills=["匠"])
    assert len(result) == 1
    assert result.iloc[0]["id"] == "2"

def test_filter_slots_min(sample_talismans):
    # 防具①が Lv3 以上
    result = filter_and_sort_talismans(sample_talismans, slot_a1_min=3)
    assert len(result) == 1
    assert result.iloc[0]["id"] == "2"

def test_filter_favorite(sample_talismans):
    result = filter_and_sort_talismans(sample_talismans, fav_only=True)
    assert len(result) == 1
    assert result.iloc[0]["id"] == "1"

def test_sort_rarity_desc(sample_talismans):
    result = filter_and_sort_talismans(sample_talismans, sort_by="レア度 (高→低)")
    assert result.iloc[0]["rarity"] == 8
    assert result.iloc[2]["rarity"] == 6
