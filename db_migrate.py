import sqlite3

connection = sqlite3.connect('tmp/database.db')
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        type TEXT NOT NULL,
        content TEXT NOT NULL,
        session_id INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

connection.commit()