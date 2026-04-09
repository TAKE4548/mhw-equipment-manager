import streamlit as st
from src.logic.master import get_master_data
from src.logic.equipment_box import load_equipment
from src.components.auth import get_current_user_id
from src.components.sidebar import render_shared_sidebar
from src.components.cards import inject_card_css
from src.components.common import render_lean_header

# 新規分割したコンポーネントのインポート
from src.components.reinforcement.form import render_registration_section
from src.components.reinforcement.list import render_active_tracker_list

# ページ設定
st.set_page_config(page_title="復元強化厳選", page_icon="✨", layout="wide")
inject_card_css()
render_shared_sidebar()

# 1. ヘッダー描画
render_lean_header(
    "復元強化厳選", 
    "武器ごとの復元ボーナス進行状況をトラッキングし、抽選結果を反映します。", 
    icon="✨"
)

user_id = get_current_user_id()
eq_df = load_equipment(user_id)

if eq_df.empty:
    st.warning("まず Equipment Box に武器を登録してください。")
    st.stop()

master = get_master_data()

# 2. 登録セクション
# セッション状態 tracker_reg_w_id が設定されている場合に自動で展開されるように制御
with st.expander("✨ 新しい強化抽選を登録する", expanded=st.session_state.get("tracker_reg_w_id") is not None):
    render_registration_section(master, eq_df, user_id)

# 3. トラッキング中のリスト表示
render_active_tracker_list(master, eq_df, user_id)
