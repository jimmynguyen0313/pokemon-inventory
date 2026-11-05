import os
import sqlite3
from sqlite3 import Connection
from pathlib import Path

# Override with DATABASE_PATH to store the SQLite file elsewhere (e.g. a mounted disk).
DB_PATH = Path(os.getenv("DATABASE_PATH", Path(__file__).parent / "inventory.db"))

def get_db() -> Connection:
    # Read the module attribute at call time so tests can point it at a temp file.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
