import streamlit as st
import json
import pandas as pd
from src.components.auth import render_auth_component
from src.utils.session import init_session_state
from src.database.storage_manager import init_memory_storage
from streamlit_local_storage import LocalStorage

def render_shared_sidebar():
    """
    Renders a shared sidebar and handles the Global Memory Sync (Handshake).
    This part ensures data is loaded from browser into memory once per session.
    """
    # 1. Base Session Init
    init_session_state()
    init_memory_storage()
    
    # 2. Central LocalStorage Handler Init
    if 'ls_handler' not in st.session_state:
        st.session_state['ls_handler'] = LocalStorage()
    
    ls = st.session_state['ls_handler']
    
    # 3. Initial Boot Handshake (Browser -> Memory)
    # We do this until all managed keys are loaded into session storage
    managed_keys = ["weapons", "trackers", "upgrades"]
    all_ready = True
    
    for key in managed_keys:
        if key not in st.session_state['mhw_memory_storage']:
            full_key = f"mhw_{key}"
            val = ls.getItem(full_key)
            
            if val is not None:
                # Browser responded!
                if val == "null" or not val:
                    st.session_state['mhw_memory_storage'][key] = pd.DataFrame()
                else:
                    try:
                        # Handle both JSON string and dict return depending on component behavior
                        data = json.loads(val) if isinstance(val, str) else val
                        st.session_state['mhw_memory_storage'][key] = pd.DataFrame(data)
                    except:
                        st.session_state['mhw_memory_storage'][key] = pd.DataFrame()
            else:
                all_ready = False # Still waiting for at least one key
    
    with st.sidebar:
        st.header("⚙️ ストレージ設定")
        
        # Display Loading status if not ready
        if not all_ready and not st.session_state.get('user'):
            st.warning("⏳ ブラウザからデータを読み込み中...")
            # We don't stop here, we let the inner pages handle the stop if they need data
        
        # Mode display
        if "user" in st.session_state and st.session_state.user:
            st.info("🌐 **モード: クラウド同期**\n\nデータは Supabase に安全に保存され、端末間で同期されます。")
        else:
            st.success("💻 **モード: ローカル保存**\n\nデータはこのブラウザにのみ保存されています。バックアップが必要な場合はログインしてください。")
        
        # Authentication & Sync Component
        render_auth_component()
        
        st.divider()
        st.caption("MHWs Equipment Manager v3.3 (Memory-First)")
