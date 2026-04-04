import streamlit as st
import pandas as pd
import json
from supabase import create_client, Client
from streamlit_cookies_manager import EncryptedCookieManager

# --- Configuration ---
COOKIE_KEY = "mhw_all"
MANAGED_TABLES = ["weapons", "trackers", "upgrades"]

# --- Cookie Manager ---

def make_cookie_manager() -> EncryptedCookieManager:
    """Creates and renders the EncryptedCookieManager component.
    Call ONCE per script run at the top level (e.g., sidebar).
    Returns the instance for use throughout the run."""
    return EncryptedCookieManager(
        prefix="mhw/",
        password=st.secrets.get("COOKIES_PASSWORD", "mhw-local-dev-default-password-2026"),
    )

def _get_cookies() -> EncryptedCookieManager:
    """Gets the manager created this run. Raises if make_cookie_manager() wasn't called."""
    cookies = st.session_state.get("_cookie_manager")
    if cookies is None:
        raise RuntimeError("make_cookie_manager() must be called before using cookies.")
    return cookies

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
    if "mhw_data" not in st.session_state:
        st.session_state["mhw_data"] = {t: pd.DataFrame() for t in MANAGED_TABLES}
    if "mhw_ready" not in st.session_state:
        st.session_state["mhw_ready"] = False

# --- Boot: Read from cookie ---

def boot_from_browser(cookies: EncryptedCookieManager) -> bool:
    """Reads persisted data from browser cookies into memory.
    Requires a ready() EncryptedCookieManager instance."""
    init_memory_storage()
    if st.session_state["mhw_ready"]:
        return True

    try:
        raw = cookies.get(COOKIE_KEY)
        if raw:
            data = json.loads(raw)
            for t in MANAGED_TABLES:
                records = data.get(t, [])
                st.session_state["mhw_data"][t] = pd.DataFrame(records) if records else pd.DataFrame()
    except Exception:
        pass  # Fresh start on error

    st.session_state["mhw_ready"] = True
    return True

# --- Persist: Write to cookie ---

def persist_to_browser(cookies: EncryptedCookieManager) -> bool:
    """Writes memory data back to the browser cookie."""
    if not cookies.ready():
        return False

    data = {}
    for t in MANAGED_TABLES:
        df = st.session_state.get("mhw_data", {}).get(t, pd.DataFrame())
        data[t] = json.loads(df.to_json(orient="records")) if not df.empty else []

    try:
        json_str = json.dumps(data, ensure_ascii=False)
        cookies[COOKIE_KEY] = json_str
        cookies.save()
    except Exception as e:
        st.error(f"Cookie 保存に失敗しました: {e}")
        return False
    return True

# --- Usage Monitoring ---

def get_cookie_usage_bytes(cookies: EncryptedCookieManager) -> int:
    """Returns the size of the current cookie data in bytes."""
    raw = cookies.get(COOKIE_KEY, "")
    return len(raw.encode("utf-8")) if raw else 0

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
    if is_logged_in():
        return _load_from_cloud(key, required_columns)
    init_memory_storage()
    df = st.session_state["mhw_data"].get(key, pd.DataFrame())
    if df.empty:
        return pd.DataFrame(columns=required_columns)
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    existing = [c for c in required_columns if c in df.columns]
    return df[existing]

def save_data(key: str, df: pd.DataFrame) -> bool:
    if is_logged_in():
        return _save_to_cloud(key, df)
    init_memory_storage()
    st.session_state["mhw_data"][key] = df
    # Get the manager created this run by sidebar
    cookies = st.session_state.get("_cookie_manager")
    if cookies and cookies.ready():
        persist_to_browser(cookies)
    return True

def sync_local_to_cloud():
    if not is_logged_in():
        return
    for table in MANAGED_TABLES:
        df = st.session_state.get("mhw_data", {}).get(table, pd.DataFrame())
        if not df.empty:
            _save_to_cloud(table, df)
