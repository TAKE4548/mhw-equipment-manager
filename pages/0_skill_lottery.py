import streamlit as st
from src.logic.master import get_master_data
from src.components.sidebar import render_shared_sidebar
from src.components.auth import get_current_user_id
from src.components.common import render_lean_header

# 新規分割したコンポーネントのインポート
from src.components.lottery.state import init_lottery_state
from src.components.lottery.form import render_registration_form
from src.components.lottery.list import render_tracker_list

# 1. ページ設定
st.set_page_config(page_title="スキル抽選管理", layout="wide")
render_shared_sidebar()

# 2. 状態の初期化
init_lottery_state()

# 3. ヘッダー描画
render_lean_header(
    "スキル抽選結果", 
    "スキル抽選の順序を確認し、武器へ割り当てます。"
)

user_id = get_current_user_id()
master = get_master_data()

# 4. 登録フォーム
render_registration_form(master, user_id)

# 5. 抽選結果一覧
render_tracker_list(master, user_id)
