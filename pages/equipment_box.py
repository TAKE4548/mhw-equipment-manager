import streamlit as st
from src.logic.master import get_master_data
from src.components.auth import get_current_user_id
from src.components.sidebar import render_shared_sidebar
from src.components.cards import inject_card_css
from src.components.common import render_lean_header

# 新規分割したコンポーネントのインポート
from src.components.box.state import init_box_state, check_data_ready
from src.components.box.form import render_registration_section
from src.components.box.list import render_equipment_list

# 1. ページ設定
st.set_page_config(page_title="所持武器台帳", page_icon="📦", layout="wide")
inject_card_css()
render_shared_sidebar()

# 2. 状態の初期化とデータ準備確認
init_box_state()
if not check_data_ready():
    st.stop()

# 3. ヘッダー描画
render_lean_header(
    "所持武器台帳", 
    "所持武器の登録・管理および強化状況の確認を行います。", 
    icon="🎒"
)

user_id = get_current_user_id()
master = get_master_data()

# 4. 登録フォーム
render_registration_section(master, user_id)

# 5. 武器一覧
render_equipment_list(master, user_id)
