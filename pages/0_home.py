import streamlit as st
from src.logic.equipment_box import load_equipment
from src.logic.talismans import load_talismans
from src.components.sidebar import render_shared_sidebar
from src.components.cards import inject_card_css
from src.components.auth import get_current_user_id
from src.utils.i18n import t

st.set_page_config(page_title=t("NAV.HOME"), layout="wide")
inject_card_css()

# Safety First: Simplified Styling for st.button
st.markdown("""
<style>
    /* Scoped to main content to avoid sidebar regression */
    [data-testid="stMain"] [data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {
        height: 100px !important;
        background-color: #262626 !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        color: #ddd !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }
    
    [data-testid="stMain"] [data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:hover {
        border-color: #ffd700 !important;
        background-color: #333 !important;
        color: #fff !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }

    /* Deactive State for System Settings */
    button[key*="go_set"] {
        filter: grayscale(100%) !important;
        opacity: 0.2 !important;
        pointer-events: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Render shared sidebar
render_shared_sidebar()

# Wait for localStorage data to be available
if not st.session_state.get('mhw_ready') and not st.session_state.get('user'):
    st.info(t("HOME.LOADING"))
    st.stop()

user_id = get_current_user_id()

# --- Header Section ---
st.markdown(f"### {t('HOME.HEADER')}")
st.markdown(f"<p style='font-size:0.9rem; color:#888; margin-top:-10px;'>{t('HOME.DESC')}</p>", unsafe_allow_html=True)
st.markdown('<div class="lean-sep"></div>', unsafe_allow_html=True)

# --- Statistics Summary Section ---
st.subheader(t("HOME.STATS_HEADER"))

# Load data for stats
eq_df = load_equipment(user_id)
tali_df = load_talismans(user_id)

col_stat1, col_stat2, col_stat3 = st.columns(3)

with col_stat1:
    st.metric(t("HOME.STATS_WEAPONS"), len(eq_df))
with col_stat2:
    st.metric(t("HOME.STATS_TALISMANS"), len(tali_df))
with col_stat3:
    fav_count = (tali_df['is_favorite'].sum() if not tali_df.empty else 0)
    st.metric(t("HOME.STATS_FAVORITES"), fav_count)

st.markdown('<div class="lean-sep"></div>', unsafe_allow_html=True)

# --- Quick Action Grid (Simplified for Stability) ---
st.subheader(t("HOME.QUICK_HEADER"))

c1, c2, c3 = st.columns(3)

with c1:
    if st.button(t("HOME.ACTION_BOX"), key="go_box", use_container_width=True):
        st.switch_page("pages/equipment_box.py")

with c2:
    if st.button(t("HOME.ACTION_SKILL"), key="go_skill", use_container_width=True):
        st.switch_page("pages/0_skill_lottery.py")

with c3:
    if st.button(t("HOME.ACTION_REIN"), key="go_rein", use_container_width=True):
        st.switch_page("pages/reinforcement_registration.py")

st.markdown("<br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

with c4:
    if st.button(t("HOME.ACTION_TALI"), key="go_tali", use_container_width=True):
        st.switch_page("pages/5_talismans.py")

with c5:
    if st.button(t("HOME.ACTION_DASH"), key="go_dash", use_container_width=True):
        st.switch_page("pages/4_analytics_dashboard.py")

with c6:
    # Stylized as deactive via CSS (grayscale + opacity)
    if st.button(t("HOME.ACTION_SETTINGS"), key="go_set", use_container_width=True, disabled=True):
        pass

st.markdown('<div class="lean-sep"></div>', unsafe_allow_html=True)
st.markdown("<div style='text-align: right; color: #444; font-size: 0.8rem;'>MHWs Equipment Manager v10.0</div>", unsafe_allow_html=True)
