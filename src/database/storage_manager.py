import streamlit as st
import pandas as pd
import json
import zlib
import base64
from supabase import create_client, Client

# --- Configuration ---
COOKIE_KEY = "mhw_data"
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

# --- Compression helpers (fit data in ~4KB cookie) ---

def _compress(data: dict) -> str:
    json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
    compressed = zlib.compress(json_bytes, level=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii")

def _decompress(s: str) -> dict:
    compressed = base64.urlsafe_b64decode(s.encode("ascii"))
    json_bytes = zlib.decompress(compressed)
    return json.loads(json_bytes.decode("utf-8"))

# --- Memory Cache ---

def init_memory_storage():
    if "mhw_data" not in st.session_state:
        st.session_state["mhw_data"] = {t: pd.DataFrame() for t in MANAGED_TABLES}
    if "mhw_ready" not in st.session_state:
        st.session_state["mhw_ready"] = False

# --- Boot: Read from cookie via st.context.cookies (INSTANT) ---

def boot_from_browser():
    """Read cookies from HTTP request headers. Zero latency, no component needed."""
    init_memory_storage()
    if st.session_state["mhw_ready"]:
        return True

    try:
        raw = st.context.cookies.get(COOKIE_KEY)
        if raw:
            data = _decompress(raw)
            for t in MANAGED_TABLES:
                records = data.get(t, [])
                st.session_state["mhw_data"][t] = pd.DataFrame(records) if records else pd.DataFrame()
    except Exception:
        pass  # corrupt/missing cookie → start fresh

    st.session_state["mhw_ready"] = True
    return True

# --- Persist: Write cookie via st.html (NO iframe, NO component) ---

def persist_to_browser():
    """Write all data to a browser cookie using st.html().
    st.html() renders JavaScript directly in the page (not an iframe),
    so document.cookie works on the actual page origin."""
    data = {}
    for t in MANAGED_TABLES:
        df = st.session_state.get("mhw_data", {}).get(t, pd.DataFrame())
        data[t] = json.loads(df.to_json(orient="records")) if not df.empty else []

    compressed = _compress(data)
    # Use st.html to inject a script tag directly into the page
    js = f"""<script>
document.cookie = "{COOKIE_KEY}={compressed}; path=/; max-age=2592000; SameSite=Lax";
</script>"""
    st.html(js)

# --- Debug ---

def get_debug_info() -> dict:
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
    persist_to_browser()
    return True

def sync_local_to_cloud():
    if not is_logged_in():
        return
    for table in MANAGED_TABLES:
        df = st.session_state.get("mhw_data", {}).get(table, pd.DataFrame())
        if not df.empty:
            _save_to_cloud(table, df)
