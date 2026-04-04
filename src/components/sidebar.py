import streamlit as st
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import (
    make_cookie_manager,
    boot_from_browser,
    get_cookie_usage_bytes,
    get_debug_info,
    is_logged_in,
)

def render_shared_sidebar():
    """Renders the sidebar with storage status and auth."""
    init_session_state()

    # --- Step 1: Create the cookie manager (renders hidden component in DOM) ---
    # This MUST be called on every run, before any st.stop()
    cookies = make_cookie_manager()
    # Store for use by save_data() later this run
    st.session_state["_cookie_manager"] = cookies

    # --- Step 2: Wait for browser ↔ Streamlit handshake ---
    if not is_logged_in() and not cookies.ready():
        with st.sidebar:
            st.info("⏳ ブラウザストレージを準備中...")
        st.stop()  # Component is already in DOM, browser will respond → auto rerun

    # --- Step 3: Load persisted data ---
    if not is_logged_in():
        boot_from_browser(cookies)

    # --- Step 4: Render sidebar UI ---
    with st.sidebar:
        st.header("⚙️ ストレージ設定")

        if is_logged_in():
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に保存・同期されています。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのブラウザの Cookie に保存されています。")

            # --- Cookie Usage Warning ---
            usage = get_cookie_usage_bytes(cookies)
            if usage > 3000:
                st.warning(
                    f"⚠️ データ容量が上限に近づいています ({usage:,} / 4,096 bytes)。\n\n"
                    "ユーザー登録すると、データがクラウドにバックアップされ、制限なく保存できます。"
                )

        render_auth_component()

        # --- Debug Panel ---
        with st.expander("🔍 デバッグ情報", expanded=True):
            info = get_debug_info(cookies)
            st.write(f"Ready: `{info['ready']}`")
            st.write(f"Cookie 書き込み済み: `{info['cookie_exists']}`")
            st.write(f"Cookie サイズ: `{info['cookie_size_bytes']} bytes`")
            st.write(f"武器: `{info['weapons_count']}件`")
            st.write(f"抽選: `{info['upgrades_count']}件`")
            st.write(f"トラッカー: `{info['trackers_count']}件`")

        st.divider()
        st.caption("MHWs Equipment Manager v8.0 (Encrypted Cookie)")
