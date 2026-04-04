import streamlit as st

def init_session_state():
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
        
    # URL Persistence
    if 'gsheet_url' not in st.session_state:
        url_from_query = st.query_params.get("url", "")
        url_from_secrets = st.secrets.get("spreadsheet_url", "")
        st.session_state['gsheet_url'] = url_from_query or url_from_secrets

init_session_state()

# Navigation setup (v1.55+)
skill_page = st.Page("pages/0_skill_lottery.py", title="スキル抽選結果", icon="⚔️", default=True)
box_page = st.Page("pages/equipment_box.py", title="所有巨戟アーティア一覧", icon="📦")
rein_page = st.Page("pages/reinforcement_registration.py", title="復元強化厳選", icon="✨")

pg = st.navigation([skill_page, box_page, rein_page])
pg.run()
