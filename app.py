import streamlit as st
import sys
import os

# Ensure the root directory is in the path for src imports
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.utils.session import init_session_state

# Always initialize session at the entry point
init_session_state()

# Navigation setup (v1.55+)
skill_page = st.Page("pages/0_skill_lottery.py", title="スキル抽選結果", icon="⚔️", default=True)
box_page = st.Page("pages/equipment_box.py", title="所有巨戟アーティア一覧", icon="📦")
rein_page = st.Page("pages/reinforcement_registration.py", title="復元強化厳選", icon="✨")

pg = st.navigation([skill_page, box_page, rein_page])
pg.run()
