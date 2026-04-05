import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import src.logic.restoration_tracker as rt
import src.logic.equipment_box as eb


@pytest.fixture(autouse=True)
def setup_test_data(monkeypatch):
    """Resets storage and ensures load functions return DataFrames for clean testing."""
    # Local storage for the test session
    storage = {
        "trackers": pd.DataFrame(columns=rt.TRACKER_COLUMNS),
        "equipment": pd.DataFrame([
            {"id": "w1", "name": "Weapon 1", "weapon_name": "Weapon 1", "weapon_type": "大剣", "element": "なし",
             "rest_1_type": "なし", "rest_1_level": "なし",
             "rest_2_type": "なし", "rest_2_level": "なし",
             "rest_3_type": "なし", "rest_3_level": "なし",
             "rest_4_type": "なし", "rest_4_level": "なし",
             "rest_5_type": "なし", "rest_5_level": "なし"}
        ])
    }
    
    # Mock load_trackers
    mock_load_t = MagicMock()
    mock_load_t.side_effect = lambda *args: storage["trackers"]
    mock_load_t.clear = MagicMock()
    
    # Mock save_trackers
    def mock_save_t(df):
        storage["trackers"] = df
        return True
        
    # Mock load_equipment
    mock_load_e = MagicMock()
    mock_load_e.side_effect = lambda *args: storage["equipment"]
    # Ensure clear() exists on the mock
    mock_load_e.clear = MagicMock()
    
    # Mock save_equipment
    def mock_save_e(df):
        storage["equipment"] = df
        return True

    # Apply patches directly to the module namespace where they are used
    monkeypatch.setattr(rt, "load_trackers", mock_load_t)
    monkeypatch.setattr(rt, "save_trackers", mock_save_t)
    monkeypatch.setattr(rt, "load_equipment", mock_load_e)
    monkeypatch.setattr(rt, "save_equipment", mock_save_e)
    monkeypatch.setattr(rt, "push_action", MagicMock())
    
    yield storage


def test_register_tracker():
    target_bonuses = [{"type": "基礎攻撃", "level": "Ⅱ"}]
    assert rt.register_tracker("w1", 10, target_bonuses) is True
    df = rt.load_trackers()
    assert len(df) == 1
    assert df.iloc[0]["weapon_id"] == "w1"
    assert df.iloc[0]["remaining_count"] == 10
    assert df.iloc[0]["target_rest_1_type"] == "基礎攻撃"
    assert df.iloc[0]["target_rest_1_level"] == "Ⅱ"
    assert df.iloc[0]["target_rest_2_type"] == "なし"

def test_advance_all_trackers():
    rt.register_tracker("w1", 10, [])
    rt.register_tracker("w1", 5, [])
    
    assert rt.advance_all_trackers(3) is True
    df = rt.load_trackers()
    assert df[df["remaining_count"] == 7].shape[0] == 1
    assert df[df["remaining_count"] == 2].shape[0] == 1
    
    # Border case: should remove when reached 0
    rt.advance_all_trackers(2)
    df = rt.load_trackers()
    assert len(df) == 1
    assert df.iloc[0]["remaining_count"] == 5

def test_execute_apply_and_advance():
    rt.register_tracker("w1", 5, [{"type": "会心率強化", "level": "Ⅰ"}])
    df = rt.load_trackers()
    t_id = df.iloc[0]["id"]
    
    rt.register_tracker("w1", 10, [])
    
    # Mock save_equipment to ensure it returns True
    assert rt.execute_apply_and_advance(t_id) is True
    
    # 2. Applied tracker should be gone
    df = rt.load_trackers()
    assert len(df) == 1
    assert df.iloc[0]["remaining_count"] == 5

def test_delete_tracker():
    rt.register_tracker("w1", 5, [])
    df = rt.load_trackers()
    t_id = df.iloc[0]["id"]
    
    assert rt.delete_tracker(t_id) is True
    assert len(rt.load_trackers()) == 0

def test_update_tracker():
    rt.register_tracker("w1", 5, [{"type": "攻撃", "level": "Ⅰ"}])
    df = rt.load_trackers()
    t_id = df.iloc[0]["id"]
    
    new_bonuses = [{"type": "会心", "level": "Ⅱ"}]
    assert rt.update_tracker(t_id, 15, new_bonuses) is True
    
    df = rt.load_trackers()
    assert df.iloc[0]["remaining_count"] == 15
    assert df.iloc[0]["target_rest_1_type"] == "会心"
