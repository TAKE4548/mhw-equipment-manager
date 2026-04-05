import streamlit as st

def clear_logic_cache(table: str):
    """
    Clears the specific st.cache_data for a given table name.
    Uses local imports to prevent circular dependencies.
    """
    try:
        if table == "trackers":
            from src.logic.restoration_tracker import load_trackers
            load_trackers.clear()
        elif table == "weapons":
            from src.logic.equipment_box import load_equipment
            load_equipment.clear()
        elif table == "upgrades":
            from src.logic.equipment import load_upgrades
            load_upgrades.clear()
        elif table == "talismans":
            from src.logic.talismans import load_talismans
            # Correcting typo: load_trackers -> load_talismans
            load_talismans.clear()
        elif table == "favorites":
            from src.logic.favorites import get_favorites
            get_favorites.clear()
    except (ImportError, AttributeError):
        pass

def clear_all_logic_caches():
    """
    Clears all logic-level caches. 
    Call this on major state changes like Login, Logout, or Cloud Sync.
    """
    for table in ["trackers", "weapons", "upgrades", "talismans", "favorites"]:
        clear_logic_cache(table)
    
    # Also clear master data to ensure any synced favorites are reflected
    try:
        from src.logic.master import get_master_data
        get_master_data.clear()
        from src.logic.talismans import load_talisman_master
        load_talisman_master.clear()
    except (ImportError, AttributeError):
        pass
