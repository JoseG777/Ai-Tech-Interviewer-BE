from database.models import User, UserHistory


def initialize_database():
    User.initialize_table()
    UserHistory.initialize_table()
