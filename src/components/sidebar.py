import streamlit as st
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import (
    boot_from_browser, 
    persist_to_browser,
    get_debug_info, 
    is_logged_in
)
from src.utils.i18n import t

def render_shared_sidebar():
    """Renders the common sidebar and manages persistent sync."""
    init_session_state()
    boot_from_browser()

    with st.sidebar:
        st.header(t("SIDEBAR.HEADER"))

        if is_logged_in():
            st.info(t("SIDEBAR.MODE_CLOUD"))
        else:
            st.success(t("SIDEBAR.MODE_LOCAL"))

        # --- Debug Display ---
        info = get_debug_info()
        with st.sidebar.expander(t("SIDEBAR.DEBUG_HEADER"), expanded=False):
            st.write(f"{t('SIDEBAR.DEBUG_COOKIE_EXISTS')}: `{info['cookie_exists']}`")
            st.write(f"{t('SIDEBAR.DEBUG_NEEDS_PERSIST')}: `{info['needs_persist']}`")
            st.write(f"{t('SIDEBAR.DEBUG_COOKIE_SIZE')}: `{info['cookie_size_bytes']} bytes`")
            st.write(t("SIDEBAR.DEBUG_COUNTS", 
                       weapons=info['weapons_count'], 
                       upgrades=info['upgrades_count'], 
                       trackers=info['trackers_count']))

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
