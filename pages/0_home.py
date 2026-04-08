import streamlit as st
from src.logic.equipment_box import load_equipment
from src.logic.talismans import load_talismans
from src.components.sidebar import render_shared_sidebar
from src.components.cards import inject_card_css
from src.components.auth import get_current_user_id

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
inject_card_css()

# Custom CSS for "Button-as-Card" UI
st.markdown("""
<style>
    /* Style EVERY button in the Quick Action grid to look like a card */
    [data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {
        height: 180px !important;
        background-color: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        color: #eee !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
        white-space: pre-wrap !important;
        line-height: 1.4 !important;
        font-family: inherit !important;
        padding: 20px !important;
    }
    
    [data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:hover {
        border-color: #ffd700 !important;
        background-color: #222 !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5), 0 0 15px rgba(255,215,0,0.1) !important;
        color: #fff !important;
    }

    [data-testid="stHorizontalBlock"] div[data-testid="stButton"] button p {
        font-size: 1rem !important;
        margin: 0 !important;
    }

    /* Icon resizing inside button text */
    .btn-icon {
        font-size: 2.5rem !important;
        display: block;
        margin-bottom: 0.5rem;
    }
    .btn-title {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        display: block;
    }
    .btn-desc {
        font-size: 0.8rem !important;
        color: #888 !important;
        display: block;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Render shared sidebar
render_shared_sidebar()

# Wait for localStorage data to be available
if not st.session_state.get('mhw_ready') and not st.session_state.get('user'):
    st.info("⏳ データを読み込み中...")
    st.stop()

user_id = get_current_user_id()

# --- Header Section ---
st.title("MHW Equipment Manager 💎")
st.markdown("### 巨戟アーティア武器・鑑定護石 統合管理ポータル")
st.divider()

# --- Statistics Summary Section ---
st.subheader("現在のステータス 📊")

# Load data for stats (Counts only for slim performance and simpler UI)
eq_df = load_equipment(user_id)
tali_df = load_talismans(user_id)

col_stat1, col_stat2, col_stat3 = st.columns(3)

with col_stat1:
    st.metric("所持武器合計", len(eq_df))
with col_stat2:
    st.metric("登録護石合計", len(tali_df))
with col_stat3:
    fav_count = (tali_df['is_favorite'].sum() if not tali_df.empty else 0)
    st.metric("お気に入り護石", fav_count)

st.divider()

# --- Quick Action Grid (Large Integrated Buttons) ---
st.subheader("クイックアクション ⚡")
st.info("カードをクリックすると各ページへ移動します。")

# Label contents with pseudo-classes for styling (standard text with formatting)
# Note: Streamlit button labels don't support HTML, but we can style them with CSS
# We use a combined string and rely on white-space: pre-wrap and line-height.

c1, c2, c3 = st.columns(3)

# Row 1
with c1:
    if st.button("📦\n所持武器台帳\n所有武器の登録と管理", key="go_box", use_container_width=True):
        st.switch_page("pages/equipment_box.py")

with c2:
    if st.button("⚔️\nスキル抽選管理\n未来の強化シードを確認", key="go_skill", use_container_width=True):
        st.switch_page("pages/0_skill_lottery.py")

with c3:
    if st.button("✨\n復元強化厳選\n最適なボーナスを追求", key="go_rein", use_container_width=True):
        st.switch_page("pages/reinforcement_registration.py")

st.markdown("<br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

# Row 2
with c4:
    if st.button("📿\n鑑定護石管理\n護石のデータベース管理", key="go_tali", use_container_width=True):
        st.switch_page("pages/5_talismans.py")

with c5:
    if st.button("📊\n分析統計\nデータの詳細な可視化", key="go_dash", use_container_width=True):
        st.switch_page("pages/4_analytics_dashboard.py")

with c6:
    if st.button("⚙️\nシステム設定\n(サイドバーより操作可能)", key="go_set", use_container_width=True, disabled=True):
        pass

# Optional: Add footer note
st.divider()
st.markdown("<div style='text-align: right; color: #444; font-size: 0.8rem;'>MHWs Equipment Manager v10.0 (Deferred Sync)</div>", unsafe_allow_html=True)
