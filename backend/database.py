import sqlite3
from sqlite3 import Connection
from pathlib import Path

DB_PATH = Path(__file__).parent / "inventory.db"

def get_db() -> Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
