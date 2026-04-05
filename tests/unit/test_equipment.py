import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
import streamlit as st
from src.logic.equipment import register_upgrade, get_active_upgrades, execute_upgrade, execute_all_upgrades

@pytest.fixture
def mock_storage(monkeypatch):
    storage = {"upgrades": pd.DataFrame(columns=["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"])}
    
    def mock_load(key, required_columns):
        return storage.get(key, pd.DataFrame(columns=required_columns))
    
    def mock_save(key, df):
        storage[key] = df
        return True

    monkeypatch.setattr("src.logic.equipment.load_data", mock_load)
    monkeypatch.setattr("src.logic.equipment.save_data", mock_save)
    return storage

def test_register_upgrade(mock_storage):
    uid = register_upgrade("大剣", "無", "シリーズA", "グループB", 5)
    assert uid is not None
    assert len(mock_storage["upgrades"]) == 1
    assert mock_storage["upgrades"].iloc[0]["remaining_count"] == 5

def test_execute_upgrade_decrement(mock_storage):
    uid = register_upgrade("太刀", "火", "S1", "G1", 3)
    success = execute_upgrade(uid, decrement=1)
    assert success
    df = get_active_upgrades()
    assert df[df["id"] == uid]["remaining_count"].values[0] == 2

def test_execute_all_upgrades(mock_storage):
    register_upgrade("大剣", "無", "S1", "G1", 5)
    register_upgrade("大剣", "無", "S2", "G2", 2)
    
    execute_all_upgrades(decrement=1)
    
    df = get_active_upgrades()
    assert df.iloc[0]["remaining_count"] == 1 # 2 -> 1
    assert df.iloc[1]["remaining_count"] == 4 # 5 -> 4

def test_execute_upgrade_sync_to_weapon(mock_storage, monkeypatch):
    """強化実施時に、対象武器のスキルが更新されるか検証"""
    mock_storage["upgrades"] = pd.DataFrame([
        {"id": "U1", "weapon_type": "大剣", "element": "火", 
         "series_skill": "炎属性強化", "group_skill": "匠の業", "remaining_count": 5}
    ])
    mock_storage["equipment"] = pd.DataFrame([
        {"id": "W1", "weapon_type": "大剣", "element": "火", "weapon_name": "テスタ",
         "current_series_skill": "なし", "current_group_skill": "なし"}
    ])
    
    # Mock equipment_box functions
    monkeypatch.setattr("src.logic.equipment_box.load_equipment", lambda: mock_storage["equipment"])
    monkeypatch.setattr("src.logic.equipment_box.save_equipment", lambda df: mock_storage.update({"equipment": df}) or True)

    with patch("src.logic.equipment.push_action") as mock_push:
        execute_upgrade("U1", decrement=1, weapon_id="W1")
        
        # Check weapon sync
        eq = mock_storage["equipment"]
        assert eq.iloc[0]["current_series_skill"] == "炎属性強化"
        assert eq.iloc[0]["current_group_skill"] == "匠の業"
        
        # Check upgrades decrement
        upg = mock_storage["upgrades"]
        assert upg.iloc[0]["remaining_count"] == 4
        assert mock_push.called
