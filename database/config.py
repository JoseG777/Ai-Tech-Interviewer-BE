import os
from dotenv import load_dotenv

load_dotenv()

# Configure SQLiteCloud connection
DATABASE_URL = os.getenv("SQLITECLOUD_CONN_STRING")
DATABASE_NAME = os.getenv("SQLITECLOUD_DB_NAME")
