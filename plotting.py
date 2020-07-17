import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import datetime
import config
from io import BytesIO
import sqlite3
from statistics import mean

matplotlib.use('Agg')
READER = sqlite3.connect(config.DATABASE["filename"], check_same_thread=False, isolation_level=None)

def check_today_cases(countryname):
    if countryname == 'all':
        cases = READER.execute(
            f"SELECT todayCases FROM stats").fetchone()[0]
    else:
        cases = READER.execute(
            f"SELECT todayCases FROM countries WHERE country LIKE '%{countryname}%'").fetchone()[0]
    return int(cases)


# def check_all_cases(countryname='all'):
#     if countryname == 'all':
#         cases, deaths, recovered = READER.execute(
#             f"SELECT todayCases, todayDeaths, todayRecovered FROM stats").fetchone()
#     else:
#         cases, deaths, recovered = READER.execute(
#             f"SELECT todayCases, todayDeaths, todayRecovered FROM countries WHERE country LIKE '%{countryname}%'").fetchone()
#     return int(cases), int(deaths), int(recovered)

def historical_stats(country, days=30):
    response = requests.get(f"https://disease.sh/v3/covid-19/historical/{country}?lastdays={days}")
    return response


def history_graph(country):
    plt.figure(figsize=(10, 8))
    confirmed_cases = []
    dates = []
    deaths = []
    recovered = []

    if country == 'all':
        data = historical_stats(country, 15).json()
        plt.figure(figsize=(13, 11))
        # updated_cases, updated_deaths, updated_recovered = check_all_cases('all')
        plt.title('Worldwide', fontweight=config.PLOT['fontweight'], fontsize=22)
    else:
        data = historical_stats(country, 15).json()['timeline']
        plt.figure(figsize=(10, 8))
        # updated_cases = check_today_cases(country)
        plt.title(country, fontweight=config.PLOT['fontweight'], fontsize=22)

    for date, cases in data['cases'].items():
        date = datetime.datetime.strptime(date, '%m/%d/%y').date()
        dates.append(date)
        confirmed_cases.append(int(cases))

    for _, cases in data['deaths'].items():
        deaths.append(int(cases))

    for _, cases in data['recovered'].items():
        recovered.append(int(cases))

    # if recovered[-1] < updated_recovered or deaths[-1] < updated_deaths or confirmed_cases[-1] < updated_cases:
    #     deaths.append(updated_deaths)
    #     confirmed_cases.append(updated_cases)
    #     recovered.append(updated_recovered)
    #     dates.append(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0))
    offset = max(confirmed_cases)*0.03
    for date, cases_value in zip(dates, confirmed_cases):
        plt.annotate(
            str(cases_value),
            xy=(date, cases_value+offset),
            fontsize=config.PLOT['fontsize'],
            fontweight=config.PLOT['fontweight'],
            horizontalalignment='center',
            verticalalignment='center')

    for date, deaths_value, recovered_value in zip(dates, deaths, recovered):
        if deaths_value < recovered_value:
            deaths_y_offset = deaths_value-offset
            recovered_y_offset = recovered_value+offset
        else:
            deaths_y_offset = deaths_value+offset
            recovered_y_offset = recovered_value-offset

        plt.annotate(
            str(deaths_value),
            xy=(date, deaths_y_offset),
            fontsize=config.PLOT['fontsize'],
            fontweight=config.PLOT['fontweight'],
            color='red',
            horizontalalignment='center',
            verticalalignment='center')
        plt.annotate(
            str(recovered_value),
            xy=(date, recovered_y_offset),
            fontsize=config.PLOT['fontsize'],
            fontweight=config.PLOT['fontweight'],
            color='green',
            horizontalalignment='center',
            verticalalignment='center')

    plt.plot(dates, deaths, label="Deaths", color='red', linewidth=3, marker='o')
    plt.plot(dates, recovered, label="Recovered", color='green', linewidth=3, marker='o')
    plt.plot(dates, confirmed_cases, label="Confirmed", linewidth=3, marker='o')

    axes = plt.gca() # return the axes of the current figure
    formatter = mdates.DateFormatter('%d/%m')
    axes.xaxis.set_major_formatter(formatter)

    plt.grid(True) # show grid on the plot
    plt.xticks(dates, rotation=45)
    # naming the x axis
    plt.xlabel('Dates')
    # naming the y axis
    plt.ylabel('Cases')
    # show a legend on the plot
    plt.legend()
    if mean(recovered) >= mean(deaths):
        plt.fill_between(dates, confirmed_cases, recovered, alpha=0.2)
        plt.fill_between(dates, recovered, deaths, alpha=0.2, color='green')
        plt.fill_between(dates, deaths, alpha=0.2, color='red')
    else:
        plt.fill_between(dates, confirmed_cases, deaths, alpha=0.2)
        plt.fill_between(dates, deaths, recovered, alpha=0.2, color='red')
        plt.fill_between(dates, recovered, alpha=0.2, color='green')

    in_memory_buffer = BytesIO()
    plt.savefig(in_memory_buffer, format="png", dpi=300)
    in_memory_buffer.seek(0)
    plt.cla()
    plt.close()
    return in_memory_buffer


