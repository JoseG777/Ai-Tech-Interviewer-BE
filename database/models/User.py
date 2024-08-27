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
                    username TEXT UNIQUE NOT NULL,
                    leetcode_username TEXT,
                    user_level_description TEXT NOT NULL,
                    overall_ratio FLOAT DEFAULT 0.0,
                    easy_ratio FLOAT DEFAULT 0.0,
                    medium_ratio FLOAT DEFAULT 0.0,
                    hard_ratio FLOAT DEFAULT 0.0,
                    beginner_topics TEXT,  -- Comma-separated list of topics
                    intermediate_topics TEXT,  -- Comma-separated list of topics
                    advanced_topics TEXT,  -- Comma-separated list of topics
                    has_taken_exam BOOLEAN DEFAULT 0,  -- Boolean field for exam status
                    current_goal TEXT,
                    upcoming_interview TEXT,
                    signup_date TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.commit()

    @staticmethod
    def add_user(user_id, username, email, lc, level):
        signup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with DatabaseConnection() as conn:
            conn.execute(
                """
                INSERT INTO users (uid, email, username, leetcode_username, user_level_description, overall_ratio,
                    easy_ratio, medium_ratio, hard_ratio, current_goal, upcoming_interview, signup_date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    email,
                    username,
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
    def get_user(uid):
        with DatabaseConnection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE uid = ?", (uid,))
            user = cursor.fetchone()
        return user

    @staticmethod
    def get_email(username):
        with DatabaseConnection() as conn:
            cur = conn.execute(
                "SELECT email FROM users WHERE username = ?", (username,)
            )
            email = cur.fetchone()

        return email
    
    @staticmethod
    def get_exam_status(uid):
        with DatabaseConnection() as conn:
            cursor = conn.execute(
                "SELECT has_taken_exam FROM users WHERE uid = ?", (uid,)
            )
            exam_status = cursor.fetchone()
        return exam_status[0] if exam_status else None

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
            conn.commit()
    
    @staticmethod
    def update_skill_levels(uid, beginner_topics, intermediate_topics, advanced_topics):
        with DatabaseConnection() as conn:
            conn.execute(
                """
                UPDATE users 
                SET beginner_topics = ?, intermediate_topics = ?, advanced_topics = ?, has_taken_exam = 1
                WHERE uid = ?""",
                (",".join(beginner_topics), ",".join(intermediate_topics), ",".join(advanced_topics), uid)
            )
            conn.commit()

    @staticmethod
    def remove_user(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE uid = ?", (uid,))
            conn.commit()

    @staticmethod
    def update_goal(uid, new_goal):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute(
                """UPDATE users SET current_goal = ? WHERE uid = ?""", (new_goal, uid)
            )
            conn.commit()

    @staticmethod
    def update_interview(uid, new_interview):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute(
                """UPDATE users SET upcoming_interview = ? WHERE uid = ?""",
                (new_interview, uid),
            )
            conn.commit()

    @staticmethod
    def update_level(uid, new_level):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute(
                """UPDATE users SET user_level_description = ? WHERE uid = ?""",
                (new_level, uid),
            )
            conn.commit()
