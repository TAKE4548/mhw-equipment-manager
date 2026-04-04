import streamlit as st
import pandas as pd
import json
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

# --- Local Storage (Direct JS Persistence) ---

def _save_to_local_background(key: str, df: pd.DataFrame):
    """Directly pushes data to browser localStorage via JS."""
    full_key = f"mhw_{key}"
    json_data = df.to_json(orient="records")
    
    # More robust escaping for JS string literal
    # 1. Escape backslashes
    safe_data = json_data.replace('\\', '\\\\')
    # 2. Escape single quotes (since we use ' in our JS)
    safe_data = safe_data.replace("'", "\\'")
    # 3. Escape double quotes (just in case)
    # 4. Remove actual newlines
    safe_data = safe_data.replace('\n', ' ')
    
    js_code = f"localStorage.setItem('{full_key}', '{safe_data}')"
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
    Unified loader for Ultimate JS Handshake.
    """
    if is_logged_in():
        return _load_from_cloud(key, required_columns)
    
    # --- Local (Memory-First) Mode ---
    init_memory_storage()
    
    # FORCED PERSISTENCE: 
    # If the app has EVER booted correctly, always return a DataFrame from memory.
    boot_complete = st.session_state.get('mhw_boot_complete', False)
    cache = st.session_state['mhw_memory_storage']
    
    if key in cache:
        df = cache[key]
    elif boot_complete:
        # Boot was complete but key is missing? Return empty.
        df = pd.DataFrame(columns=required_columns)
        st.session_state['mhw_memory_storage'][key] = df
    else:
        # ONLY return None if we are strictly in the first-ever loading frame
        return None
        
    # Column maintenance
    existing_cols = [c for c in required_columns if c in df.columns]
    df = df[existing_cols]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    return df[required_columns]

def save_data(key: str, df: pd.DataFrame) -> bool:
    """Unified saver using direct JS setItem."""
    if is_logged_in():
        return _save_to_cloud(key, df)
    
    # --- Local Mode ---
    init_memory_storage()
    
    # 1. Update memory FIRST (Instant feedback)
    st.session_state['mhw_memory_storage'][key] = df
    
    # 2. Push to browser background via raw JS
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
