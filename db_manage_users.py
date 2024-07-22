# UTILITY FUNCTION TO MANAGE USERS

import sqlitecloud
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('SQLITECLOUD_CONN_STRING')
DATABASE_NAME = os.getenv('SQLITECLOUD_DB_NAME')

def get_connection():
    conn = sqlitecloud.connect(DATABASE_URL)
    conn.execute(f"USE DATABASE {DATABASE_NAME}")
    return conn

def clear_users_table():
    conn = get_connection()
    try:
        conn.execute("DELETE FROM users")
        conn.commit() 
        print("All entries in the 'users' table have been deleted.")
    except Exception as e:
        print(f"Error while clearing the 'users' table: {str(e)}")
    finally:
        conn.close()

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

if __name__ == '__main__':
    # clear_users_table() 
    delete_user_by_uid('qeLQEOVDDHOVuY6jxnlyqdGD3bH2')  # Delete a specific user by UID
