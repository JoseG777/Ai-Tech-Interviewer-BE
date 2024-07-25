import sqlite3
from contextlib import contextmanager

DATABASE_PATH = "local_database.db" 

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

@contextmanager
def DatabaseConnection():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
