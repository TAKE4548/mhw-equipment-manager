import streamlit as st
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import (
    boot_from_browser, 
    persist_to_browser,
    get_debug_info, 
    is_logged_in
)

def render_shared_sidebar():
    """Renders the common sidebar and manages persistent sync."""
    init_session_state()
    boot_from_browser()

    with st.sidebar:
        st.header("⚙️ ストレージ設定")

        if is_logged_in():
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に保存されています。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのブラウザに保存されています。")

        # --- Debug Display ---
        info = get_debug_info()
        with st.expander("🔍 デバッグ情報", expanded=True):
            st.write(f"Cookie 書き込み済み: `{info['cookie_exists']}`")
            st.write(f"再保存リクエスト: `{info['needs_persist']}`")
            st.write(f"Cookie サイズ: `{info['cookie_size_bytes']} bytes`")
            st.write(f"武器: `{info['weapons_count']}件 / 抽選: `{info['upgrades_count']}件` / トラッカー: `{info['trackers_count']}件`")

        render_auth_component()
        st.divider()
        st.caption("MHWs Equipment Manager v10.0 (Deferred Sync)")

    # --- V10 Deferred Persistence Logic ---
    # We call persist_to_browser here so the <script> tag is 
    # part of the very last HTML sent to the client in this run.
    # This prevents st.rerun() from wiping out the script.
    if st.session_state.get("needs_persist", False):
        persist_to_browser()
        st.session_state["needs_persist"] = False
