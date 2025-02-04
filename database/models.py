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
    def get_user_id(uid):
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

    @staticmethod
    def update_level(uid, new_level):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            cur.execute(
                """UPDATE users SET user_level_description = ? WHERE uid = ?""",
                (new_level, uid),
            )


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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(user_id, date),
                    FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE
                )
                """
            )
            conn.commit()

    @staticmethod
    def update_history(
        user_id,
        problem,
        response,
        code_evaluation,
        code_feedback,
        final_code_grade,
        speech_evaluation=None,
        speech_feedback=None,
        final_speech_grade=None,
    ):
        save_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with DatabaseConnection() as conn:
            conn.execute(
                """INSERT INTO userhistory 
                 (user_id, user_question, user_response, code_evaluation, code_feedback, final_code_grade, 
                 speech_evaluation, speech_feedback, final_speech_grade, saved_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    problem,
                    response,
                    code_evaluation,
                    code_feedback,
                    final_code_grade,
                    speech_evaluation,
                    speech_feedback,
                    final_speech_grade,
                    save_date,
                ),
            )
            conn.commit()

    @staticmethod
    def update_daily_attempts(user_id):
        save_date = datetime.now().strftime("%Y-%m-%d")
        with DatabaseConnection() as conn:
            conn.execute(
                """
                INSERT INTO daily_attempts (user_id, date, count)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, date)
                DO UPDATE SET count = count + 1
                """,
                (user_id, save_date),
            )
            conn.commit()

    @staticmethod
    def get_user_history(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            history = cur.execute(
                "SELECT user_question, user_response, "
                'COALESCE(code_evaluation, "N/A"), COALESCE(code_feedback, "N/A"), '
                'COALESCE(final_code_grade, "N/A"), COALESCE(speech_evaluation, "N/A"), '
                'COALESCE(speech_feedback, "N/A"), COALESCE(final_speech_grade, "N/A"), '
                'COALESCE(saved_date, "N/A") '
                "FROM userhistory WHERE user_id = ?",
                (uid,),
            ).fetchall()

        history_list = [
            {
                "user_question": record[0],
                "user_response": record[1],
                "code_evaluation": record[2],
                "code_feedback": record[3],
                "final_code_grade": record[4],
                "speech_evaluation": record[5],
                "speech_feedback": record[6],
                "final_speech_grade": record[7],
                "saved_date": record[8],
            }
            for record in history
        ]

        return history_list

    @staticmethod
    def get_code_grades(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            grades = cur.execute(
                "SELECT final_code_grade, saved_date FROM userhistory WHERE user_id = ? AND final_code_grade IS NOT NULL",
                (uid,),
            ).fetchall()

        grades_list = [
            {"final_code_grade": grade[0], "saved_date": grade[1]} for grade in grades
        ]

        return grades_list

    @staticmethod
    def get_speech_grades(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            grades = cur.execute(
                "SELECT final_speech_grade, saved_date FROM userhistory WHERE user_id = ? AND final_speech_grade IS NOT NULL",
                (uid,),
            ).fetchall()

        grades_list = [
            {"final_speech_grade": grade[0], "saved_date": grade[1]} for grade in grades
        ]

        return grades_list

    @staticmethod
    def count_history(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            records = cur.execute(
                "SELECT date, count FROM daily_attempts WHERE user_id = ?",
                (uid,),
            ).fetchall()

        attempts_list = [
            {"saved_date": record[0], "count": record[1]} for record in records
        ]

        return attempts_list
    
    
    @staticmethod
    def get_leetcode_stats(uid):
        with DatabaseConnection() as conn:
            cur = conn.cursor()
            lc_ratios = cur.execute(
                "SELECT overall_ratio, easy_ratio, medium_ratio, hard_ratio FROM users WHERE uid = ?",
                (uid,),
            ).fetchone()  

        if lc_ratios:
            lc_stats = [float(ratio) * 100 for ratio in lc_ratios] 
        else:
            lc_stats = [0.0, 0.0, 0.0, 0.0] 

        return lc_stats

