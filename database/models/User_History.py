from datetime import datetime
from database.connection import DatabaseConnection

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
