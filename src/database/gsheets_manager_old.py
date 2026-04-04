import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def normalize_gsheet_url(url: str) -> str:
    """Standardizes Google Sheet URLs to simple /edit format for gspread compatibility."""
    if not url:
        return ""
    # We just need the base URL or Spreadsheet ID. 
    # gspread's open_by_url is robust if it contains /d/ID
    if '/spreadsheets/d/' in url:
        base = url.split('/edit')[0].split('/view')[0].split('?')[0].split('#')[0]
        return base.rstrip('/') + '/edit'
    return url

def get_gspread_client():
    """Initializes and returns an authorized gspread client using streamlit secrets."""
    try:
        creds_dict = st.secrets["connections"]["gsheets"]
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Failed to initialize Google Sheets client: {e}. Check your Streamlit Secrets.")
        return None

@st.cache_data(show_spinner=False)
def _get_spreadsheet(url):
    """Internal cached helper to get a spreadsheet object."""
    client = get_gspread_client()
    if not client:
        return None
    
    n_url = normalize_gsheet_url(url)
    try:
        return client.open_by_url(n_url)
    except gspread.exceptions.SpreadsheetNotFound:
        # Get email to show in error message
        try:
            client_email = st.secrets["connections"]["gsheets"].get("client_email", "サービスアカウント")
        except:
            client_email = "サービスアカウント"
            
        st.error(f"""
        ❌ **スプレッドシートが見つかりません (404)**
        
        以下のいずれかが原因です：
        1. **URLの間違い**: 正しいGoogleスプレッドシートのURLか確認してください。
        2. **権限不足**: 自分のシートの「共有」ボタンから、以下のメールを「編集者」として追加してください：
        `{client_email}`
        """)
        return None
    except Exception as e:
        st.error(f"Error accessing spreadsheet: {e}")
        return None

def ensure_worksheet_exists(spreadsheet, worksheet_name):
    """Ensures a worksheet exists in the given spreadsheet object."""
    if not spreadsheet or not worksheet_name:
        return None
        
    try:
        return spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # Create it
        return spreadsheet.add_worksheet(title=worksheet_name, rows="500", cols="30")
    except Exception as e:
        print(f"Error checking worksheet '{worksheet_name}': {e}")
        return None

@st.cache_data(show_spinner="Loading data from GSheets...", ttl=60)
def load_data(url, worksheet_name, required_columns=None):
    """Loads data from a specific worksheet using gspread directly."""
    if not url:
        return pd.DataFrame()
    
    if required_columns is None:
        required_columns = ["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"]
        
    spreadsheet = _get_spreadsheet(url)
    if not spreadsheet:
        return pd.DataFrame(columns=required_columns)
        
    ws = ensure_worksheet_exists(spreadsheet, worksheet_name)
    if not ws:
        return pd.DataFrame(columns=required_columns)
        
    try:
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        
        if df.empty:
            return pd.DataFrame(columns=required_columns)
            
        # Ensure all columns exist
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        return df[required_columns]
    except Exception as e:
        st.error(f"Error reading worksheet '{worksheet_name}': {e}")
        return pd.DataFrame(columns=required_columns)

def save_data(df: pd.DataFrame, url, worksheet_name):
    """Saves the entire DataFrame to the specific worksheet using gspread directly."""
    if not url:
        return False
        
    spreadsheet = _get_spreadsheet(url)
    if not spreadsheet:
        return False
        
    ws = ensure_worksheet_exists(spreadsheet, worksheet_name)
    if not ws:
        return False
        
    try:
        # Clear and update (Atomic-ish)
        ws.clear()
        # Header + values
        ws.update([df.columns.values.tolist()] + df.values.tolist())
        st.cache_data.clear() # Reset cache so next load gets fresh data
        return True
    except Exception as e:
        st.error(f"Error saving to worksheet '{worksheet_name}': {e}")
        return False
