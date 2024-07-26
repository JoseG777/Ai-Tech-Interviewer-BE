import sqlite3

DATABASE_PATH = "local_database.db"

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def delete_user_by_uid(uid):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM users WHERE uid = ?", (uid,))
        conn.commit()
        print(f"User with UID {uid} has been deleted.")
    except Exception as e:
        print(f"Error while deleting user with UID {uid}: {str(e)}")
    finally:
        conn.close()

def clear_user_history():
    conn = get_connection()
    try:
        conn.execute("DELETE FROM userhistory")
        conn.commit()
        print("All entries in the 'userhistory' table have been deleted.")
    except Exception as e:
        print(f"Error while clearing the 'userhistory' table: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    delete_user_by_uid('')  
