from datetime import datetime
from database.connection import DatabaseConnection

class DailyAttempts:
    @staticmethod
    def initialize_table():
        with DatabaseConnection() as conn:
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
