import streamlit as st
import pandas as pd
import json
import zlib
import base64
from supabase import create_client, Client

# --- Configuration ---
COOKIE_KEY = "mhw_data"
MANAGED_TABLES = ["weapons", "trackers", "upgrades"]

# --- Compression (keep data under 4KB) ---

def _compress(data: dict) -> str:
    json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(zlib.compress(json_bytes, level=9)).decode("ascii")

def _decompress(s: str) -> dict:
    return json.loads(zlib.decompress(base64.urlsafe_b64decode(s)).decode("utf-8"))

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

# --- Boot: Read from HTTP cookie headers (instantaneous, no component) ---

def boot_from_browser():
    """Reads data from cookies sent in the HTTP request headers.
    st.context.cookies is available the moment the page is requested — zero latency."""
    init_memory_storage()
    if st.session_state["mhw_ready"]:
        return True

    try:
        raw = st.context.cookies.get(COOKIE_KEY)
        if raw:
            data = _decompress(raw)
            for t in MANAGED_TABLES:
                records = data.get(t, [])
                st.session_state["mhw_data"][t] = (
                    pd.DataFrame(records) if records else pd.DataFrame()
                )
    except Exception:
        pass  # corrupt / missing → start fresh

    st.session_state["mhw_ready"] = True
    return True

# --- Persist: Write cookie via st.html(unsafe_allow_javascript=True) ---
#
# KEY INSIGHT:
#   st.html(unsafe_allow_javascript=False) → inert <script> inside sandbox iframe
#   st.html(unsafe_allow_javascript=True)  → runs directly in main page context
#   ↑ This means document.cookie works on the real page origin!
#
# On the *next* page load the cookie appears in the HTTP request headers
# and st.context.cookies.get() picks it up instantly.

def persist_to_browser():
    """Writes all session data to a browser cookie."""
    data = {}
    for t in MANAGED_TABLES:
        df = st.session_state.get("mhw_data", {}).get(t, pd.DataFrame())
        data[t] = json.loads(df.to_json(orient="records")) if not df.empty else []

    compressed = _compress(data)
    cookie_str = f"{COOKIE_KEY}={compressed}; path=/; max-age=2592000; SameSite=Lax"

    st.html(
        f"<script>document.cookie = {json.dumps(cookie_str)};</script>",
        unsafe_allow_javascript=True,
    )

# --- Debug ---

def get_debug_info() -> dict:
    raw = st.context.cookies.get(COOKIE_KEY, "")
    return {
        "cookie_exists": bool(raw),
        "cookie_size_bytes": len(raw.encode()) if raw else 0,
        "weapons_count": len(
            st.session_state.get("mhw_data", {}).get("weapons", pd.DataFrame())
        ),
        "upgrades_count": len(
            st.session_state.get("mhw_data", {}).get("upgrades", pd.DataFrame())
        ),
        "trackers_count": len(
            st.session_state.get("mhw_data", {}).get("trackers", pd.DataFrame())
        ),
    }

# --- Cloud Storage (Supabase) ---

def _load_from_cloud(table: str, required_columns: list) -> pd.DataFrame:
    client = get_supabase_client()
    if not client or not is_logged_in():
        return pd.DataFrame(columns=required_columns)
    try:
        response = (
            client.table(table)
            .select("*")
            .eq("user_id", st.session_state.user.id)
            .execute()
        )
        df = pd.DataFrame(response.data)
        return df if not df.empty else pd.DataFrame(columns=required_columns)
    except Exception as e:
        st.error(f"Cloud load error: {e}")
        return pd.DataFrame(columns=required_columns)

def _save_to_cloud(table: str, df: pd.DataFrame) -> bool:
    client = get_supabase_client()
    if not client or not is_logged_in():
        return False
    df_save = df.copy()
    df_save["user_id"] = st.session_state.user.id
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
    return df[[c for c in required_columns if c in df.columns]]

def save_data(key: str, df: pd.DataFrame) -> bool:
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
