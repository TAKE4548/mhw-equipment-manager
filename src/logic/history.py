import streamlit as st
import pandas as pd
from src.database.storage_manager import load_data, save_data

from src.utils.cache_utils import clear_logic_cache

def get_history():
    """Returns the undo and redo stacks from session state."""
    if 'undo_stack' not in st.session_state: st.session_state['undo_stack'] = []
    if 'redo_stack' not in st.session_state: st.session_state['redo_stack'] = []
    return st.session_state['undo_stack'], st.session_state['redo_stack']

def push_action(action_type: str, table: str, prev_df: pd.DataFrame, next_df: pd.DataFrame):
    """Records an action for Undo/Redo."""
    if not isinstance(prev_df, pd.DataFrame) or not isinstance(next_df, pd.DataFrame):
        # Fail gracefully if not a DataFrame (preventing future malformed pushes)
        return

    undo_stack, redo_stack = get_history()
    undo_stack.append({
        'action_type': action_type,
        'table': table,
        'prev_df': prev_df.copy(),
        'next_df': next_df.copy()
    })
    redo_stack.clear()
    # Limit stack size to 20
    if len(undo_stack) > 20: undo_stack.pop(0)

def undo_last_action() -> bool:
    undo_stack, redo_stack = get_history()
    if not undo_stack: return False
    
    action = undo_stack.pop()
    if save_data(action['table'], action['prev_df']):
        clear_logic_cache(action['table'])
        redo_stack.append(action)
        return True
    return False

def redo_last_action() -> bool:
    undo_stack, redo_stack = get_history()
    if not redo_stack: return False
    
    action = redo_stack.pop()
    if save_data(action['table'], action['next_df']):
        clear_logic_cache(action['table'])
        undo_stack.append(action)
        return True
    return False


