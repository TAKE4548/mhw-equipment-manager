import streamlit as st
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import boot_from_browser, get_debug_info, is_logged_in

def render_shared_sidebar():
    """Renders sidebar. No cookie component handshake needed — reads from HTTP headers."""
    init_session_state()
    boot_from_browser()  # reads st.context.cookies instantly, no rerun needed

    with st.sidebar:
        st.header("⚙️ ストレージ設定")

        if is_logged_in():
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に保存されています。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのブラウザに保存されています。")

        with st.expander("🔍 デバッグ情報", expanded=True):
            info = get_debug_info()
            st.write(f"Cookie 書き込み済み: `{info['cookie_exists']}`")
            st.write(f"Cookie サイズ: `{info['cookie_size_bytes']} bytes`")
            st.write(f"武器: `{info['weapons_count']}件`")
            st.write(f"抽選: `{info['upgrades_count']}件`")
            st.write(f"トラッカー: `{info['trackers_count']}件`")

        render_auth_component()
        st.divider()
        st.caption("MHWs Equipment Manager v9.0 (HTML Cookie)")
