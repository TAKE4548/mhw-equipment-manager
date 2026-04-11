import streamlit as st
import sys
import os

# Ensure the root directory is in the path for src imports (Robust absolute path resolution)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.utils.session import init_session_state
from src.utils.i18n import t

# Always initialize session at the entry point
init_session_state()

# Navigation setup (v1.55+)
home_page = st.Page("pages/0_home.py", title=t("NAV.HOME"), default=True)
box_page = st.Page("pages/equipment_box.py", title=t("NAV.BOX"))
skill_page = st.Page("pages/0_skill_lottery.py", title=t("NAV.SKILL"))
rein_page = st.Page("pages/reinforcement_registration.py", title=t("NAV.REIN"))
talisman_page = st.Page("pages/5_talismans.py", title=t("NAV.TALI"))
dashboard_page = st.Page("pages/4_analytics_dashboard.py", title=t("NAV.DASH"))

pg = st.navigation({
    t("NAV.GROUP.PORTAL"): [home_page],
    t("NAV.GROUP.EQUIP"): [box_page, talisman_page],
    t("NAV.GROUP.LOTTERY"): [skill_page, rein_page],
    t("NAV.GROUP.OTHER"): [dashboard_page]
})
pg.run()
