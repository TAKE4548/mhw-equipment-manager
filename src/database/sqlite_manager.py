import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mhw_equipment.db")

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_upgrade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weapon_type TEXT NOT NULL,
                element TEXT NOT NULL,
                series_skill TEXT NOT NULL,
                group_skill TEXT NOT NULL,
                remaining_count INTEGER NOT NULL CHECK (remaining_count >= 0)
            )
        ''')

# Initialize DB on import
init_db()
