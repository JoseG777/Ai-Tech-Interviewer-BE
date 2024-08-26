from database.models import User, UserHistory, DailyAttempts

def initialize_database():
    User.initialize_table()
    UserHistory.initialize_table()
    DailyAttempts.initialize_table()
