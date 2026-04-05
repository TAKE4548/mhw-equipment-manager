import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.logic.restoration_tracker import execute_apply_and_advance, advance_all_trackers

@pytest.fixture
def mock_storage(monkeypatch):
    # 日本語 UTF-8 データの定義
    tracker_cols = ["id", "weapon_id", "remaining_count"]
    for i in range(1, 6):
        tracker_cols.append(f"target_rest_{i}_type")
        tracker_cols.append(f"target_rest_{i}_level")
        
    weapon_cols = ["id", "weapon_type", "element", "weapon_name"]
    for i in range(1, 6):
        weapon_cols.append(f"rest_{i}_type")
        weapon_cols.append(f"rest_{i}_level")

    storage = {
        "trackers": pd.DataFrame(columns=tracker_cols),
        "weapons": pd.DataFrame(columns=weapon_cols)
    }
    
    def mock_load(key, required_columns=None):
        return storage.get(key, pd.DataFrame(columns=required_columns))
    
    def mock_save(key, df):
        storage[key] = df
        return True

    # トップレベルインポートを考慮したモック
    monkeypatch.setattr("src.logic.restoration_tracker.load_trackers", lambda: mock_load("trackers"))
    monkeypatch.setattr("src.logic.restoration_tracker.save_trackers", lambda df: mock_save("trackers", df))
    monkeypatch.setattr("src.logic.restoration_tracker.load_equipment", lambda: mock_load("weapons"))
    monkeypatch.setattr("src.logic.restoration_tracker.save_equipment", lambda df: mock_save("weapons", df))
    return storage

def test_advance_all_trackers_japanese(mock_storage):
    """日本語データを含む全トラック進行の検証"""
    mock_storage["trackers"] = pd.concat([mock_storage["trackers"], pd.DataFrame([
        {"id": "T1", "remaining_count": 1, "target_rest_1_type": "回避性能", "target_rest_1_level": "Ⅱ"},
        {"id": "T2", "remaining_count": 5, "target_rest_1_type": "属性強化", "target_rest_1_level": "Ⅲ"}
    ])], ignore_index=True)
    
    with patch("src.logic.restoration_tracker.push_action") as mock_push:
        advance_all_trackers(1)
        df = mock_storage["trackers"]
        # T1 が自動削除されていること
        assert len(df) == 1
        assert df.iloc[0]["target_rest_1_type"] == "属性強化"
        assert mock_push.called

def test_execute_apply_sync_japanese(mock_storage):
    """日本語データを含む武器同期（適用）の検証"""
    new_tracker = {"id": "T1", "weapon_id": "W1", "remaining_count": 1}
    for i in range(1, 6):
        new_tracker[f"target_rest_{i}_type"] = "攻撃力強化" if i == 1 else "属性強化"
        new_tracker[f"target_rest_{i}_level"] = "Ⅱ"
    
    mock_storage["trackers"] = pd.concat([mock_storage["trackers"], pd.DataFrame([new_tracker])], ignore_index=True)
    
    new_weapon = {"id": "W1", "weapon_type": "大剣", "element": "火", "weapon_name": "テスタ"}
    for i in range(1, 6):
        new_weapon[f"rest_{i}_type"] = "なし"
        new_weapon[f"rest_{i}_level"] = "なし"
        
    mock_storage["weapons"] = pd.concat([mock_storage["weapons"], pd.DataFrame([new_weapon])], ignore_index=True)
    
    with patch("src.logic.restoration_tracker.push_action") as mock_push:
        execute_apply_and_advance("T1")
        
        eq = mock_storage["weapons"]
        target = eq[eq["id"].astype(str) == "W1"].iloc[0]
        # 同期された値が正しい日本語であることを検証
        assert target["rest_1_type"] == "攻撃力強化"
        assert target["rest_2_type"] == "属性強化"
        assert mock_push.called
