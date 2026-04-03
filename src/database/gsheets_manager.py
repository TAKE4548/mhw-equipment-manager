import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
import json

import gspread
from google.oauth2.service_account import Credentials

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
        
    try:
        # Use gspread directly for advanced operations like creating worksheets
        creds_dict = st.secrets["connections"]["gsheets"]
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_url(url)
        
        # Check if exists
        worksheet_list = [w.title for w in spreadsheet.worksheets()]
        if worksheet_name not in worksheet_list:
            spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="20")
            print(f"Created new worksheet: {worksheet_name}")
    except Exception as e:
        # Print the error to console instead of using st.error to avoid Streamlit cache replay issues
        print(f"Failed to auto-create worksheet '{worksheet_name}': {type(e).__name__} - {e}")

def load_data(worksheet=0, required_columns=None):
    """Loads data from a specific worksheet in the configured Google Sheet."""
    url = st.session_state.get("gsheet_url")
    if not url:
        return pd.DataFrame()
    
    # Auto-create worksheet if name is provided and doesn't exist
    ensure_worksheet_exists(url, worksheet)
    
    if required_columns is None:
        required_columns = ["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"]
    
    conn = get_gsheets_connection()
    if conn:
        try:
            # Set ttl to 60 seconds to prevent Rate Limit 429 on every dropdown rerendering
            df = conn.read(spreadsheet=url, worksheet=worksheet, ttl=60)
            if df.empty:
                return pd.DataFrame(columns=required_columns)
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            return df[required_columns]
        except Exception as e:
            if "No columns to parse" in str(e) or "WorksheetNotFound" in str(e):
                return pd.DataFrame(columns=required_columns)
            st.error(f"Error reading from Google Sheets (worksheet: {worksheet}): {repr(e)}")
            return pd.DataFrame(columns=required_columns)
    return pd.DataFrame(columns=required_columns)

def save_data(df: pd.DataFrame, worksheet=0):
    """Saves the entire DataFrame to the specific worksheet in the configured Google Sheet."""
    url = st.session_state.get("gsheet_url")
    if not url:
        return False
        
    ensure_worksheet_exists(url, worksheet)
    
    conn = get_gsheets_connection()
    if conn:
        try:
            conn.update(spreadsheet=url, worksheet=worksheet, data=df)
            st.cache_data.clear() # Clear cache to instantly reflect changes
            return True
        except Exception as e:
            st.error(f"Error writing to Google Sheets (worksheet: {worksheet}): {e}. Make sure the sheet is shared and the worksheet exists.")
            return False
    return False
