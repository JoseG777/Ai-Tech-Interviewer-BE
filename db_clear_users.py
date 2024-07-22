# UTILITY FUNCTION TO CLEAR USERS

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

def clear_user_history():
    conn = get_connection()
    try:
        conn.execute("DELETE FROM userhistory")
        conn.commit()
    except Exception as e:
        print(f"Error while clearing the 'users' table: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    clear_users_table()
