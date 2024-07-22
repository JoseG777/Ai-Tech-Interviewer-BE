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
                evaluation TEXT NOT NULL,
                feedback TEXT NOT NULL,
                final_grade TEXT NOT NULL,
                saved_date TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
                )
                """
            )
            conn.commit()

    @staticmethod
    def update_history(id, problem, response, evaluation, feedback, final_grade):
        save_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with DatabaseConnection() as conn:
            conn.execute(
                """INSERT INTO userhistory 
                (user_id, user_question, user_response, evaluation, 
                feedback, final_grade, saved_date) VALUES (?, ?, ?, ?, ?)""",
                (id, problem, response, evaluation, feedback, final_grade, save_date),
            )
            conn.commit()

    @staticmethod
    def get_grades(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            grades = cur.execute('SELECT final_grade, saved_date FROM userhistory WHERE user_id = ?', (uid,)).fetchall()

        return grades
