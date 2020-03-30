import requests
import sqlite3
import datetime
import config

conn = sqlite3.connect(config.database["filename"], check_same_thread=False)


def update_database():
    now = datetime.datetime.now()
    response = requests.get("https://corona.lmao.ninja/all")
    data = response.json()
    c = conn.cursor()
    with conn:
        c.execute("DELETE FROM stats")
        c.execute(f"""INSERT INTO stats VALUES (
                    '{data['cases']}', 
                    '{data['deaths']}', 
                    '{data['recovered']}', 
                    '{data['active']}',
                    '{convert_updated(data['updated'])}')""")

    print(f'Data updated: {now.strftime("%Y-%m-%d %H:%M:%S")}')


def convert_updated(milliseconds):
    seconds, _ = divmod(milliseconds, 1000)
    timedate = datetime.datetime.fromtimestamp(seconds)
    return timedate


update_database()
