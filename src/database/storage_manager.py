import streamlit as st
import pandas as pd
import json
import os
from supabase import create_client, Client

# --- Configuration & Initialization ---

# Local data directory (relative to the app root)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")

def _ensure_data_dir():
    """Create local data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

def get_supabase_client() -> Client:
    """Initializes and returns the Supabase client using secrets."""
    try:
        url = st.secrets["connections"]["supabase"]["url"]
        key = st.secrets["connections"]["supabase"]["key"]
        return create_client(url, key)
    except Exception:
        return None

def is_logged_in() -> bool:
    """Checks if a user is currently logged in via Supabase."""
    return "user" in st.session_state and st.session_state.user is not None

# --- Session Storage (Memory Cache) ---

def init_memory_storage():
    """Initializes the memory storage dictionary in session state."""
    if 'mhw_memory_storage' not in st.session_state:
        st.session_state['mhw_memory_storage'] = {}

# --- Local File Storage ---

def _get_file_path(key: str) -> str:
    """Returns the file path for a given data key."""
    _ensure_data_dir()
    return os.path.join(DATA_DIR, f"{key}.json")

def _load_from_file(key: str) -> pd.DataFrame:
    """Reads data from a local JSON file."""
    filepath = _get_file_path(key)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data:
                return pd.DataFrame(data)
        except Exception as e:
            st.warning(f"ローカルファイル読み込みエラー ({key}): {e}")
    return pd.DataFrame()

def _save_to_file(key: str, df: pd.DataFrame) -> bool:
    """Writes data to a local JSON file."""
    filepath = _get_file_path(key)
    try:
        data = json.loads(df.to_json(orient="records"))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"ローカルファイル保存エラー ({key}): {e}")
        return False

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

def _save_to_cloud(table: str, df: pd.DataFrame) -> bool:
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

def load_data(key: str, required_columns: list) -> pd.DataFrame:
    """
    Unified loader. Always returns a DataFrame (never None).
    - Logged in: Supabase
    - Anonymous: Local JSON file with memory cache
    """
    if is_logged_in():
        return _load_from_cloud(key, required_columns)
    
    # --- Local Mode (File + Memory Cache) ---
    init_memory_storage()
    cache = st.session_state['mhw_memory_storage']
    
    if key not in cache:
        # First access this session: load from disk
        cache[key] = _load_from_file(key)
    
    df = cache[key]
    
    if df.empty:
        return pd.DataFrame(columns=required_columns)
    
    # Column maintenance
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    existing_cols = [c for c in required_columns if c in df.columns]
    return df[existing_cols]

def save_data(key: str, df: pd.DataFrame) -> bool:
    """
    Unified saver.
    - Logged in: Supabase
    - Anonymous: Local JSON file + memory cache update
    """
    if is_logged_in():
        return _save_to_cloud(key, df)
    
    # --- Local Mode ---
    init_memory_storage()
    
    # Update memory cache
    st.session_state['mhw_memory_storage'][key] = df
    
    # Persist to disk immediately
    return _save_to_file(key, df)

def sync_local_to_cloud():
    """Pushes local file data to Supabase after login."""
    if not is_logged_in():
        return
    
    tables = ["weapons", "trackers", "upgrades"]
    for table in tables:
        df = _load_from_file(table)
        if not df.empty:
            _save_to_cloud(table, df)
