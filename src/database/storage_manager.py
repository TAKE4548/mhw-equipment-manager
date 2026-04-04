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
        # Fallback if secrets are not set yet
        return None

def is_logged_in() -> bool:
    """Checks if a user is currently logged in via Supabase."""
    return "user" in st.session_state and st.session_state.user is not None

# --- Local Storage (Browser) ---

def _load_from_local(key: str) -> pd.DataFrame:
    """Reads data from browser localStorage using JavaScript."""
    js_code = f"localStorage.getItem('mhw_{key}')"
    result = st_javascript(js_code)
    
    if result and result != "null":
        try:
            data = json.loads(result)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error parsing local storage for {key}: {e}")
    return pd.DataFrame()

def _save_to_local(key: str, df: pd.DataFrame):
    """Writes data to browser localStorage using JavaScript."""
    json_data = df.to_json(orient="records")
    # Escape single quotes for JS
    json_data_escaped = json_data.replace("'", "\\'")
    js_code = f"localStorage.setItem('mhw_{key}', '{json_data_escaped}')"
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
    # Add user_id to all rows
    df_to_save = df.copy()
    df_to_save["user_id"] = user_id
    
    # Convert DataFrame to list of dicts
    data = df_to_save.to_dict(orient="records")
    
    try:
        # Supabase upsert requires a unique constraint (usually 'id')
        client.table(table).upsert(data).execute()
        return True
    except Exception as e:
        st.error(f"Cloud save error: {e}")
        return False

# --- Unified Interface ---

def load_data(key: str, required_columns: list) -> pd.DataFrame:
    """Unified loader that switches between Local and Cloud."""
    if is_logged_in():
        df = _load_from_cloud(key, required_columns)
    else:
        df = _load_from_local(key)
    
    # Ensure columns exist and cleanup
    if df.empty:
        return pd.DataFrame(columns=required_columns)
    
    # Filter to required columns and fill missing
    existing_cols = [c for c in required_columns if c in df.columns]
    df = df[existing_cols]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
            
    return df[required_columns]

def save_data(key: str, df: pd.DataFrame) -> bool:
    """Unified saver that switches between Local and Cloud."""
    if is_logged_in():
        return _save_to_cloud(key, df)
    else:
        _save_to_local(key, df)
        return True

def sync_local_to_cloud():
    """Pushes any data found in localStorage to Supabase after login."""
    if not is_logged_in():
        return
    
    tables = ["weapons", "trackers"] # These match our GSheets names for now
    for table in tables:
        local_df = _load_from_local(table)
        if not local_df.empty:
            if _save_to_cloud(table, local_df):
                # Optionally clear local storage after successful sync
                # st_javascript(f"localStorage.removeItem('mhw_{table}')")
                pass
