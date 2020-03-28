import sqlite3
import config

conn = sqlite3.connect(config.database["filename"])

c = conn.cursor()

with conn:
    c.execute("""CREATE TABLE IF NOT EXISTS stats (
            cases INTEGER,
            deaths INTEGER,
            recovered INTEGER,
            updated INTEGER,
            active INTEGER
        )""")

with conn:
    c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER NOT NULL PRIMARY KEY,
            username STRING,
            started_date DATE,
            last_check DATETIME,
            language VARCHAR(3)
        )""")

