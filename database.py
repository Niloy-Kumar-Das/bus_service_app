import sqlite3

DB_NAME = "bus_service.db"

def init_db():
    """Initialize the database and create tables if they don't exist."""
    with sqlite3.connect(DB_NAME) as conn:
        with open("schema.sql", "r") as schema_file:
            conn.executescript(schema_file.read())
    print("Database initialized successfully!")

def get_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_NAME)
