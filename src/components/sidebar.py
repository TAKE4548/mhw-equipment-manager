import streamlit as st

def render_shared_sidebar():
    """Renders a shared sidebar with Google Sheet URL configuration."""
    with st.sidebar:
        st.header("⚙️ 設定 (Settings)")
        
        # URL Logic
        if 'gsheet_url' not in st.session_state:
            url_from_query = st.query_params.get("url", "")
            url_from_secrets = st.secrets.get("spreadsheet_url", "")
            st.session_state['gsheet_url'] = url_from_query or url_from_secrets

        url = st.text_input(
            "スプレッドシート URL", 
            value=st.session_state.get('gsheet_url', ''), 
            help="Google スプレッドシートの URL を貼り付けてください。"
        )
        
        if url != st.session_state.get('gsheet_url'):
            st.session_state['gsheet_url'] = url
            st.query_params["url"] = url
            st.rerun()
            
        if not st.session_state.get('gsheet_url'):
            st.warning("⚠️ スプレッドシートの URL を入力してください。")
        else:
            st.success("✅ 接続済み")
            st.info("💡 ヒント: この画面をブックマークしておくと、次回から URL の再入力が不要になります。")
        
        st.divider()
        st.caption("MHWs Equipment Manager v2.11")
