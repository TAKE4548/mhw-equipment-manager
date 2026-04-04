import streamlit as st
from src.database.storage_manager import get_supabase_client, sync_local_to_cloud

def render_auth_component():
    """Renders the login/sync component in the sidebar."""
    if "user" not in st.session_state:
        st.session_state.user = None

    with st.sidebar:
        st.divider()
        st.markdown("### ☁️ クラウド同期 (Cloud Sync)")
        
        # v11-hotfix: Disable for main branch as it is under development
        st.warning("🚧 現在開発中 (Under Development)")
        st.caption("クラウド同期機能は現在開発中です。現在はローカル保存のみご利用いただけます。")
        
        if st.session_state.user is None:
            # Simple Expandable Login Form
            with st.expander("ログイン / 新規登録 (Coming Soon)"):
                st.info("この機能は次回のアップデートで公開予定です。")
                st.text_input("メールアドレス (Email)", key="auth_email", disabled=True)
                st.text_input("パスワード (Password)", type="password", key="auth_pass", disabled=True)
                
                col1, col2 = st.columns(2)
                col1.button("ログイン", use_container_width=True, disabled=True, key="login_btn_disabled")
                col2.button("新規登録", use_container_width=True, disabled=True, key="signup_btn_disabled")
        else:
            # Logged In State (Safeguard)
            st.success(f"✅ ログイン中: {st.session_state.user.email}")
            col1, col2 = st.columns(2)
            col1.button("同期 (Sync)", use_container_width=True, disabled=True, key="sync_btn_disabled")
            if col2.button("ログアウト", use_container_width=True, key="logout_btn"):
                st.session_state.user = None
                st.rerun()

def get_current_user_id():
    """Helper to get the current logged-in user ID or None."""
    if "user" in st.session_state and st.session_state.user:
        return st.session_state.user.id
    return None
