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

def load_data():
    """Loads data from the configured Google Sheet."""
    url = st.session_state.get("gsheet_url")
    if not url:
        return pd.DataFrame()
    
    conn = get_gsheets_connection()
    if conn:
        try:
            df = conn.read(spreadsheet=url, ttl=0)
            if df.empty:
                return pd.DataFrame(columns=["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"])
            
            required = ["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"]
            for col in required:
                if col not in df.columns:
                    df[col] = None
            return df[required]
        except Exception as e:
            if "No columns to parse" in str(e):
                return pd.DataFrame(columns=["id", "weapon_type", "element", "series_skill", "group_skill", "remaining_count"])
            st.error(f"Error reading from Google Sheets: {repr(e)}")
            st.exception(e)
            return pd.DataFrame()
    return pd.DataFrame()

def save_data(df: pd.DataFrame):
    """Saves the entire DataFrame to the configured Google Sheet."""
    url = st.session_state.get("gsheet_url")
    if not url:
        return False
    
    conn = get_gsheets_connection()
    if conn:
        try:
            conn.update(spreadsheet=url, data=df)
            return True
        except Exception as e:
            st.error(f"Error writing to Google Sheets: {e}. Make sure the sheet is shared with the service account.")
            return False
    return False
