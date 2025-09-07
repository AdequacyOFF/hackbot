import sqlite3
from contextlib import closing
from config import settings
from .schema import SCHEMA_SQL

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_schema():
    with closing(connect()) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()