import streamlit as st
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import boot_from_browser, init_memory_storage

def render_shared_sidebar():
    """
    Renders the shared sidebar and performs the one-time browser boot handshake.
    The LocalStorage component must be rendered on every page load to communicate
    with the browser.
    """
    init_session_state()
    init_memory_storage()
    
    # --- Boot Handshake ---
    # Call boot_from_browser() on every run until it succeeds.
    # LocalStorage renders its hidden component here, enabling browser communication.
    boot_from_browser()

    with st.sidebar:
        st.header("⚙️ ストレージ設定")
        
        if not st.session_state.get('mhw_ready') and not is_cloud_mode():
            st.warning("⏳ データを読み込み中...")

        if "user" in st.session_state and st.session_state.user:
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に保存されます。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのブラウザに保存されています。")
        
        render_auth_component()
        
        st.divider()
        st.caption("MHWs Equipment Manager v5.1 (LocalStorage)")

def is_cloud_mode():
    return "user" in st.session_state and st.session_state.user is not None
