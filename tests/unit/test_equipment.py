import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.logic.equipment import (
    register_upgrade, get_active_upgrades, execute_upgrade, execute_all_upgrades,
    UPGRADES_COLUMNS
)

@pytest.fixture
def mock_storage(monkeypatch):
    # Initial state
    storage = {"upgrades": pd.DataFrame(columns=UPGRADES_COLUMNS)}
    
    # Use MagicMock so that load_upgrades.clear() doesn't fail
    # We define a side_effect to always return the current value from storage
    mock_load = MagicMock()
    mock_load.side_effect = lambda *args: storage.get("upgrades")
    
    def mock_save(key, df):
        storage[key] = df
        return True

    monkeypatch.setattr("src.logic.equipment.load_upgrades", mock_load)
    monkeypatch.setattr("src.logic.equipment.save_data", mock_save)
    return storage

def test_register_upgrade(mock_storage):
    uid = register_upgrade("大剣", "無", "シリーズA", "グループB", 5)
    assert uid is not None
    assert len(mock_storage["upgrades"]) == 1
    assert mock_storage["upgrades"].iloc[0]["remaining_count"] == 5

def test_execute_upgrade_decrement(mock_storage):
    uid = register_upgrade("太刀", "火", "S1", "G1", 3)
    # execute_upgrade calls execute_all_upgrades internally in current logic
    success = execute_upgrade(uid, decrement=1)
    assert success
    df = get_active_upgrades()
    assert df[df["id"] == uid]["remaining_count"].values[0] == 2

def test_execute_all_upgrades_with_auto_delete(mock_storage):
    register_upgrade("大剣", "無", "S1", "G1", 1) # Will be 0 -> deleted
    register_upgrade("大剣", "無", "S2", "G2", 5) # Will be 4
    
    execute_all_upgrades(decrement=1)
    
    df = mock_storage["upgrades"]
    assert len(df) == 1
    assert df.iloc[0]["remaining_count"] == 4
    assert df.iloc[0]["series_skill"] == "S2"

def test_execute_upgrade_sync_to_weapon(mock_storage, monkeypatch):
    """強化実施時に、対象武器のスキルが更新されるか検証"""
    mock_storage["upgrades"] = pd.DataFrame([
        {"id": "U1", "weapon_type": "大剣", "element": "火", 
         "series_skill": "炎属性強化", "group_skill": "匠の業", "remaining_count": 5}
    ], columns=UPGRADES_COLUMNS)
    
    equipment_df = pd.DataFrame([
        {"id": "W1", "weapon_type": "大剣", "element": "火", "weapon_name": "テスタ",
         "current_series_skill": "なし", "current_group_skill": "なし"}
    ])
    
    # Mock equipment_box functions with MagicMock to handle .clear()
    mock_load_eq = MagicMock()
    mock_load_eq.side_effect = lambda *args: equipment_df
    monkeypatch.setattr("src.logic.equipment_box.load_equipment", mock_load_eq)
    
    def mock_save_eq(df):
        nonlocal equipment_df
        equipment_df = df
        mock_load_eq.return_value = df # Update mock return value
        return True
    monkeypatch.setattr("src.logic.equipment_box.save_equipment", mock_save_eq)

    with patch("src.logic.equipment.push_action") as mock_push:
        execute_upgrade("U1", decrement=1, weapon_id="W1")
        
        # Check weapon sync - use the updated equipment_df or mock_load_eq result
        final_df = mock_load_eq()
        assert final_df.iloc[0]["current_series_skill"] == "炎属性強化"
        assert final_df.iloc[0]["current_group_skill"] == "匠の業"
        
        # Check upgrades decrement
        upg = mock_storage["upgrades"]
        assert upg.iloc[0]["remaining_count"] == 4
        assert mock_push.called
