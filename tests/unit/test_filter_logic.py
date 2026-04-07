import pandas as pd
import pytest
from src.logic.equipment_box import filter_equipment

# Mocking master data since filter_equipment calls it for sorting
@pytest.fixture(autouse=True)
def mock_master(mocker):
    mocker.patch("src.logic.equipment_box.get_master_data", return_value={
        "weapon_types": ["大剣", "太刀"],
        "elements": ["火", "水", "無"]
    })

def test_filter_equipment_series_group():
    df = pd.DataFrame([
        {
            "id": "1", "weapon_name": "W1", "weapon_type": "大剣", "element": "火",
            "current_series_skill": "SkillA", "current_group_skill": "GroupA",
            "enhancement_type": "Attack",
            "p_bonus_1": "なし", "p_bonus_2": "なし", "p_bonus_3": "なし",
            "rest_1_type": "なし", "rest_1_level": "なし",
            "rest_2_type": "なし", "rest_2_level": "なし",
            "rest_3_type": "なし", "rest_3_level": "なし",
            "rest_4_type": "なし", "rest_4_level": "なし",
            "rest_5_type": "なし", "rest_5_level": "なし"
        },
        {
            "id": "2", "weapon_name": "W2", "weapon_type": "太刀", "element": "水",
            "current_series_skill": "SkillB", "current_group_skill": "GroupB",
            "enhancement_type": "Critical",
            "p_bonus_1": "なし", "p_bonus_2": "なし", "p_bonus_3": "なし",
            "rest_1_type": "なし", "rest_1_level": "なし",
            "rest_2_type": "なし", "rest_2_level": "なし",
            "rest_3_type": "なし", "rest_3_level": "なし",
            "rest_4_type": "なし", "rest_4_level": "なし",
            "rest_5_type": "なし", "rest_5_level": "なし"
        }
    ])
    
    # Filter by series
    res = filter_equipment(df, series_skills=["SkillA"])
    assert len(res) == 1
    assert res.iloc[0]['id'] == "1"
    
    # Filter by group
    res = filter_equipment(df, group_skills=["GroupB"])
    assert len(res) == 1
    assert res.iloc[0]['id'] == "2"

def test_filter_equipment_restoration_and_logic():
    df = pd.DataFrame([
        {
            "id": "1", "weapon_name": "W1", "weapon_type": "大剣", "element": "火",
            "current_series_skill": "なし", "current_group_skill": "なし",
            "enhancement_type": "Attack",
            "p_bonus_1": "なし", "p_bonus_2": "なし", "p_bonus_3": "なし",
            "rest_1_type": "基礎攻撃力強化", "rest_1_level": "Ⅱ",
            "rest_2_type": "会心率強化", "rest_2_level": "Ⅲ",
            "rest_3_type": "なし", "rest_3_level": "なし",
            "rest_4_type": "なし", "rest_4_level": "なし",
            "rest_5_type": "なし", "rest_5_level": "なし"
        },
        {
            "id": "2", "weapon_name": "W2", "weapon_type": "太刀", "element": "水",
            "current_series_skill": "なし", "current_group_skill": "なし",
            "enhancement_type": "Critical",
            "p_bonus_1": "なし", "p_bonus_2": "なし", "p_bonus_3": "なし",
            "rest_1_type": "基礎攻撃力強化", "rest_1_level": "Ⅱ",
            "rest_2_type": "属性強化", "rest_2_level": "無印",
            "rest_3_type": "なし", "rest_3_level": "なし",
            "rest_4_type": "なし", "rest_4_level": "なし",
            "rest_5_type": "なし", "rest_5_level": "なし"
        }
    ])
    
    # Single filter
    res = filter_equipment(df, restoration_bonuses=["基礎攻撃力強化 [Ⅱ]"])
    assert len(res) == 2
    
    # AND filter (基礎攻撃Ⅱ & 会心Ⅲ)
    res = filter_equipment(df, restoration_bonuses=["基礎攻撃力強化 [Ⅱ]", "会心率強化 [Ⅲ]"])
    assert len(res) == 1
    assert res.iloc[0]['id'] == "1"
    
    # AND filter (基礎攻撃Ⅱ & 属性強化)
    res = filter_equipment(df, restoration_bonuses=["基礎攻撃力強化 [Ⅱ]", "属性強化"])
    assert len(res) == 1
    assert res.iloc[0]['id'] == "2"
    
    # AND filter (会心Ⅲ & 属性強化) - Should be Empty
    res = filter_equipment(df, restoration_bonuses=["会心率強化 [Ⅲ]", "属性強化"])
    assert len(res) == 0

def test_filter_equipment_production_and_logic():
    df = pd.DataFrame([
        {
            "id": "1", "weapon_name": "W1", "weapon_type": "大剣", "element": "火",
            "current_series_skill": "なし", "current_group_skill": "なし",
            "enhancement_type": "Attack",
            "p_bonus_1": "基礎攻撃力増強", "p_bonus_2": "会心率増強", "p_bonus_3": "なし",
            "rest_1_type": "なし", "rest_1_level": "なし",
            "rest_2_type": "なし", "rest_2_level": "なし",
            "rest_3_type": "なし", "rest_3_level": "なし",
            "rest_4_type": "なし", "rest_4_level": "なし",
            "rest_5_type": "なし", "rest_5_level": "なし"
        },
        {
            "id": "2", "weapon_name": "W2", "weapon_type": "太刀", "element": "水",
            "current_series_skill": "なし", "current_group_skill": "なし",
            "enhancement_type": "Critical",
            "p_bonus_1": "基礎攻撃力増強", "p_bonus_2": "属性増強", "p_bonus_3": "なし",
            "rest_1_type": "なし", "rest_1_level": "なし",
            "rest_2_type": "なし", "rest_2_level": "なし",
            "rest_3_type": "なし", "rest_3_level": "なし",
            "rest_4_type": "なし", "rest_4_level": "なし",
            "rest_5_type": "なし", "rest_5_level": "なし"
        }
    ])
    
    # AND filter (攻撃増強 & 会心増強)
    res = filter_equipment(df, production_bonuses=["基礎攻撃力増強", "会心率増強"])
    assert len(res) == 1
    assert res.iloc[0]['id'] == "1"
    
    # AND filter (攻撃増強 & 属性増強)
    res = filter_equipment(df, production_bonuses=["基礎攻撃力増強", "属性増強"])
    assert len(res) == 1
    assert res.iloc[0]['id'] == "2"
