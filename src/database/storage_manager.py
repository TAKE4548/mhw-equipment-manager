import streamlit as st
import pandas as pd
import json
import zlib
import base64
import uuid
import re
from supabase import create_client, Client

# --- Configuration ---
COOKIE_KEY = "mhw_data"
MANAGED_TABLES = ["weapons", "trackers", "upgrades", "favorites", "talismans"]

# --- Compression ---

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
    if "needs_persist" not in st.session_state:
        st.session_state["needs_persist"] = False

def _is_valid_uuid(val):
    if not isinstance(val, str): return False
    # Simple UUID v4 regex
    return bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', val.lower()))

def _migrate_local_ids():
    """Scans session state for legacy IDs and converts them to UUIDs, maintaining references."""
    if "mhw_data" not in st.session_state: return
    
    data = st.session_state["mhw_data"]
    id_map = {} # old_id -> new_id
    any_migration = False
    
    # 1. Collect and migrate IDs for primary tables
    for table in ["weapons", "upgrades", "talismans", "favorites"]:
        df = data.get(table, pd.DataFrame())
        if df.empty or "id" not in df.columns: continue
        
        # Explicitly cast to object to avoid FutureWarning when assigning UUID strings to numeric columns
        if df["id"].dtype != "object":
            df["id"] = df["id"].astype(object)
            
        changed = False
        for idx, row in df.iterrows():
            old_id = str(row["id"])
            if not _is_valid_uuid(old_id):
                new_id = str(uuid.uuid4())
                id_map[old_id] = new_id
                df.at[idx, "id"] = new_id
                changed = True
                any_migration = True
        if changed: data[table] = df

    # 2. Migrate Trackers
    df_t = data.get("trackers", pd.DataFrame())
    if not df_t.empty:
        # Cast columns to object
        for col in ["id", "weapon_id"]:
            if col in df_t.columns and df_t[col].dtype != "object":
                df_t[col] = df_t[col].astype(object)
                
        changed_t = False
        for idx, row in df_t.iterrows():
            old_tid = str(row["id"])
            if not _is_valid_uuid(old_tid):
                new_tid = str(uuid.uuid4())
                df_t.at[idx, "id"] = new_tid
                changed_t = True
                any_migration = True
            
            old_wid = str(row.get("weapon_id", ""))
            if old_wid in id_map:
                df_t.at[idx, "weapon_id"] = id_map[old_wid]
                changed_t = True
                any_migration = True
            elif old_wid and not _is_valid_uuid(old_wid):
                df_t.at[idx, "weapon_id"] = str(uuid.uuid4())
                changed_t = True
                any_migration = True
                
        if changed_t: data["trackers"] = df_t

    if any_migration:
        st.session_state["needs_persist"] = True
        # If logged in, sync to cloud to clear the UUID constraint error
        if is_logged_in():
            for table in MANAGED_TABLES:
                df = data.get(table, pd.DataFrame())
                if not df.empty:
                    _save_to_cloud(table, df)

# --- Boot: Read from HTTP cookie headers ---

def boot_from_browser():
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
            _migrate_local_ids()
    except Exception:
        pass

    st.session_state["mhw_ready"] = True
    return True

# --- Persist: Write cookie via st.html ---

def persist_to_browser():
    """Immediately injects a JS snippet to write the cookie to the browser.
    This should be called at the end of the script (e.g. in the sidebar)
    to ensure the script is not killed by a premature st.rerun()."""
    data = {}
    for t in MANAGED_TABLES:
        df = st.session_state.get("mhw_data", {}).get(t, pd.DataFrame())
        data[t] = json.loads(df.to_json(orient="records")) if not df.empty else []

    try:
        compressed = _compress(data)
        cookie_str = f"{COOKIE_KEY}={compressed}; path=/; max-age=2592000; SameSite=Lax"

        # Using unsafe_allow_javascript=True to escape sandbox iframe
        # Try to write to both local and parent document just in case.
        js = f"""
        <script>
            (function() {{
                const cookie = {json.dumps(cookie_str)};
                console.log("MHW Sync: Attempting write...");
                try {{
                    document.cookie = cookie;
                    console.log("MHW Sync: Local write successful.");
                }} catch(e) {{
                    console.error("MHW Sync: Local write failed", e);
                }}
                
                try {{
                    if (window.parent && window.parent.document) {{
                        window.parent.document.cookie = cookie;
                        console.log("MHW Sync: Parent write successful.");
                    }}
                }} catch(e) {{
                    console.warn("MHW Sync: Parent write blocked (CORS/Sandbox)", e);
                }}
            }})();
        </script>
        """
        st.html(js, unsafe_allow_javascript=True)
    except Exception as e:
        st.error(f"Persistence error: {e}")

