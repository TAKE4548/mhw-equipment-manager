import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from src.logic.talismans import (
    validate_talisman, get_valid_skill_names, 
    get_valid_levels_for_skill, get_valid_slot_levels,
    add_talisman, delete_talisman, update_talisman
)

# Mock Master Data for tests
MOCK_MASTER = {
    "groups": {
        "A": {"見切り": 1, "回避性能": 1},
        "B": {"砲術": 2, "攻撃": 2},
        "C": {"砲術": 3, "弾導強化": 3},
        "D": {"攻撃": 2, "超会心": 1},
        "F": {"体術": 3},
        "G": {"植生学": 4},
        "H": {"耳栓": 1},
        "J": {"弱点特効": 1}
    },
    "rarity_patterns": {
        "5": [
            {
                "slots": ["①①ー", "②ーー"],
                "skill_patterns": [["A", "G"], ["A", "J"]]
            }
        ],
        "8": [
            {
                "slots": ["[1]ーー", "[1]①ー", "[1]①①"],
                "skill_patterns": [
                    ["B", "A", "G"],
                    ["B", "A", "H"],
                    ["B", "A", "J"]
                ]
            }
        ]
    }
}

@pytest.fixture(autouse=True)
def mock_master_data():
    with patch("src.logic.talismans.load_talisman_master", return_value=MOCK_MASTER):
        yield

@pytest.fixture
def mock_storage_talisman():
    # Patch the higher-level load_talismans and the lower-level save_data
    with patch("src.logic.talismans.load_talismans") as mock_load_t, \
         patch("src.logic.talismans.save_talismans", return_value=True) as mock_save_t, \
         patch("src.logic.talismans.push_action") as mock_push:
        
        # Ensure .clear() doesn't fail on the mock
        mock_load_t.clear = MagicMock()
        
        # Default empty DF
        initial_df = pd.DataFrame(columns=[
            "id", "rarity", "skill_1_name", "skill_1_level",
            "skill_2_name", "skill_2_level", "skill_3_name", "skill_3_level",
            "weapon_slot_level", "armor_slot_1_level", "armor_slot_2_level", "armor_slot_3_level",
            "is_favorite"
        ])
        mock_load_t.side_effect = lambda *args: mock_load_t.return_value if hasattr(mock_load_t, 'return_value') and not isinstance(mock_load_t.return_value, MagicMock) else initial_df
        mock_load_t.return_value = initial_df
        yield mock_load_t, mock_save_t, mock_push

def test_validate_talisman_ok_ts_tl_001():
    skills = [
        {"name": "砲術", "level": 2},
        {"name": "見切り", "level": 1},
        {"name": "植生学", "level": 4}
    ]
    slots = [1, 1, 1, 0]
    is_valid, msg = validate_talisman(8, skills, slots)
    assert is_valid is True, f"Expected valid, got invalid: {msg}"

def test_validate_talisman_ng_level_mismatch_ts_tl_002():
    skills = [{"name": "砲術", "level": 4}]
    slots = [1, 0, 0, 0]
    is_valid, msg = validate_talisman(8, skills, slots)
    assert is_valid is False
    assert "レベル(4)が不正です" in msg

def test_validate_talisman_ng_pattern_mismatch_ts_tl_002():
    skills = [{"name": "見切り", "level": 1}, {"name": "回避性能", "level": 1}]
    slots = [1, 0, 0, 0]
    is_valid, msg = validate_talisman(8, skills, slots)
    assert is_valid is False
    assert "組み合わせ" in msg

def test_validate_talisman_ng_slot_mismatch_ts_tl_002():
    skills = [{"name": "砲術", "level": 2}, {"name": "見切り", "level": 1}, {"name": "植生学", "level": 4}]
    slots = [0, 1, 0, 0]
    is_valid, msg = validate_talisman(8, skills, slots)
    assert is_valid is False
    assert "スロット構成" in msg

def test_get_valid_skill_names():
    names = get_valid_skill_names(8, [])
    assert "砲術" in names
    assert "攻撃" in names

def test_get_valid_levels_for_skill():
    levels = get_valid_levels_for_skill(8, [], "砲術")
    assert 2 in levels

def test_get_valid_slot_levels():
    levels = get_valid_slot_levels(8, [("砲術", 2)], [])
    assert 1 in levels

def test_validate_talisman_ng_rarity_weapon_slot_exclusivity():
    skills = [{"name": "見切り", "level": 1}]
    slots = [1, 1, 0, 0]
    is_valid, msg = validate_talisman(5, skills, slots)
    assert is_valid is False
    assert "武器スロットはレア度8でのみ" in msg

def test_add_and_delete_talisman(mock_storage_talisman):
    mock_load_t, mock_save_t, mock_push = mock_storage_talisman
    
    t_id = add_talisman(8, [{"name": "砲術", "level": 2}], [1, 0, 0, 0])
    assert t_id is not None
    assert mock_save_t.called
    assert mock_push.called
    
    # Mock return for delete
    mock_load_t.return_value = pd.DataFrame([{"id": t_id, "rarity": 8}])
    res = delete_talisman(t_id)
    assert res is True
    assert mock_push.call_count == 2

def test_update_talisman(mock_storage_talisman):
    mock_load_t, mock_save_t, mock_push = mock_storage_talisman
    t_id = "test-uuid"
    mock_load_t.return_value = pd.DataFrame([{
        "id": t_id, "rarity": 5, 
        "skill_1_name": "見切り", "skill_1_level": 1,
        "weapon_slot_level": 0, "armor_slot_1_level": 1, "armor_slot_2_level": 0, "armor_slot_3_level": 0
    }])
    
    res = update_talisman(t_id, 8, [{"name": "砲術", "level": 2}], [1, 1, 0, 0])
    assert res is True
    assert mock_push.called
    
    # Check if rarity was updated to 8 in the saved DF
    args, kwargs = mock_save_t.call_args
    df_saved = args[0] # save_talismans takes df as first arg
    assert df_saved.iloc[0]["rarity"] == 8
