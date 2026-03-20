import json
import os

def get_master_data():
    """Loads master data from JSON file."""
    # Build path relative to this file
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'master_data.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback for unexpected path issues
        return {}
