import streamlit as st
import json
import pandas as pd
from streamlit_javascript import st_javascript
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import init_memory_storage

def render_shared_sidebar():
    """
    Ultimate JS Handshake Sidebar (Phase 10 - Anti-Freeze).
    Uses a timeout mechanism to ensure the UI is unblocked.
    """
    init_session_state()
    init_memory_storage()
    
    # 1. Global JS Fetch Handshake with Timeout mechanism
    if not st.session_state.get('mhw_boot_complete'):
        # Handshake Timeout/Attempt Counter
        if 'mhw_boot_attempts' not in st.session_state:
            st.session_state['mhw_boot_attempts'] = 0
        st.session_state['mhw_boot_attempts'] += 1
        
        # Robust One-Liner JS script
        js_code = "JSON.stringify(Object.assign({}, window.localStorage))"
        all_data_json = st_javascript(js_code)
        
        # We wait for a valid JSON string result from JavaScript
        if all_data_json and isinstance(all_data_json, str) and all_data_json != "0":
            try:
                raw_items = json.loads(all_data_json)
                for k in ["weapons", "trackers", "upgrades"]:
                    full_key = f"mhw_{k}"
                    val = raw_items.get(full_key)
                    if val and val != "null":
                        try:
                            # Handle potential double-escaped JSON string
                            data = json.loads(val) if isinstance(val, str) else val
                            st.session_state['mhw_memory_storage'][k] = pd.DataFrame(data)
                        except:
                            st.session_state['mhw_memory_storage'][k] = pd.DataFrame()
                    else:
                        st.session_state['mhw_memory_storage'][k] = pd.DataFrame()
                
                st.session_state['mhw_boot_complete'] = True
            except:
                pass # Still waiting
                
        # 2. FORCE UNBLOCK: If JS is taking too long (e.g. 5 attempts), proceed anyway
        elif st.session_state['mhw_boot_attempts'] > 10: # Increased threshold for safety
             # Ensure managed keys exist so we don't crash
             for k in ["weapons", "trackers", "upgrades"]:
                 if k not in st.session_state['mhw_memory_storage']:
                     st.session_state['mhw_memory_storage'][k] = pd.DataFrame()
             st.session_state['mhw_boot_complete'] = True

    with st.sidebar:
        st.header("⚙️ ストレージ設定")
        
        boot_complete = st.session_state.get('mhw_boot_complete', False)
        if not boot_complete and not st.session_state.get('user'):
            st.warning("⏳ データを同期中...")
        
        # Mode display
        if "user" in st.session_state and st.session_state.user:
            st.info("🌐 **モード: クラウド同期**")
        else:
            st.success("💻 **モード: ローカル保存**")
        
        # Authentication & Sync Component
        render_auth_component()
        
        st.divider()
        st.caption("MHWs Equipment Manager v4.2 (Anti-Freeze)")
