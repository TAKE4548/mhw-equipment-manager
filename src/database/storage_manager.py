import streamlit as st
import pandas as pd
import json
import base64
from supabase import create_client, Client
from streamlit_javascript import st_javascript

# --- Configuration & Initialization ---

def get_supabase_client() -> Client:
    """Initializes and returns the Supabase client using secrets."""
    try:
        url = st.secrets["connections"]["supabase"]["url"]
        key = st.secrets["connections"]["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        return None

def is_logged_in() -> bool:
    """Checks if a user is currently logged in via Supabase."""
    return "user" in st.session_state and st.session_state.user is not None

# --- Session Storage (The Primary Truth) ---

def init_memory_storage():
    """Initializes the memory storage dictionary in session state."""
    if 'mhw_memory_storage' not in st.session_state:
        st.session_state['mhw_memory_storage'] = {}

# --- Local Storage (Base64 Safe Persistence) ---

def _save_to_local_background(key: str, df: pd.DataFrame):
    """Directly pushes data to browser localStorage via JS, using Base64 for safety."""
    full_key = f"mhw_{key}"
    json_data = df.to_json(orient="records")
    
    # 1. Base64 Encode to avoid all character escaping issues in JS
    b64_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    prefix_data = f"b64:{b64_data}"
    
    js_code = f"localStorage.setItem('{full_key}', '{prefix_data}')"
    # Execute JS. 
    st_javascript(js_code)

# --- Cloud Storage (Supabase) ---

def _load_from_cloud(table: str, required_columns: list) -> pd.DataFrame:
    """Reads data from Supabase for the current user."""
    client = get_supabase_client()
    if not client or not is_logged_in():
        return pd.DataFrame(columns=required_columns)
    
    user_id = st.session_state.user.id
    try:
        response = client.table(table).select("*").eq("user_id", user_id).execute()
        df = pd.DataFrame(response.data)
        if df.empty:
            return pd.DataFrame(columns=required_columns)
        return df
    except Exception as e:
        st.error(f"Cloud load error: {e}")
        return pd.DataFrame(columns=required_columns)

def _save_to_cloud(table: str, df: pd.DataFrame):
    """Upserts data to Supabase for the current user."""
    client = get_supabase_client()
    if not client or not is_logged_in():
        return False
    
    user_id = st.session_state.user.id
    df_to_save = df.copy()
    df_to_save["user_id"] = user_id
    data = df_to_save.to_dict(orient="records")
    
    try:
        client.table(table).upsert(data).execute()
        return True
    except Exception as e:
        st.error(f"Cloud save error: {e}")
        return False

# --- Unified Interface ---

def load_data(key: str, required_columns: list):
    """
    Unified loader for Ultimate Persistence (Phase 11).
    """
    if is_logged_in():
        return _load_from_cloud(key, required_columns)
    
    # --- Local (Memory-First) Mode ---
    init_memory_storage()
    
    boot_complete = st.session_state.get('mhw_boot_complete', False)
    cache = st.session_state['mhw_memory_storage']
    
    if key in cache:
        df = cache[key]
    elif boot_complete:
        df = pd.DataFrame(columns=required_columns)
        st.session_state['mhw_memory_storage'][key] = df
    else:
        return None
        
    # Column maintenance
    existing_cols = [c for c in required_columns if c in df.columns]
    df = df[existing_cols]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    return df[required_columns]

def save_data(key: str, df: pd.DataFrame) -> bool:
    """Unified saver using Base64-safe JS setItem."""
    if is_logged_in():
        return _save_to_cloud(key, df)
    
    # --- Local Mode ---
    init_memory_storage()
    
    # 1. Update memory FIRST (Instant feedback)
    st.session_state['mhw_memory_storage'][key] = df
    
    # 2. Push to browser background via Base64 raw JS
    _save_to_local_background(key, df)
    return True

def sync_local_to_cloud():
    """Pushes memory data to Supabase after login."""
    if not is_logged_in():
        return
    
    tables = ["weapons", "trackers", "upgrades"] 
    for table in tables:
        df = st.session_state.get('mhw_memory_storage', {}).get(table)
        if df is not None and not df.empty:
            _save_to_cloud(table, df)
