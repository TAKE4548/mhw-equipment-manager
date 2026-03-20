import streamlit as st
import os

from src.database.sqlite_manager import init_db

def init_session_state():
    if 'undo_stack' not in st.session_state:
        st.session_state['undo_stack'] = []
    if 'redo_stack' not in st.session_state:
        st.session_state['redo_stack'] = []

init_session_state()
init_db()

st.set_page_config(
    page_title="MHWs Equipment Manager",
    page_icon="⚔️",
    layout="wide",
)

st.title("MHWs Equipment Manager ⚔️")
st.sidebar.success("Choose an option from above.")

from src.logic.equipment import get_active_upgrades

st.markdown("""
Welcome to the Monster Hunter Wilds Equipment Manager MVP!

This tool focuses on managing skill upgrade tables for Kyogeki Artia weapons.
""")

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
