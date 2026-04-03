import streamlit as st
import os



def init_session_state():
    if 'undo_stack' not in st.session_state:
        st.session_state['undo_stack'] = []
    if 'redo_stack' not in st.session_state:
        st.session_state['redo_stack'] = []
    
    # URL Persistence logic
    if 'gsheet_url' not in st.session_state:
        # Priority: 1. Query Params, 2. Secrets, 3. Empty
        url_from_query = st.query_params.get("url", "")
        url_from_secrets = st.secrets.get("spreadsheet_url", "")
        st.session_state['gsheet_url'] = url_from_query or url_from_secrets

init_session_state()

st.set_page_config(
    page_title="MHWs Equipment Manager",
    page_icon="⚔️",
    layout="wide",
)

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    url = st.text_input("Google Sheet URL", value=st.session_state['gsheet_url'], help="Paste your Google Sheet URL here.")
    if url != st.session_state['gsheet_url']:
        st.session_state['gsheet_url'] = url
        st.query_params["url"] = url
        st.rerun()
    
    if not st.session_state['gsheet_url']:
        st.warning("Please provide a Google Sheet URL to enable persistence.")
    else:
        st.info("💡 **Tip**: Bookmark this page now! The URL is saved in your browser's address bar so you won't have to re-enter it next time.")

st.title("MHWs Equipment Manager ⚔️")
st.sidebar.success("Choose an option from above.")

from src.logic.equipment import get_active_upgrades

st.markdown("""
Welcome to the Monster Hunter Wilds Equipment Manager MVP!

This tool focuses on managing skill upgrade tables for Kyogeki Artia weapons.
""")

if not st.session_state.get('gsheet_url'):
    st.info("👋 **Setup Required**: Please paste your Google Sheet URL in the **sidebar** to enable data persistence and start tracking upgrades.")
    st.stop()

st.divider()

col_undo, col_redo, _, col_reg = st.columns([1, 1, 8, 2], vertical_alignment="center")
with col_undo:
    if st.button("↩️", help="Undo", disabled=len(st.session_state.get('undo_stack', [])) == 0, use_container_width=True):
        from src.logic.history import undo_last_action
        undo_last_action()
        st.rerun()
with col_redo:
    if st.button("↪️", help="Redo", disabled=len(st.session_state.get('redo_stack', [])) == 0, use_container_width=True):
        from src.logic.history import redo_last_action
        redo_last_action()
        st.rerun()
with col_reg:
    st.page_link("pages/1_register.py", label="新規登録", icon="➕")

st.markdown("<br>", unsafe_allow_html=True)

from src.components.tables import render_active_upgrades
df = get_active_upgrades()
render_active_upgrades(df)
