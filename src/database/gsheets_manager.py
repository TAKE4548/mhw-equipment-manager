import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def normalize_gsheet_url(url: str) -> str:
    """Standardizes Google Sheet URLs to include the /edit suffix for best library compatibility."""
    if not url:
        return ""
    
    if '/spreadsheets/d/' in url:
        # Extract base and append /edit, removing any view/edit suffixes or query params
        base = url.split('/edit')[0].split('/view')[0].split('?')[0].split('#')[0]
        return base.rstrip('/') + '/edit'
            
    return url

def get_gsheets_connection():
    """Returns a GSheets connection if a URL is provided in session state."""
    url = st.session_state.get("gsheet_url")
    if not url:
        return None
    
    return st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(show_spinner=False)
def ensure_worksheet_exists(url, worksheet_name):
    """Ensures a worksheet with the given name exists in the spreadsheet."""
    if isinstance(worksheet_name, int) or not worksheet_name:
        return
        
    n_url = normalize_gsheet_url(url)
    try:
        # Use gspread directly for advanced operations like creating worksheets
        creds_dict = st.secrets["connections"]["gsheets"]
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        
        # open_by_url is sensitive to extra parameters
        spreadsheet = client.open_by_url(n_url)
        
        # Check if exists
        worksheet_list = [w.title for w in spreadsheet.worksheets()]
        if worksheet_name not in worksheet_list:
            spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="20")
            print(f"Created new worksheet: {worksheet_name}")
    except Exception as e:
        # Print the error to console instead of using st.error to avoid Streamlit cache replay issues
        print(f"Failed to auto-create worksheet '{worksheet_name}' at {n_url}: {type(e).__name__} - {e}")

def load_data(worksheet=0, required_columns=None):
    """Loads data from a specific worksheet in the configured Google Sheet."""
    url = st.session_state.get("gsheet_url")
    if not url:
        return pd.DataFrame()
    
    n_url = normalize_gsheet_url(url)
    
    # Auto-create worksheet if name is provided and doesn't exist
    ensure_worksheet_exists(n_url, worksheet)
    
    if required_columns is None:
        required_columns = ["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"]
    
    conn = get_gsheets_connection()
    if conn:
        try:
            # Set ttl to 60 seconds to prevent Rate Limit 429 on every dropdown rerendering
            # Using normalized URL here is critical to avoid 400 Bad Request
            df = conn.read(spreadsheet=n_url, worksheet=worksheet, ttl=60)
            if df.empty:
                return pd.DataFrame(columns=required_columns)
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            return df[required_columns]
        except Exception as e:
            err_msg = str(e)
            if "No columns to parse" in err_msg or "WorksheetNotFound" in err_msg:
                return pd.DataFrame(columns=required_columns)
            
            # Diagnose 400/404 errors
            if "400" in err_msg:
                st.error(f"❌ **Google Sheets API エラー (400 Bad Request)**\n\nURL または ワークシート名「{worksheet}」が正しく解釈されていません。スプレッドシートが正しく認識されているか確認してください。")
            elif "404" in err_msg:
                st.error(f"❌ **Google Sheets API エラー (404 Not Found)**\n\n指定されたスプレッドシートが見つかりません。以下の点をご確認ください。\n\n1.  **URLの確認**: 入力したURLが正しいか確認してください。\n2.  **共有設定の確認**: Service Accountのメールアドレス（Secrets 参照）が、スプレッドシートに対して「編集者 (Editor)」として共有されている必要があります。\n3.  **シート名の確認**: スプレッドシート内に「{worksheet}」という名称のタブが存在するか確認してください。")
            else:
                st.error(f"Error reading from Google Sheets (worksheet: {worksheet}): {repr(e)}")
            return pd.DataFrame(columns=required_columns)
    return pd.DataFrame(columns=required_columns)

def save_data(df: pd.DataFrame, worksheet=0):
    """Saves the entire DataFrame to the specific worksheet in the configured Google Sheet."""
    url = st.session_state.get("gsheet_url")
    if not url:
        return False
        
    n_url = normalize_gsheet_url(url)
    ensure_worksheet_exists(n_url, worksheet)
    
    conn = get_gsheets_connection()
    if conn:
        try:
            conn.update(spreadsheet=n_url, worksheet=worksheet, data=df)
            st.cache_data.clear() # Clear cache to instantly reflect changes
            return True
        except Exception as e:
            st.error(f"Error writing to Google Sheets (worksheet: {worksheet}): {e}. Make sure the sheet is shared and the worksheet exists.")
            return False
    return False
