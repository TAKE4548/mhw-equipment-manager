import pytest
import pandas as pd
from src.database.storage_manager import MANAGED_TABLES

# We can't easily test the internal 'columns_map' of pull_cloud_to_local 
# because it's defined inside the function.
# But we can test the expected columns for Talismans and Favorites logic.

def test_talisman_column_consistency():
    from src.logic.talismans import TALISMANS_COLUMNS
    
    expected_cols = [
        "id", "rarity",
        "skill_1_name", "skill_1_level",
        "skill_2_name", "skill_2_level",
        "skill_3_name", "skill_3_level",
        "weapon_slot_level",
        "armor_slot_1_level", "armor_slot_2_level", "armor_slot_3_level",
        "is_favorite"
    ]
    
    for col in expected_cols:
        assert col in TALISMANS_COLUMNS, f"Column {col} missing in TALISMANS_COLUMNS"

def test_favorites_column_consistency():
    from src.logic.favorites import FAVORITES_COLUMNS
    
    expected_cols = ["id", "favorite_type", "skill_value"]
    for col in expected_cols:
        assert col in FAVORITES_COLUMNS, f"Column {col} missing in FAVORITES_COLUMNS"

# This test targets the bug in storage_manager.py indirectly by checking what logic expects vs what storage yields.
# However, the direct fix is in the code. I'll add a test that checks if the pull function can handle full schemas.
