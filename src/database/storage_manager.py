import streamlit as st
import pandas as pd
import json
from supabase import create_client, Client
from streamlit_local_storage import LocalStorage

# --- The ONE localStorage key ---
MHW_STORAGE_KEY = "mhw_all_data"

# Table names
MANAGED_TABLES = ["weapons", "trackers", "upgrades"]

# --- Supabase ---

def get_supabase_client() -> Client:
    try:
        url = st.secrets["connections"]["supabase"]["url"]
        key = st.secrets["connections"]["supabase"]["key"]
        return create_client(url, key)
    except Exception:
        return None

def is_logged_in() -> bool:
    return "user" in st.session_state and st.session_state.user is not None

# --- Memory Cache ---

def init_memory_storage():
    if 'mhw_data' not in st.session_state:
        st.session_state['mhw_data'] = {t: pd.DataFrame() for t in MANAGED_TABLES}
    if 'mhw_ready' not in st.session_state:
        st.session_state['mhw_ready'] = False
    if 'mhw_ls' not in st.session_state:
        st.session_state['mhw_ls'] = LocalStorage()

def get_ls() -> LocalStorage:
    """Returns the singleton LocalStorage instance."""
    init_memory_storage()
    return st.session_state['mhw_ls']

# --- Boot Handshake: read ALL data from browser in one shot ---

def boot_from_browser():
    """
    Called once per session. Reads all data from localStorage into memory.
    Returns True if successful, False if still waiting.
    """
    init_memory_storage()
    
    if st.session_state['mhw_ready']:
        return True  # Already loaded
    
    ls = get_ls()
    raw = ls.getItem(MHW_STORAGE_KEY)
    
    if raw is not None:
        # Browser responded (raw may be a dict, list, or string)
        try:
            if isinstance(raw, str):
                data = json.loads(raw)
            elif isinstance(raw, dict):
                data = raw
            else:
                data = {}
            
            for t in MANAGED_TABLES:
                records = data.get(t, [])
                st.session_state['mhw_data'][t] = pd.DataFrame(records)
        except Exception:
            pass  # Parse error → use empty DataFrames
        
        st.session_state['mhw_ready'] = True
        return True
    
    return False  # Still waiting for browser

# --- Persist ALL data to browser in one shot ---

def persist_to_browser():
    """Writes all in-memory data to localStorage as a single JSON object."""
    ls = get_ls()
    data = {}
    for t in MANAGED_TABLES:
        df = st.session_state['mhw_data'].get(t, pd.DataFrame())
        records = json.loads(df.to_json(orient="records")) if not df.empty else []
        data[t] = records
    ls.setItem(MHW_STORAGE_KEY, data)

# --- Cloud Storage (Supabase) ---

def _load_from_cloud(table: str, required_columns: list) -> pd.DataFrame:
    client = get_supabase_client()
    if not client or not is_logged_in():
        return pd.DataFrame(columns=required_columns)
    user_id = st.session_state.user.id
    try:
        response = client.table(table).select("*").eq("user_id", user_id).execute()
        df = pd.DataFrame(response.data)
        return df if not df.empty else pd.DataFrame(columns=required_columns)
    except Exception as e:
        st.error(f"Cloud load error: {e}")
        return pd.DataFrame(columns=required_columns)

def _save_to_cloud(table: str, df: pd.DataFrame) -> bool:
    client = get_supabase_client()
    if not client or not is_logged_in():
        return False
    user_id = st.session_state.user.id
    df_save = df.copy()
    df_save["user_id"] = user_id
    try:
        client.table(table).upsert(df_save.to_dict(orient="records")).execute()
        return True
    except Exception as e:
        st.error(f"Cloud save error: {e}")
        return False

# --- Unified Interface ---

def load_data(key: str, required_columns: list) -> pd.DataFrame:
    """
    Always returns a DataFrame.
    - Cloud mode: fetch from Supabase
    - Local mode: read from memory (populated by boot_from_browser)
    """
    if is_logged_in():
        return _load_from_cloud(key, required_columns)
    
    init_memory_storage()
    df = st.session_state['mhw_data'].get(key, pd.DataFrame())
    
    if df.empty:
        return pd.DataFrame(columns=required_columns)
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    existing = [c for c in required_columns if c in df.columns]
    return df[existing]

def save_data(key: str, df: pd.DataFrame) -> bool:
    """Saves data to memory + persists all data to browser localStorage."""
    if is_logged_in():
        return _save_to_cloud(key, df)
    
    init_memory_storage()
    st.session_state['mhw_data'][key] = df
    persist_to_browser()
    return True

def sync_local_to_cloud():
    if not is_logged_in():
        return
    for table in MANAGED_TABLES:
        df = st.session_state.get('mhw_data', {}).get(table, pd.DataFrame())
        if not df.empty:
            _save_to_cloud(table, df)
