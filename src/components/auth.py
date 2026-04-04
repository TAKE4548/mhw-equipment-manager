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
                    if client:
                        try:
                            # Supabase auth handles login
                            res = client.auth.sign_in_with_password({"email": email, "password": password})
                            st.session_state.user = res.user
                            # After login, trigger sync from local to cloud
                            sync_local_to_cloud()
                            st.success("ログインしました！同期を開始します。")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ ログイン失敗: {e}")
                    else:
                        st.warning("⚠️ Supabase の設定（URL/Key）が未完了です。")

                if col2.button("新規登録", use_container_width=True):
                    client = get_supabase_client()
                    if client:
                        try:
                            client.auth.sign_up({"email": email, "password": password})
                            st.info("✉️ 確認メールを送信しました。リンクをクリックして承認後にログインしてください。")
                        except Exception as e:
                            st.error(f"❌ 登録失敗: {e}")
                    else:
                        st.warning("⚠️ Supabase の設定が未完了です。")
        else:
            # Logged In State
            st.success(f"✅ ログイン中: {st.session_state.user.email}")
            
            col1, col2 = st.columns(2)
            if col1.button("同期 (Sync)", use_container_width=True):
                sync_local_to_cloud()
                st.info("🔃 同期完了")
                
            if col2.button("ログアウト", use_container_width=True):
                st.session_state.user = None
                st.rerun()

def get_current_user_id():
    """Helper to get the current logged-in user ID or None."""
    if "user" in st.session_state and st.session_state.user:
        return st.session_state.user.id
    return None
