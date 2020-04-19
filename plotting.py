
import matplotlib.pyplot as plt
import requests
from datetime import datetime


def create_graph(country):
    plt.figure(figsize=(10, 8))
    response = requests.get(f"https://corona.lmao.ninja/v2/historical/{country}?lastdays=15")
    data = response.json()
    confirmed_cases = []
    dates = []
    deaths = []
    recovered = []
    for date, cases in data['timeline']['cases'].items():
        date = datetime.strptime(date, '%m/%d/%y')
        date = datetime.strftime(date, '%d/%m')
        dates.append(date)
        confirmed_cases.append(int(cases))

    for date, cases in data['timeline']['deaths'].items():
        deaths.append(int(cases))

    for date, cases in data['timeline']['recovered'].items():
        recovered.append(int(cases))

    plt.plot(dates, confirmed_cases, label="Confirmed", linewidth=3, marker='o')  

    for date, cases_value in zip(dates, confirmed_cases):
        plt.annotate(
            str(cases_value),
            xy=(date, cases_value+(max(confirmed_cases)*0.03)),
            fontsize=9,
            fontweight='bold',
            horizontalalignment='center',
            verticalalignment='bottom')

    plt.plot(dates, deaths, label="Deaths", color='red', linewidth=3, marker='o')

    for date, cases_value in zip(dates, deaths):
        plt.annotate(
            str(cases_value),
            xy=(date, cases_value-(max(confirmed_cases)*0.03)),
            fontsize=9,
            fontweight='bold',
            color='red',
            horizontalalignment='center',
            verticalalignment='top')

    plt.plot(dates, recovered, label="Recovered", color='green', linewidth=3, marker='o')

    for date, cases_value in zip(dates, recovered):
        plt.annotate(
            str(cases_value),
            xy=(date, cases_value+(max(confirmed_cases)*0.03)),
            fontsize=9,
            fontweight='bold',
            color='green',
            horizontalalignment='center',
            verticalalignment='bottom')

    plt.grid(True)
    plt.xticks(dates, rotation=45)
    plt.title(data['country'], fontweight='bold')
    # naming the x axis
    plt.xlabel('Dates')
    # naming the y axis
    plt.ylabel('Cases')
    # show a legend on the plot
    plt.legend()
    # function to show the plot
    filepath = f'plots/{country}.png'
    plt.savefig(filepath, dpi=300)
    plt.close()
    plt.clf()
    return filepath

