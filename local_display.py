import sqlite3

DATABASE_PATH = "local_database.db"

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def display_all_users():
    conn = get_connection()
    try:
        cursor = conn.execute('SELECT * FROM users')
        users = cursor.fetchall()

        if users:
            print("Users:")
            for user in users:
                print(
                      f"****************************************************************\n"
                      f"UID: {user[0]}, Email: {user[1]}, Username: {user[2]}, LeetCode Username: {user[3]}, "
                      f"User Level Description: {user[4]}, Overall Ratio: {user[5]}, "
                      f"Easy Ratio: {user[6]}, Medium Ratio: {user[7]}, Hard Ratio: {user[8]}, "
                      f"Current Goal: {user[9]}, Upcoming Interview: {user[10]}, Signup Date: {user[11]}"
                      f"\n****************************************************************\n")
        else:
            print("No users found.")
    except Exception as e:
        print(f"Error while fetching users: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    display_all_users()
