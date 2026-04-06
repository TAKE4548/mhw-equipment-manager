import streamlit as st
import sys
import os

# Ensure the root directory is in the path for src imports (Robust absolute path resolution)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.utils.session import init_session_state

# Always initialize session at the entry point
init_session_state()

# Navigation setup (v1.55+)
# Navigation setup (v1.55+)
home_page = st.Page("pages/4_analytics_dashboard.py", title="Home", icon="🏠", default=True)
box_page = st.Page("pages/equipment_box.py", title="所有巨戟アーティア一覧", icon="📦")
skill_page = st.Page("pages/0_skill_lottery.py", title="スキル抽選結果", icon="⚔️")
rein_page = st.Page("pages/reinforcement_registration.py", title="復元強化厳選", icon="✨")
talisman_page = st.Page("pages/5_talismans.py", title="鑑定護石管理", icon="📿")

pg = st.navigation([home_page, box_page, skill_page, rein_page, talisman_page])
pg.run()
