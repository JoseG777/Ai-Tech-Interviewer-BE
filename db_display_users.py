# UTILITY FUNCTION TO DISPLAY USERS INFO

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

def display_all_users():
    conn = get_connection()
    try:
        cursor = conn.execute('SELECT * FROM users')
        users = cursor.fetchall()

        if users:
            print("Users:")
            for user in users:
                print(f"UID: {user[0]}, Email: {user[1]}, LeetCode Username: {user[2]}, "
                      f"User Level Description: {user[3]}, Overall Ratio: {user[4]}, "
                      f"Easy Ratio: {user[5]}, Medium Ratio: {user[6]}, Hard Ratio: {user[7]}, "
                      f"Current Goal: {user[8]}")
        # , Upcoming Interview: {user[9]}, Signup: {user[10]}
        else:
            print("No users found.")
    except Exception as e:
        print(f"Error while fetching users: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    display_all_users()
