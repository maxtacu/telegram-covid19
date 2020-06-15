import sqlite3
import config

WRITER = sqlite3.connect(config.DATABASE["filename"], isolation_level=None)

WRITER.execute("""CREATE TABLE IF NOT EXISTS stats (
            cases INTEGER,
            todayCases INTEGER,
            deaths INTEGER,
            todayDeaths INTEGER,
            recovered INTEGER,
            todayRecovered INTEGER,
            active INTEGER,
            updated TEXT
        )""")

WRITER.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER NOT NULL PRIMARY KEY,
            username STRING,
            started_date DATE,
            last_check DATETIME,
            language VARCHAR(3)
        )""")

WRITER.execute("""CREATE TABLE IF NOT EXISTS countries (
            country VARCHAR(15) NOT NULL PRIMARY KEY,
            cases INTEGER,
            todayCases INTEGER,
            deaths INTEGER,
            todayDeaths INTEGER,
            recovered INTEGER,
            critical INTEGER,
            active INTEGER,
            tests INTEGER,
            updated DATETIME
        )""")

WRITER.execute("""CREATE TABLE IF NOT EXISTS notifications (
            user_id INTEGER NOT NULL,
            username STRING,
            country VARCHAR(15) NOT NULL,
            added DATETIME
        )""")
        