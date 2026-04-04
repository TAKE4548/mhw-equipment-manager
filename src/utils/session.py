import streamlit as st

def init_session_state():
    """Initializes all session state variables to prevent AttributeErrors."""
    # Skill Selection history
    if 'undo_stack' not in st.session_state:
        st.session_state['undo_stack'] = []
    if 'redo_stack' not in st.session_state:
        st.session_state['redo_stack'] = []
    
    # Reinforcement (Restoration) history
    if 'history_undo' not in st.session_state:
        st.session_state['history_undo'] = []
    if 'history_redo' not in st.session_state:
        st.session_state['history_redo'] = []
        
    # Persistent weapon selection for registration
    if 'tracker_reg_w_id' not in st.session_state:
        st.session_state.tracker_reg_w_id = None
        
    # User session for Hybrid Storage
    if 'user' not in st.session_state:
        st.session_state.user = None
