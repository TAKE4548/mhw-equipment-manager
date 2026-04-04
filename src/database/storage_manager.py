import streamlit as st
import pandas as pd
import json
from supabase import create_client, Client

# Note: LocalStorage component is initialized once in the sidebar and stored in session state.

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

# --- Local Storage (Browser) Consistency ---

def _get_ls_handler():
    """Returns the central LocalStorage handler from session state."""
    if 'ls_handler' not in st.session_state:
        # Fallback if accessed before sidebar (rare)
        from streamlit_local_storage import LocalStorage
        st.session_state['ls_handler'] = LocalStorage()
    return st.session_state['ls_handler']

def is_storage_ready(key: str) -> bool:
    """Checks if the local storage has successfully communicated with the browser."""
    if is_logged_in():
        return True
        
    full_key = f"mhw_{key}"
    ready_key = f"ready_{full_key}"
    
    if ready_key not in st.session_state:
        st.session_state[ready_key] = False
    
    # Try to fetch from browser using the central handler
    ls = _get_ls_handler()
    result = ls.getItem(full_key)
    
    if result is not None:
        st.session_state[ready_key] = True
        st.session_state[f"cache_{full_key}"] = result
        return True
    
    return st.session_state.get(ready_key, False)

# --- Local Storage (Browser) Operations ---

def _load_from_local(key: str) -> pd.DataFrame:
    """Reads data from browser localStorage with a 'Ready' check."""
    full_key = f"mhw_{key}"
    
    if not is_storage_ready(key):
        return None 
        
    final_val = st.session_state.get(f"cache_{full_key}")
    
    if final_val and final_val != "null":
        try:
            if isinstance(final_val, str):
                data = json.loads(final_val)
            else:
                data = final_val
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error parsing local storage for {key}: {e}")
            
    return pd.DataFrame()

def _save_to_local(key: str, df: pd.DataFrame):
    """Writes data to browser localStorage only if we have successfully loaded it once."""
    if not is_storage_ready(key):
        return False

    full_key = f"mhw_{key}"
    json_data = df.to_json(orient="records")
    data = json.loads(json_data)
    
    ls = _get_ls_handler()
    ls.setItem(full_key, data)
    
    # Update cache immediately
    st.session_state[f"cache_{full_key}"] = data
    return True

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
    """Unified loader."""
    if is_logged_in():
        df = _load_from_cloud(key, required_columns)
    else:
        df = _load_from_local(key)
    
    if df is None:
        return None
        
    if df.empty:
        return pd.DataFrame(columns=required_columns)
    
    existing_cols = [c for c in required_columns if c in df.columns]
    df = df[existing_cols]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
            
    return df[required_columns]

def save_data(key: str, df: pd.DataFrame) -> bool:
    """Unified saver."""
    if is_logged_in():
        return _save_to_cloud(key, df)
    else:
        return _save_to_local(key, df)

def sync_local_to_cloud():
    """Pushes any data found in localStorage to Supabase after login."""
    if not is_logged_in():
        return
    
    tables = ["weapons", "trackers", "upgrades"] 
    for table in tables:
        local_df = _load_from_local(table)
        if local_df is not None and not local_df.empty:
            if _save_to_cloud(table, local_df):
                pass
