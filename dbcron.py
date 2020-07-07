import requests
import sqlite3
import datetime
import config
import time


WRITER = sqlite3.connect(config.DATABASE["filename"], check_same_thread=False, isolation_level=None)


def global_stats():
    now = datetime.datetime.now()
    response = requests.get("https://corona.lmao.ninja/v2/all")
    data = response.json()
    WRITER.execute("DELETE FROM stats")
    WRITER.execute(f"""INSERT INTO stats VALUES (
                    '{data['cases']}', 
                    '{data['todayCases']}', 
                    '{data['deaths']}',
                    '{data['todayDeaths']}',
                    '{data['recovered']}',
                    '{data['todayRecovered']}',
                    '{data['active']}',
                    '{convert_updated(data['updated'])}')""")

    print(f'General data updated: {now.strftime("%Y-%m-%d %H:%M:%S")}')


def all_countries():
    response = requests.get("https://corona.lmao.ninja/v2/countries?sort=cases")
    data = response.json()
    WRITER.execute("DELETE FROM countries")
    for country in data:
        if "'" in country["country"]:
            country["country"] = country["country"].replace("'", "''")
        WRITER.execute(f"""INSERT INTO countries VALUES (
                    '{country["country"]}', 
                    '{country["cases"]}', 
                    '{country["todayCases"]}', 
                    '{country["deaths"]}', 
                    '{country["todayDeaths"]}', 
                    '{country["recovered"]}',
                    '{country["todayRecovered"]}',
                    '{country["critical"]}',
                    '{country["active"]}',
                    '{country["tests"]}',
                    '{convert_updated(country["updated"])}')""")
    now = datetime.datetime.now()
    print(f'Data for countries updated: {now.strftime("%Y-%m-%d %H:%M:%S")}')


def convert_updated(milliseconds):
    seconds, _ = divmod(milliseconds, 1000)
    timedate = datetime.datetime.fromtimestamp(seconds)
    return timedate


global_stats()
time.sleep(3)
all_countries()
