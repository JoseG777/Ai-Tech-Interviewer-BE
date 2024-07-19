import sqlitecloud
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configure SQLiteCloud connection
DATABASE_URL = os.getenv('SQLITECLOUD_CONN_STRING')
DATABASE_NAME = os.getenv('SQLITECLOUD_DB_NAME')


def get_connection():
    conn = sqlitecloud.connect(DATABASE_URL)
    conn.execute(f"USE DATABASE {DATABASE_NAME}")
    return conn


# This function will create the necessary tables if they don't exist
def initialize_database():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY NOT NULL,
            email TEXT UNIQUE NOT NULL,
            leetcode_username TEXT UNIQUE,
            user_level_description TEXT NOT NULL,
            overall_ratio FLOAT,
            easy_ratio FLOAT,
            medium_ratio FLOAT,
            hard_ratio FLOAT,
            current_goal TEXT,
            upcoming_interview TEXT,
            signup_date TEXT NOT NULL DEFAULT (datetime('now'))
        )
    ''')

    conn.commit()

    # Creates User History table
    # Note: Delete Cascade allows for any history saved for a deleted user will also be deleted.
    conn.execute('''
        CREATE TABLE IF NOT EXISTS userhistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        user_question TEXT NOT NULL,
        user_response TEXT NOT NULL,
        saved_response TEXT NOT NULL,
        saved_date TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


def add_user(user_id, email, lc, level, ovr, er, mr, hr):
    """
    Adding user into database based on given info and firebase authentication
    :param user_id: user's id from firebase
    :param email: valid user email
    :param lc: leetcode username
    :param level: level description
    :param ovr: overall ratio
    :param er: easy ration
    :param mr: medium ratio
    :param hr: hard ratio
    :return: will return true/false if user was created or not
    """
    conn = get_connection()
    signup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute('''
        INSERT INTO users (uid, email, leetcode_username, user_level_description, overall_ratio,
            easy_ratio, medium_ratio, hard_ratio, current_goal, upcoming_interview, signup_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(user_id, email, lc, level, ovr, er, mr, hr, None, None, signup_time))

    conn.commit()
    conn.close()


def get_user_id(uid):
    conn = get_connection()
    cursor = conn.execute('SELECT * FROM users WHERE uid = ?', (uid,))
    user = cursor.fetchone()
    conn.close()

    return user

def update_history(id, problem, response, evaluation):

    conn = get_connection()
    save_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur = conn.cursor()
    cur.execute('''INSERT INTO userhistory 
        (user_id, user_question, user_response, saved_response, saved_date) VALUES (?, ?, ?, ?)''',
    (id, problem, response, evaluation, save_date))
