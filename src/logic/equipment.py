import pandas as pd
from src.database.sqlite_manager import get_db_connection

def register_upgrade(weapon_type: str, element: str, series_skill: str, group_skill: str, count: int) -> int:
    """Registers a new skill upgrade in the database and returns its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO skill_upgrade (weapon_type, element, series_skill, group_skill, remaining_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (weapon_type, element, series_skill, group_skill, count))
        return cursor.lastrowid

def get_active_upgrades() -> pd.DataFrame:
    """Returns active upgrades as a DataFrame."""
    with get_db_connection() as conn:
        df = pd.read_sql_query('SELECT * FROM skill_upgrade WHERE remaining_count > 0 ORDER BY remaining_count ASC', conn)
    return df

def execute_upgrade(record_id: int, decrement: int = 1) -> bool:
    """Decrements remaining_count by decrement."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT remaining_count FROM skill_upgrade WHERE id=?", (record_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        new_count = max(0, row["remaining_count"] - decrement)
        cursor.execute("UPDATE skill_upgrade SET remaining_count=? WHERE id=?", (new_count, record_id))
        return True

def execute_all_upgrades(decrement: int) -> bool:
    """Decrements remaining_count by decrement for all active records."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE skill_upgrade 
            SET remaining_count = MAX(0, remaining_count - ?)
            WHERE remaining_count > 0
        ''', (decrement,))
        return True
