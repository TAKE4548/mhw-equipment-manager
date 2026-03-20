import streamlit as st
from src.database.sqlite_manager import get_db_connection

def undo_last_action() -> bool:
    if 'undo_stack' not in st.session_state or len(st.session_state['undo_stack']) == 0:
        return False
        
    action = st.session_state['undo_stack'].pop()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if action['action_type'] == 'REGISTER':
            cursor.execute("SELECT * FROM skill_upgrade WHERE id=?", (action['target_id'],))
            row = cursor.fetchone()
            if row:
                action['full_record'] = dict(row)
                cursor.execute("DELETE FROM skill_upgrade WHERE id=?", (action['target_id'],))
        
        elif action['action_type'] == 'EXECUTE':
            cursor.execute("SELECT remaining_count FROM skill_upgrade WHERE id=?", (action['target_id'],))
            row = cursor.fetchone()
            if row:
                action['redo_count'] = row['remaining_count']
                cursor.execute("UPDATE skill_upgrade SET remaining_count=? WHERE id=?", 
                               (action['previous_count'], action['target_id']))

        elif action['action_type'] == 'EXECUTE_ALL':
            for state in action['previous_states']:
                cursor.execute("UPDATE skill_upgrade SET remaining_count=? WHERE id=?", 
                               (state['remaining_count'], state['id']))
                
    if 'redo_stack' not in st.session_state:
        st.session_state['redo_stack'] = []
    st.session_state['redo_stack'].append(action)
    return True

def redo_last_action() -> bool:
    if 'redo_stack' not in st.session_state or len(st.session_state['redo_stack']) == 0:
        return False
        
    action = st.session_state['redo_stack'].pop()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if action['action_type'] == 'REGISTER':
            rec = action['full_record']
            cursor.execute('''
                INSERT INTO skill_upgrade (id, weapon_type, element, series_skill, group_skill, remaining_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (rec['id'], rec['weapon_type'], rec['element'], rec['series_skill'], rec['group_skill'], rec['remaining_count']))
            
        elif action['action_type'] == 'EXECUTE':
            cursor.execute("UPDATE skill_upgrade SET remaining_count=? WHERE id=?", 
                           (action['redo_count'], action['target_id']))

        elif action['action_type'] == 'EXECUTE_ALL':
            target_ids = [state['id'] for state in action['previous_states']]
            if target_ids:
                placeholders = ','.join('?' * len(target_ids))
                params = [action['decrement']] + target_ids
                cursor.execute(f'''
                    UPDATE skill_upgrade 
                    SET remaining_count = MAX(0, remaining_count - ?)
                    WHERE id IN ({placeholders})
                ''', params)

    if 'undo_stack' not in st.session_state:
        st.session_state['undo_stack'] = []
    st.session_state['undo_stack'].append(action)
    return True
