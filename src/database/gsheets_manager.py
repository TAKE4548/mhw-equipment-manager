import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
import json

def get_gsheets_connection():
    """Returns a GSheets connection if a URL is provided in session state."""
    url = st.session_state.get("gsheet_url")
    if not url:
        return None
    
    return st.connection("gsheets", type=GSheetsConnection)

def load_data(worksheet=0, required_columns=None):
    """Loads data from a specific worksheet in the configured Google Sheet."""
    url = st.session_state.get("gsheet_url")
    if not url:
        return pd.DataFrame()
    
    if required_columns is None:
        required_columns = ["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"]
    
    conn = get_gsheets_connection()
    if conn:
        try:
            df = conn.read(spreadsheet=url, worksheet=worksheet, ttl=0)
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
    
    conn = get_gsheets_connection()
    if conn:
        try:
            conn.update(spreadsheet=url, worksheet=worksheet, data=df)
            return True
        except Exception as e:
            st.error(f"Error writing to Google Sheets (worksheet: {worksheet}): {e}. Make sure the sheet is shared and the worksheet exists.")
            return False
    return False
