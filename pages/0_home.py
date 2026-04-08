import streamlit as st
import pandas as pd
import altair as alt
from src.logic.equipment_box import load_equipment, ATTRIBUTE_COLORS
from src.logic.talismans import load_talismans
from src.components.sidebar import render_shared_sidebar
from src.components.cards import inject_card_css
from src.components.auth import get_current_user_id

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
inject_card_css()

# Custom CSS for Premium Portal Look
st.markdown("""
<style>
    .portal-card {
        background: #1e1e1e;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .portal-card:hover {
        border-color: #ffd700;
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.5), 0 0 15px rgba(255,215,0,0.2);
    }
    .portal-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .portal-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #ddd;
    }
    .portal-desc {
        font-size: 0.875rem;
        color: #888;
        margin-top: 0.5rem;
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

# Load data for stats
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

# Weapon Type Ratio Chart
if not eq_df.empty:
    st.markdown("#### 武器種別所持比率")
    type_counts = eq_df['weapon_type'].value_counts().reset_index()
    type_counts.columns = ['Weapon Type', 'Count']
    
    chart = alt.Chart(type_counts).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Weapon Type", type="nominal", legend=alt.Legend(title="武器種")),
        tooltip=["Weapon Type", "Count"]
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("武器がまだ登録されていません。")

st.divider()

# --- Quick Action Grid ---
st.subheader("クイックアクション ⚡")

def card_button(icon, title, desc, page_name):
    """Note: st.button inside columns is the standard way, 
    but for a 'premium' look we can use container + button."""
    if st.button(f"{icon}\n\n{title}\n\n{desc}", key=f"btn_{page_name}", use_container_width=True):
        st.switch_page(page_name)

# Grid Layout
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="portal-card"><div class="portal-icon">📦</div><div class="portal-title">武器台帳</div><div class="portal-desc">所有武器の登録と管理</div></div>', unsafe_allow_html=True)
    if st.button("台帳を開く", key="nav_box", use_container_width=True):
        st.switch_page("pages/equipment_box.py")

with c2:
    st.markdown('<div class="portal-card"><div class="portal-icon">⚔️</div><div class="portal-title">スキル抽選</div><div class="portal-desc">未来の強化シードを確認</div></div>', unsafe_allow_html=True)
    if st.button("抽選管理を開く", key="nav_skill", use_container_width=True):
        st.switch_page("pages/0_skill_lottery.py")

with c3:
    st.markdown('<div class="portal-card"><div class="portal-icon">✨</div><div class="portal-title">復元厳選</div><div class="portal-desc">最適なボーナスを追求</div></div>', unsafe_allow_html=True)
    if st.button("復元厳選を始める", key="nav_rein", use_container_width=True):
        st.switch_page("pages/reinforcement_registration.py")

st.markdown("<br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

with c4:
    st.markdown('<div class="portal-card"><div class="portal-icon">📿</div><div class="portal-title">鑑定護石</div><div class="portal-desc">護石のデータベース管理</div></div>', unsafe_allow_html=True)
    if st.button("護石管理を開く", key="nav_tali", use_container_width=True):
        st.switch_page("pages/5_talismans.py")

with c5:
    st.markdown('<div class="portal-card"><div class="portal-icon">📊</div><div class="portal-title">分析統計</div><div class="portal-desc">データの詳細な可視化</div></div>', unsafe_allow_html=True)
    if st.button("分析画面を表示", key="nav_dash", use_container_width=True):
        st.switch_page("pages/4_analytics_dashboard.py")

with c6:
    # Future / Empty slot for symmetry
    st.markdown('<div class="portal-card"><div class="portal-icon">⚙️</div><div class="portal-title">設定</div><div class="portal-desc">サイドバーより操作可能</div></div>', unsafe_allow_html=True)
    if st.button("サイドバーを確認", key="nav_set", use_container_width=True, disabled=True):
        pass

# --- Footer or Recent Items ---
# (Recent items could be added later when REQ-014 is implemented)
