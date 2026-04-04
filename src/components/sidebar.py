import streamlit as st
import json
import pandas as pd
from streamlit_javascript import st_javascript
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import init_memory_storage

def render_shared_sidebar():
    """
    Ultimate JS Handshake Sidebar.
    Directly fetches all mhw_ data from browser localStorage via JS.
    """
    init_session_state()
    init_memory_storage()
    
    # 1. Global JS Fetch Handshake
    # We use a single JS call to get all MHW-related persistent data
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
    
    # st_javascript returns the result of the JS execution
    all_data_json = st_javascript(js_code)
    
    # 2. Populate Memory Storage if not already done and data arrived
    if all_data_json and isinstance(all_data_json, str) and not st.session_state.get('mhw_boot_complete'):
        try:
            raw_items = json.loads(all_data_json)
            # Map "mhw_weapons" -> "weapons"
            for full_key, val in raw_items.items():
                if full_key.startswith('mhw_'):
                    short_key = full_key[4:]
                    try:
                        data = json.loads(val) if isinstance(val, str) else val
                        st.session_state['mhw_memory_storage'][short_key] = pd.DataFrame(data)
                    except:
                        st.session_state['mhw_memory_storage'][short_key] = pd.DataFrame()
            
            # Ensure managed keys exist even if not in localStorage yet
            for k in ["weapons", "trackers", "upgrades"]:
                if k not in st.session_state['mhw_memory_storage']:
                    st.session_state['mhw_memory_storage'][k] = pd.DataFrame()
                    
            st.session_state['mhw_boot_complete'] = True
        except:
            pass # Wait for valid JSON

    with st.sidebar:
        st.header("⚙️ ストレージ設定")
        
        # Display Loading status if boot is not complete
        if not st.session_state.get('mhw_boot_complete') and not st.session_state.get('user'):
            st.warning("⏳ ブラウザからデータを読み込み中...")
        
        # Mode display
        if "user" in st.session_state and st.session_state.user:
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に安全に保存され、端末間で同期されます。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのブラウザにのみ保存されています。バックアップが必要な場合はログインしてください。")
        
        # Authentication & Sync Component
        render_auth_component()
        
        st.divider()
        st.caption("MHWs Equipment Manager v4.0 (JavaScript Handshake)")
