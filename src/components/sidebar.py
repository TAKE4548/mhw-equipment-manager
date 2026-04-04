import streamlit as st
from src.components.auth import render_auth_component
from src.utils.session import init_session_state

def render_shared_sidebar():
    """Renders the shared sidebar."""
    init_session_state()
    
    with st.sidebar:
        st.header("⚙️ ストレージ設定")
        
        if "user" in st.session_state and st.session_state.user:
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に保存されます。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのPCの `data/` フォルダに保存されています。")
        
        render_auth_component()
        
        st.divider()
        st.caption("MHWs Equipment Manager v5.0 (File Storage)")
