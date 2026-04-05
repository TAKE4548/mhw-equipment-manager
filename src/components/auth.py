import streamlit as st
from src.database.storage_manager import get_supabase_client, sync_local_to_cloud

def render_auth_component():
    """Renders the login/sync component in the sidebar."""
    # Ensure session state for user is initialized
    if "user" not in st.session_state:
        st.session_state.user = None

    with st.sidebar:
        st.divider()
        
        if st.session_state.user is None:
            st.markdown("### ☁️ クラウド同期 (Cloud Sync)")
            st.caption("ログインすると複数端末での同期とバックアップが可能になります。")
            
            # Simple Expandable Login Form
            with st.expander("ログイン / 新規登録"):
                email = st.text_input("メールアドレス (Email)", key="auth_email")
                password = st.text_input("パスワード (Password)", type="password", key="auth_pass")
                
                col1, col2 = st.columns(2)
                
                if col1.button("ログイン", use_container_width=True):
                    client = get_supabase_client()
                    if not client:
                        st.warning("⚠️ Supabase の設定（URL/Key）が `.streamlit/secrets.toml` に未設定です。")
                    else:
                        with st.spinner("認証中..."):
                            try:
                                # Supabase auth handles login
                                res = client.auth.sign_in_with_password({"email": email, "password": password})
                                if res.user:
                                    st.session_state.user = res.user
                                    
                                    # Persistence: Save session to cookie
                                    if res.session:
                                        from src.database.storage_manager import set_auth_cookie, pull_cloud_to_local
                                        set_auth_cookie(res.session.access_token, res.session.refresh_token)
                                        # Key Fix: Pull cloud data into local memory immediately after login
                                        pull_cloud_to_local()
                                    
                                    # Clear logical caches and state
                                    from src.utils.cache_utils import clear_all_logic_caches
                                    clear_all_logic_caches()
                                    st.session_state['undo_stack'] = []
                                    st.session_state['redo_stack'] = []
                                    st.session_state['logging_out'] = False # Reset if it was set
                                    st.toast("✅ ログイン成功", icon="🎉")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ ログイン失敗: {e}")

                if col2.button("新規登録", use_container_width=True):
                    client = get_supabase_client()
                    if not client:
                        st.warning("⚠️ Supabase の設定が未設定です。")
                    else:
                        with st.spinner("登録処理中..."):
                            try:
                                client.auth.sign_up({"email": email, "password": password})
                                st.info("✉️ 確認メールを送信しました。リンクをクリックして承認後にログインしてください。")
                            except Exception as e:
                                st.error(f"❌ 登録失敗: {e}")
        else:
            # Logged In State
            st.success(f"✅ ログイン中: {st.session_state.user.email}")
            
            col1, col2 = st.columns(2)
            if col1.button("同期 (Sync)", use_container_width=True):
                sync_local_to_cloud()
                st.info("🔃 同期完了")
                
            if col2.button("ログアウト", use_container_width=True):
                # Key Fix: Set logging_out flag to prevent auto-restore on rerun
                st.session_state['logging_out'] = True
                st.session_state.user = None
                
                # Reset memory state: Force re-initialization from local browser cookie
                from src.database.storage_manager import set_auth_cookie, MANAGED_TABLES
                import pandas as pd
                st.session_state['mhw_ready'] = False
                st.session_state['mhw_data'] = {t: pd.DataFrame() for t in MANAGED_TABLES}
                
                # Clear auth cookie
                set_auth_cookie("", "")
                
                # Clear logical caches and state
                from src.utils.cache_utils import clear_all_logic_caches
                clear_all_logic_caches()
                st.session_state['undo_stack'] = []
                st.session_state['redo_stack'] = []
                st.rerun()

def get_current_user_id():
    """
    Helper to get the current logged-in user ID.
    Returns 'local' if no user is authenticated to maintain a consistent logic signature.
    """
    if "user" in st.session_state and st.session_state.user:
        return st.session_state.user.id
    return "local"
