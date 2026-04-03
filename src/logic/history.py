import streamlit as st
import pandas as pd
from src.database.gsheets_manager import load_data, save_data

def undo_last_action() -> bool:
    if 'undo_stack' not in st.session_state or len(st.session_state['undo_stack']) == 0:
        return False
        
    action = st.session_state['undo_stack'].pop()
    df = load_data()
    if df.empty and action['action_type'] != 'REGISTER':
        return False

    if action['action_type'] == 'REGISTER':
        # Undo Register = Delete the record
        # Store full record for Redo
        idx = df[df["id"] == action['target_id']].index
        if not idx.empty:
            action['full_record'] = df.loc[idx].iloc[0].to_dict()
            df = df.drop(idx)
    
    elif action['action_type'] == 'EXECUTE':
        # Undo Execute = Restore previous count
        idx = df[df["id"] == action['target_id']].index
        if not idx.empty:
            action['redo_count'] = df.loc[idx, "remaining_count"].iloc[0]
            df.loc[idx, "remaining_count"] = action['previous_count']

    elif action['action_type'] == 'EXECUTE_ALL':
        # Undo Execute All = Restore all previous counts
        for state in action['previous_states']:
            idx = df[df["id"] == state['id']].index
            if not idx.empty:
                df.loc[idx, "remaining_count"] = state['remaining_count']
            else:
                # If it was deleted because it reached 0, we'd need to re-add it? 
                # Actually, our execute_all keeps records even at 0 (only the UI filters them).
                # Wait, the previous logic removed them from UI but kept in DB? 
                # No, SQLite code didn't delete, it just set to 0.
                pass

    save_data(df)
    
    if 'redo_stack' not in st.session_state:
        st.session_state['redo_stack'] = []
    st.session_state['redo_stack'].append(action)
    return True

def redo_last_action() -> bool:
    if 'redo_stack' not in st.session_state or len(st.session_state['redo_stack']) == 0:
        return False
        
    action = st.session_state['redo_stack'].pop()
    df = load_data()

    if action['action_type'] == 'REGISTER':
        # Redo Register = Re-add the record
        new_row = pd.DataFrame([action['full_record']])
        if df.empty:
            df = new_row
        else:
            df = pd.concat([df, new_row], ignore_index=True)
        
    elif action['action_type'] == 'EXECUTE':
        # Redo Execute = Apply the count change again
        idx = df[df["id"] == action['target_id']].index
        if not idx.empty:
            df.loc[idx, "remaining_count"] = action['redo_count']

    elif action['action_type'] == 'EXECUTE_ALL':
        # Redo Execute All = Apply the decrement again
        target_ids = [state['id'] for state in action['previous_states']]
        mask = df["id"].isin(target_ids)
        df.loc[mask, "remaining_count"] = df.loc[mask, "remaining_count"].apply(lambda x: max(0, x - action['decrement']))

    save_data(df)
    
    if 'undo_stack' not in st.session_state:
        st.session_state['undo_stack'] = []
    st.session_state['undo_stack'].append(action)
    return True
