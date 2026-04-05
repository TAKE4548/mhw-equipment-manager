import pytest
import pandas as pd
from src.logic.restoration_tracker import (
    register_tracker, advance_all_trackers, execute_apply_and_advance,
    delete_tracker, update_tracker, load_trackers, TRACKER_TABLE
)
from src.logic.equipment_box import load_equipment, save_equipment
from src.database.storage_manager import save_data

@pytest.fixture(autouse=True)
def setup_test_data():
    """Resets storage for clean testing."""
    save_data(TRACKER_TABLE, pd.DataFrame())
    # Mock equipment
    eq_df = pd.DataFrame([
        {"id": "w1", "name": "Weapon 1", "rest_1_type": "なし", "rest_1_level": "なし"}
    ])
    save_equipment(eq_df)

def test_register_tracker():
    target_bonuses = [{"type": "基礎攻撃", "level": "Ⅱ"}]
    assert register_tracker("w1", 10, target_bonuses) is True
    df = load_trackers()
    assert len(df) == 1
    assert df.iloc[0]["weapon_id"] == "w1"
    assert df.iloc[0]["remaining_count"] == 10
    assert df.iloc[0]["target_rest_1_type"] == "基礎攻撃"
    assert df.iloc[0]["target_rest_1_level"] == "Ⅱ"
    assert df.iloc[0]["target_rest_2_type"] == "なし"

def test_advance_all_trackers():
    register_tracker("w1", 10, [])
    register_tracker("w1", 5, [])
    
    assert advance_all_trackers(3) is True
    df = load_trackers()
    assert df[df["remaining_count"] == 7].shape[0] == 1
    assert df[df["remaining_count"] == 2].shape[0] == 1
    
    # Border case: should remove when reached 0
    advance_all_trackers(2)
    df = load_trackers()
    assert len(df) == 1
    assert df.iloc[0]["remaining_count"] == 5

def test_execute_apply_and_advance():
    # Use normalized type or it will be normalized upon loading equipment
    register_tracker("w1", 5, [{"type": "会心率強化", "level": "Ⅰ"}])
    df = load_trackers()
    t_id = df.iloc[0]["id"]
    
    # Register another one to verify global advance
    register_tracker("w1", 10, [])
    
    assert execute_apply_and_advance(t_id) is True
    
    # 1. Weapon should be updated
    eq_df = load_equipment()
    # Note: execute_apply_and_advance copies from tracker to weapon. 
    # load_equipment() will normalize what's in the weapon.
    assert eq_df.iloc[0]["rest_1_type"] == "会心率強化"
    
    # 2. Applied tracker should be gone, others should be advanced
    df = load_trackers()
    assert len(df) == 1
    assert df.iloc[0]["remaining_count"] == 5  # 10 - 5

def test_delete_tracker():
    register_tracker("w1", 5, [])
    df = load_trackers()
    t_id = df.iloc[0]["id"]
    
    assert delete_tracker(t_id) is True
    assert len(load_trackers()) == 0

def test_update_tracker():
    register_tracker("w1", 5, [{"type": "攻撃", "level": "Ⅰ"}])
    df = load_trackers()
    t_id = df.iloc[0]["id"]
    
    new_bonuses = [{"type": "会心", "level": "Ⅱ"}]
    assert update_tracker(t_id, 15, new_bonuses) is True
    
    df = load_trackers()
    assert df.iloc[0]["remaining_count"] == 15
    assert df.iloc[0]["target_rest_1_type"] == "会心"