# --- Debug ---

def get_debug_info() -> dict:
    raw = st.context.cookies.get(COOKIE_KEY, "")
    return {
        "cookie_exists": bool(raw),
        "cookie_size_bytes": len(raw.encode()) if raw else 0,
        "needs_persist": st.session_state.get("needs_persist", False),
        "weapons_count": len(st.session_state.get("mhw_data", {}).get("weapons", pd.DataFrame())),
        "upgrades_count": len(st.session_state.get("mhw_data", {}).get("upgrades", pd.DataFrame())),
        "trackers_count": len(st.session_state.get("mhw_data", {}).get("trackers", pd.DataFrame())),
    }

# --- Cloud Storage (Supabase) ---

def _load_from_cloud(table: str, required_columns: list) -> pd.DataFrame:
    client = get_supabase_client()
    if not client or not is_logged_in():
        return pd.DataFrame(columns=required_columns)
    try:
        response = client.table(table).select("*").eq("user_id", st.session_state.user.id).execute()
        df = pd.DataFrame(response.data)
        if df.empty:
            return pd.DataFrame(columns=required_columns)
            
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        return df[required_columns]
    except Exception as e:
        st.error(f"Cloud load error (table: {table}): {e}")
        return pd.DataFrame(columns=required_columns)

def _save_to_cloud(table: str, df: pd.DataFrame) -> bool:
    client = get_supabase_client()
    if not client or not is_logged_in():
        return False
    
    if df.empty:
        return True
        
    df_save = df.copy()
    df_save["user_id"] = st.session_state.user.id
    
    try:
        data_to_save = df_save.to_dict(orient="records")
        client.table(table).upsert(data_to_save).execute()
        return True
    except Exception as e:
        st.error(f"Cloud save error (table: {table}): {e}")
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
    st.session_state["needs_persist"] = False
    return True

def delete_record(key: str, record_id: str) -> bool:
    if is_logged_in():
        client = get_supabase_client()
        if client:
            try:
                client.table(key).delete().eq("id", record_id).eq("user_id", st.session_state.user.id).execute()
            except Exception as e:
                st.error(f"Cloud delete error: {e}")
                return False

    init_memory_storage()
    df = st.session_state["mhw_data"].get(key, pd.DataFrame())
    if not df.empty:
        st.session_state["mhw_data"][key] = df[df["id"].astype(str) != str(record_id)]
    
    persist_to_browser()
    return True

def sync_local_to_cloud():
    if not is_logged_in():
        return
        
    progress_text = st.empty()
    progress_text.info("🔃 ローカルデータをクラウドに同期中...")
    
    success_count = 0
    for table in MANAGED_TABLES:
        df = st.session_state.get("mhw_data", {}).get(table, pd.DataFrame())
        if not df.empty:
            if _save_to_cloud(table, df):
                success_count += 1
                
    if success_count > 0:
        progress_text.success(f"✅ {success_count} 個のテーブルをクラウドに同期しました。")
    else:
        progress_text.empty()

# --- Persistent Auth ---

AUTH_COOKIE_KEY = "mhw_auth"

def set_auth_cookie(access_token: str, refresh_token: str):
    """Writes the Supabase session tokens to a browser cookie."""
    cookie_val = f"{access_token}|{refresh_token}" if access_token else ""
    cookie_str = f"{AUTH_COOKIE_KEY}={cookie_val}; path=/; max-age=2592000; SameSite=Lax"
    
    js = f"""
    <script>
        (function() {{
            const cookie = {json.dumps(cookie_str)};
            try {{ document.cookie = cookie; }} catch(e) {{}}
            try {{ if (window.parent && window.parent.document) window.parent.document.cookie = cookie; }} catch(e) {{}}
        }})();
    </script>
    """
    st.html(js, unsafe_allow_javascript=True)

def try_restore_session():
    """Attempts to restore a Supabase session from the browser cookie."""
    if st.session_state.get("user"):
        return True # Already logged in
        
    client = get_supabase_client()
    if not client:
        return False
        
    try:
        raw_auth = st.context.cookies.get(AUTH_COOKIE_KEY)
        if raw_auth and "|" in raw_auth:
            access, refresh = raw_auth.split("|", 1)
            # Restore session
            res = client.auth.set_session(access, refresh)
            if res.user:
                st.session_state.user = res.user
                return True
    except Exception:
        pass
    return False
