import json
import os
import streamlit as st

@st.cache_data
def _load_translations():
    """Loads the translation JSON file."""
    # Robust path resolution
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_path, "locales", "ja.json")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # Fallback to empty dict and log or handle gracefully
        return {}

def t(key, **kwargs):
    """
    Returns the translated string for the given key.
    Supports variables via kwargs (e.g., t("HI", name="Alice")).
    If key is not found, returns the key itself.
    """
    translations = _load_translations()
    val = translations.get(key, key)
    
    if kwargs and isinstance(val, str):
        try:
            return val.format(**kwargs)
        except KeyError:
            return val
            
    return val
