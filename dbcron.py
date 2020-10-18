import requests
from dbmodels import GlobalStats, CountryStats
import datetime
import config
import time


def global_stats():
    now = datetime.datetime.now()
    response = requests.get("https://disease.sh/v3/covid-19/all")
    data = response.json()
    GlobalStats.delete().execute()
    GlobalStats.create(
        cases=data['cases'],
        todayCases=data['todayCases'],
        deaths=data['deaths'],
        todayDeaths=data['todayDeaths'],
        recovered=data['recovered'],
        todayRecovered=data['todayRecovered'],
        active=data['active'],
        updated=convert_updated(data['updated'])
    )

    print(f'General data updated: {now.strftime("%Y-%m-%d %H:%M:%S")}')


def all_countries():
    response = requests.get("https://disease.sh/v3/covid-19/countries?sort=cases")
    data = response.json()
    CountryStats.delete().execute()
    for country in data:
        if "'" in country["country"]:
            country["country"] = country["country"].replace("'", "''")
        CountryStats.create(
            country = country["country"], 
            cases = country["cases"], 
            todayCases = country["todayCases"], 
            deaths = country["deaths"], 
            todayDeaths = country["todayDeaths"], 
            recovered = country["recovered"],
            todayRecovered = country["todayRecovered"],
            critical = country["critical"],
            active = country["active"],
            casesPerOneMillion = country["casesPerOneMillion"],
            tests = country["tests"],
            updated = convert_updated(country["updated"])
        )
    now = datetime.datetime.now()
    print(f'Data for countries updated: {now.strftime("%Y-%m-%d %H:%M:%S")}')


def convert_updated(milliseconds):
    seconds, _ = divmod(milliseconds, 1000)
    timedate = datetime.datetime.fromtimestamp(seconds)
    return timedate


global_stats()
time.sleep(2)
all_countries()
