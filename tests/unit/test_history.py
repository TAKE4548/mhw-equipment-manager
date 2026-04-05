import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
import streamlit as st
from src.logic.history import push_action, undo_last_action, redo_last_action

@pytest.fixture
def mock_storage(monkeypatch):
    storage = {"test_table": pd.DataFrame(columns=["id", "val"])}
    
    def mock_save(key, df):
        storage[key] = df
        return True

    monkeypatch.setattr("src.logic.history.save_data", mock_save)
    return storage

def test_push_undo_redo_flow(mock_storage):
    """push -> undo -> redo の一連の流れでデータが正しく復元されるか検証"""
    prev_df = pd.DataFrame([{"id": 1, "val": "A"}])
    next_df = pd.DataFrame([{"id": 1, "val": "B"}])
    
    # 記録
    push_action("UPDATE", "test_table", prev_df, next_df)
    
    # Undo
    undo_last_action()
    assert mock_storage["test_table"].iloc[0]["val"] == "A"
    
    # Redo
    redo_last_action()
    assert mock_storage["test_table"].iloc[0]["val"] == "B"

def test_stack_limit():
    """スタックサイズが20件に制限されているか検証"""
    st.session_state['undo_stack'] = []
    df = pd.DataFrame()
    for i in range(25):
        push_action("ACT", "table", df, df)
    
    assert len(st.session_state['undo_stack']) == 20
