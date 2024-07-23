from datetime import datetime
from database.connection import DatabaseConnection


class User:
    @staticmethod
    def initialize_table():
        with DatabaseConnection() as conn:
            conn.execute(
                """
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
                """
            )
            conn.commit()

    @staticmethod
    def add_user(user_id, email, lc, level):
        signup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with DatabaseConnection() as conn:
            conn.execute(
                """
                INSERT INTO users (uid, email, leetcode_username, user_level_description, overall_ratio,
                    easy_ratio, medium_ratio, hard_ratio, current_goal, upcoming_interview, signup_date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    email,
                    lc,
                    level,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    signup_time,
                ),
            )
            conn.commit()

    @staticmethod
    def get_user_id(uid):
        with DatabaseConnection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE uid = ?", (uid,))
            user = cursor.fetchone()
        return user

    @staticmethod
    def update_user(
        uid,
        leetcode_username,
        coding_level,
        goal,
        upcoming_interview,
        overall_ratio=None,
        easy_ratio=None,
        medium_ratio=None,
        hard_ratio=None,
    ):
        # print(f"Executing update for user {uid}")
        with DatabaseConnection() as conn:
            conn.execute(
                """
                UPDATE users 
                SET leetcode_username = ?, user_level_description = ?, current_goal = ?, upcoming_interview = ?, 
                    overall_ratio = ?, easy_ratio = ?, medium_ratio = ?, hard_ratio = ?
                WHERE uid = ?""",
                (
                    leetcode_username,
                    coding_level,
                    goal,
                    upcoming_interview,
                    overall_ratio,
                    easy_ratio,
                    medium_ratio,
                    hard_ratio,
                    uid,
                ),
            )

            # print(f"Update executed successfully for user {uid}")
            conn.commit()

    @staticmethod
    def remove_user(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM users WHERE uid = ?', (uid,))
            conn.commit()

    @staticmethod
    def update_goal(uid, new_goal):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute('''UPDATE users SET current_goal = ? WHERE uid = ?''', (new_goal, uid))
            conn.commit()

    @staticmethod
    def update_interview(uid, new_interview):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute('''UPDATE users SET upcoming_interview = ? WHERE uid = ?''', (new_interview, uid))

    @staticmethod
    def update_level(uid, new_level):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute('''UPDATE users SET user_level_description = ? WHERE uid = ?''', (new_level, uid))


class UserHistory:
    @staticmethod
    def initialize_table():
        with DatabaseConnection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS userhistory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_question TEXT NOT NULL,
                    user_response TEXT NOT NULL,
                    code_evaluation TEXT NOT NULL,
                    code_feedback TEXT NOT NULL,
                    final_code_grade INTEGER NOT NULL,
                    speech_evaluation TEXT,
                    speech_feedback TEXT,
                    final_speech_grade INTEGER,
                    saved_date TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
                )
                """
            )
            conn.commit()

    @staticmethod
    def update_history(user_id, problem, response, code_evaluation, code_feedback, final_code_grade,
                       speech_evaluation=None, speech_feedback=None, final_speech_grade=None):
        save_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with DatabaseConnection() as conn:
            conn.execute(
                """INSERT INTO userhistory 
                 (user_id, user_question, user_response, code_evaluation, code_feedback, final_code_grade, 
                 speech_evaluation, speech_feedback, final_speech_grade, saved_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?""",
                (user_id, problem, response, code_evaluation, code_feedback, final_code_grade,
                 speech_evaluation, speech_feedback, final_speech_grade, save_date)
            )
            conn.commit()

    @staticmethod
    def get_code_grades(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            grades = cur.execute('SELECT final_code_grade, saved_date FROM userhistory WHERE user_id = ?', (uid,)).fetchall()

        # return the final grade of an assignment & its saved date
        if grades is not None:
            grades_list = [{'final_code_grade': grade['final_code_grade'], 'saved_date': grade['saved_date']} for grade in grades]
        else:
            # if user has no final grades, return empty list
            grades_list = []

        return grades_list

    @staticmethod
    def get_speech_grades(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            grades = cur.execute('SELECT final_speech_grade, saved_date FROM userhistory WHERE user_id = ?', (uid,)).fetchall()

        # return the final grade of an assignment & its saved date
        if grades is not None:
            grades_list = [{'final_speech_grade': grade['final_speech_grade'], 'saved_date': grade['saved_date']} for grade in grades]
        else:
            # if user has no final grades, return empty list
            grades_list = []

        return grades_list

    @staticmethod
    def count_history(uid):
        # will fetch user history for number of attempts per save date (for coding attempts)
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT final_code_grade, saved_date FROM userhistory WHERE user_id = ?", (uid,))
            records = cur.fetchall()

            if records is not None:
                # Count occurrences of each saved date
                attempts_count = {}
                for record in records:
                    saved_date = record[1]
                    if saved_date in attempts_count:
                        attempts_count[saved_date] += 1
                    else:
                        attempts_count[saved_date] = 1

                # Convert dictionary to list of dictionaries
                attempts_list = [{'saved_date': date, 'count': count} for date, count in attempts_count.items()]
            else:
                attempts_list = []

            return attempts_list


