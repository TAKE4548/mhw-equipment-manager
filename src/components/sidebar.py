import streamlit as st
import json
import pandas as pd
from streamlit_javascript import st_javascript
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import init_memory_storage

def render_shared_sidebar():
    """
    Ultimate JS Handshake Sidebar (Phase 9 - Final Stability).
    Ensures memory storage is populated once and never lost during session.
    """
    init_session_state()
    init_memory_storage()
    
    # 1. Global JS Fetch Handshake
    # Only perform the pull from browser if we haven't successfully done it yet
    if not st.session_state.get('mhw_boot_complete'):
        js_code = """
        (function() {
            const items = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith('mhw_')) {
                    items[key] = localStorage.getItem(key);
                }
            }
            return JSON.stringify(items);
        })()
        """
        all_data_json = st_javascript(js_code)
        
        # We wait for a valid JSON string result from JavaScript
        if all_data_json and isinstance(all_data_json, str):
            try:
                raw_items = json.loads(all_data_json)
                
                # Check for "null" values or empty results
                for k in ["weapons", "trackers", "upgrades"]:
                    full_key = f"mhw_{k}"
                    val = raw_items.get(full_key)
                    
                    if val and val != "null":
                        try:
                            # Handle potential double-escaped JSON string from some browsers
                            data = json.loads(val) if isinstance(val, str) else val
                            st.session_state['mhw_memory_storage'][k] = pd.DataFrame(data)
                        except:
                            st.session_state['mhw_memory_storage'][k] = pd.DataFrame()
                    else:
                        # Key missing in browser? Use empty DF.
                        st.session_state['mhw_memory_storage'][k] = pd.DataFrame()
                
                # Flag boot as complete so we don't overwrite memory from browser again
                st.session_state['mhw_boot_complete'] = True
            except:
                pass # Still waiting for valid JSON

    with st.sidebar:
        st.header("⚙️ ストレージ設定")
        
        # Display Loading status ONLY during the very first boot check
        boot_complete = st.session_state.get('mhw_boot_complete', False)
        if not boot_complete and not st.session_state.get('user'):
            st.warning("⏳ データを同期中...")
        
        # Mode display
        if "user" in st.session_state and st.session_state.user:
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に安全に保存されます。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのブラウザに保存されています。")
        
        # Authentication & Sync Component
        render_auth_component()
        
        st.divider()
        st.caption("MHWs Equipment Manager v4.1 (Stable Persistence)")
