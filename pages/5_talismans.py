import streamlit as st
from src.components.sidebar import render_shared_sidebar
from src.components.auth import get_current_user_id
from src.components.common import render_lean_header
from src.components.cards import inject_card_css

# 新規分割したコンポーネントのインポート
from src.components.talismans.state import init_talisman_state
from src.components.talismans.dialogs import skill_dialog_root
from src.components.talismans.form import render_registration_form
from src.components.talismans.list import render_talisman_list

# ページ設定
st.set_page_config(page_title="鑑定護石管理", page_icon="📿", layout="wide")
inject_card_css()
render_shared_sidebar()

# 1. 状態の初期化
init_talisman_state()

# 2. ダイアログの制御 (st.dialog はメインスレッドでの呼び出しが必要)
if st.session_state.get("active_dialog"):
    skill_dialog_root(st.session_state["active_dialog"])

# 3. ヘッダー描画
render_lean_header(
    "鑑定護石管理", 
    "マカ錬金で入手した護石の登録・検索・お気に入り管理を行います。", 
    icon="📿"
)

user_id = get_current_user_id()

# 4. 登録フォームの描画
render_registration_form(user_id)

# 5. 護石一覧の描画
render_talisman_list(user_id)
