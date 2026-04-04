import streamlit as st
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from streamlit_local_storage import LocalStorage

def render_shared_sidebar():
    """Renders a shared sidebar with Hybrid Storage (Local/Cloud) management."""
    # Ensure session state is always initialized
    init_session_state()
    
    # Initialize LocalStorage component ONCE and store in session state
    if 'ls_handler' not in st.session_state:
        st.session_state['ls_handler'] = LocalStorage()
    
    with st.sidebar:
        st.header("⚙️ ストレージ設定")
        
        # Mode display
        if "user" in st.session_state and st.session_state.user:
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に安全に保存され、端末間で同期されます。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのブラウザにのみ保存されています。バックアップが必要な場合はログインしてください。")
        
        # Authentication & Sync Component
        render_auth_component()
        
        st.divider()
        st.caption("MHWs Equipment Manager v3.2 (Stable Handshake)")
