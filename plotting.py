
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
from datetime import datetime
import config
from io import BytesIO
from threading import Lock

matplotlib.use('Agg')
LOCK = Lock()


def create_graph(country):
    with LOCK:
        plt.figure(figsize=(10, 8))
        response = requests.get(f"https://corona.lmao.ninja/v2/historical/{country}?lastdays=15")
        data = response.json()
        confirmed_cases = []
        dates = []
        deaths = []
        recovered = []
        for date, cases in data['timeline']['cases'].items():
            date = datetime.strptime(date, '%m/%d/%y')
            dates.append(date)
            confirmed_cases.append(int(cases))

        for date, cases in data['timeline']['deaths'].items():
            deaths.append(int(cases))

        for date, cases in data['timeline']['recovered'].items():
            recovered.append(int(cases))

        for date, cases_value in zip(dates, confirmed_cases):
            plt.annotate(
                str(cases_value),
                xy=(date, cases_value+(max(confirmed_cases)*0.03)),
                fontsize=config.PLOT['fontsize'],
                fontweight=config.PLOT['fontweight'],
                horizontalalignment='center',
                verticalalignment='center')

        for date, deaths_value, recovered_value in zip(dates, deaths, recovered):
            if deaths_value < recovered_value:
                deaths_y_offset = deaths_value-(max(confirmed_cases)*0.03)
                recovered_y_offset = recovered_value+(max(confirmed_cases)*0.03)
            else:
                deaths_y_offset = deaths_value+(max(confirmed_cases)*0.03)
                recovered_y_offset = recovered_value-(max(confirmed_cases)*0.03)

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
        plt.title(data['country'], fontweight=config.PLOT['fontweight'])
        # naming the x axis
        plt.xlabel('Dates')
        # naming the y axis
        plt.ylabel('Cases')
        # show a legend on the plot
        plt.legend()

        in_memory_buffer = BytesIO()
        plt.savefig(in_memory_buffer, format="png", dpi=300)
        in_memory_buffer.seek(0)
        return in_memory_buffer