def graph_per_day(country):
    confirmed_cases = []
    dates = []

    if country == 'all':
        data = historical_stats(country, 30).json()
        plt.figure(figsize=(15, 11))
        updated_cases = check_today_cases('all')
        plt.title('Worldwide', fontweight=config.PLOT['fontweight'], fontsize=22)
    else:
        data = historical_stats(country, 30).json()['timeline']
        plt.figure(figsize=(15, 8))
        updated_cases = check_today_cases(country)
        plt.title(country, fontweight=config.PLOT['fontweight'], fontsize=22)

    for date, cases in data['cases'].items():
        date = datetime.datetime.strptime(date, '%m/%d/%y').date()
        dates.append(date)
        confirmed_cases.append(int(cases))

    confirmed_cases.reverse()
    for index, cases_count in enumerate(confirmed_cases):
        if index == len(confirmed_cases)-1:
            pass
        elif cases_count - confirmed_cases[index+1] < 0: # if total cases of one day are less than the previous day
            confirmed_cases[index] = 0
        else:
            confirmed_cases[index] = cases_count - confirmed_cases[index+1]
    confirmed_cases.reverse()
    confirmed_cases.pop(0)
    dates.pop(0)

    if updated_cases > 0 and country != 'all':
        yesterday = datetime.date.today() - datetime.timedelta(1)
        if dates[-1] != yesterday:
            confirmed_cases.append(updated_cases)
            dates.append(yesterday)
        else:
            confirmed_cases.append(updated_cases)
            dates.append(datetime.date.today())

    for date, cases_value in zip(dates, confirmed_cases):
        plt.annotate(
            str(cases_value),
            xy=(date, cases_value+(max(confirmed_cases)*0.03)),
            fontsize=config.PLOT['fontsize'],
            fontweight=config.PLOT['fontweight'],
            horizontalalignment='center',
            verticalalignment='center')

    plt.plot(dates, confirmed_cases, label="Confirmed", linewidth=3, marker='o')

    axes = plt.gca() # return the axes of the current figure
    formatter = mdates.DateFormatter('%d/%m')
    axes.xaxis.set_major_formatter(formatter)

    plt.grid(True) # show grid on the plot
    plt.xticks(dates, rotation=45)
    # naming the x axis
    plt.xlabel('Dates')
    # naming the y axis
    plt.ylabel('Cases')
    plt.fill_between(dates, confirmed_cases, alpha=0.3)

    in_memory_buffer = BytesIO()
    plt.savefig(in_memory_buffer, format="png", dpi=300)
    in_memory_buffer.seek(0)
    plt.cla()
    plt.close()
    return in_memory_buffer
