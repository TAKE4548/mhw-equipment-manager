import streamlit as st
import pandas as pd
import json
import zlib
import base64
from supabase import create_client, Client
from streamlit_cookies_controller import CookieController

# --- Configuration ---
COOKIE_KEY = "mhw_all_data"
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

# --- Compression helpers (to fit data in 4KB cookie limit) ---

def _compress(data: dict) -> str:
    """Compress dict → base64 string for cookie storage."""
    json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
    compressed = zlib.compress(json_bytes, level=9)
    return base64.b64encode(compressed).decode("ascii")

def _decompress(s: str) -> dict:
    """Decompress base64 string → dict."""
    compressed = base64.b64decode(s.encode("ascii"))
    json_bytes = zlib.decompress(compressed)
    return json.loads(json_bytes.decode("utf-8"))

# --- Cookie controller singleton ---

def _get_controller() -> CookieController:
    """Retrieves the CookieController rendered by the sidebar this run."""
    return st.session_state.get("mhw_cookie_ctrl")

def setup_cookie_controller():
    """Call this on EVERY script run from the sidebar to keep the
    CookieController component rendered and able to receive set() calls."""
    ctrl = CookieController()  # renders the hidden component in the UI
    st.session_state["mhw_cookie_ctrl"] = ctrl
    return ctrl

# --- Memory cache ---

def init_memory_storage():
    if "mhw_data" not in st.session_state:
        st.session_state["mhw_data"] = {t: pd.DataFrame() for t in MANAGED_TABLES}
    if "mhw_ready" not in st.session_state:
        st.session_state["mhw_ready"] = False

# --- Boot: Read from cookie (INSTANT via st.context.cookies) ---

def boot_from_browser():
    """
    Reads persisted data from browser cookies into memory.
    Must be called AFTER setup_cookie_controller() in the sidebar.
    """
    init_memory_storage()

    if st.session_state["mhw_ready"]:
        return True

    # Read immediately from HTTP request cookies — zero latency, no rerun needed
    try:
        raw = st.context.cookies.get(COOKIE_KEY)
        if raw:
            data = _decompress(raw)
            for t in MANAGED_TABLES:
                records = data.get(t, [])
                st.session_state["mhw_data"][t] = pd.DataFrame(records) if records else pd.DataFrame()
    except Exception:
        # Parse / decompress error → start fresh
        pass

    st.session_state["mhw_ready"] = True
    return True

# --- Persist: Write to cookie via CookieController ---

def persist_to_browser():
    """Writes all in-memory data to a single browser cookie (compressed, 30-day expiry)."""
    ctrl = _get_controller()
    data = {}
    for t in MANAGED_TABLES:
        df = st.session_state["mhw_data"].get(t, pd.DataFrame())
        data[t] = json.loads(df.to_json(orient="records")) if not df.empty else []
    try:
        compressed = _compress(data)
        # max_age: 30 days in seconds — must be explicit or cookie is session-scoped and wiped on reload
        ctrl.set(COOKIE_KEY, compressed, max_age=2592000)
    except Exception as e:
        st.warning(f"⚠️ 保存エラー: {e}")

def get_debug_info() -> dict:
    """Returns debug info about current storage state."""
    raw_cookie = st.context.cookies.get(COOKIE_KEY, "")
    return {
        "cookie_exists": bool(raw_cookie),
        "cookie_size_bytes": len(raw_cookie.encode()) if raw_cookie else 0,
        "mhw_ready": st.session_state.get("mhw_ready", False),
        "weapons_count": len(st.session_state.get("mhw_data", {}).get("weapons", pd.DataFrame())),
        "trackers_count": len(st.session_state.get("mhw_data", {}).get("trackers", pd.DataFrame())),
        "upgrades_count": len(st.session_state.get("mhw_data", {}).get("upgrades", pd.DataFrame())),
    }

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
    """Always returns a DataFrame immediately."""
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
    """Saves to memory and persists to browser cookie."""
    if is_logged_in():
        return _save_to_cloud(key, df)

    init_memory_storage()
    st.session_state["mhw_data"][key] = df
    persist_to_browser()
    return True

def sync_local_to_cloud():
    if not is_logged_in():
        return
    for table in MANAGED_TABLES:
        df = st.session_state.get("mhw_data", {}).get(table, pd.DataFrame())
        if not df.empty:
            _save_to_cloud(table, df)
