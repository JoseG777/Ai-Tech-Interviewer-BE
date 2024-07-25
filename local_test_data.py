import sqlite3

DATABASE_PATH = "local_database.db"

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def insert_test_data(uid):
    conn = get_connection()
    try:
        conn.executemany("""
            INSERT INTO daily_attempts (user_id, date, count) VALUES
            (?, ?, ?)
        """, [
            (uid, '2024-07-21', 6),
            (uid, '2024-07-22', 10),
            (uid, '2024-07-23', 5),
            (uid, '2024-07-24', 8),
            (uid, '2024-07-25', 2),
            (uid, '2024-07-26', 3)
        ])
        conn.commit()
        print(f"Test data has been inserted into the 'daily_attempts' table for user_id {uid}.")
    except Exception as e:
        print(f"Error while inserting test data into the 'daily_attempts' table: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    # replace with your UID, get from local_display.py
    insert_test_data("LsAqtdlAKiRruTiPKbru0GoxaEH2")
