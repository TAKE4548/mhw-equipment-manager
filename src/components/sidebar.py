import streamlit as st
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import boot_from_browser

def render_shared_sidebar():
    """
    Renders the shared sidebar.
    boot_from_browser() reads cookies instantly — no spinner, no freeze.
    """
    init_session_state()
    
    # Reads from st.context.cookies immediately. No rerun needed.
    boot_from_browser()

    with st.sidebar:
        st.header("⚙️ ストレージ設定")

        if "user" in st.session_state and st.session_state.user:
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に保存されます。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのブラウザの Cookie に保存されています。")

        render_auth_component()

        st.divider()
        st.caption("MHWs Equipment Manager v6.0 (Cookie Storage)")
