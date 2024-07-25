from database.models import User, UserHistory

def initialize_database():
    User.initialize_table()
    UserHistory.initialize_table()

if __name__ == "__main__":
    initialize_database()
