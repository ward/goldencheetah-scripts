# Because I do not like how GC only calculates it on days you run.

import datetime
import pathlib
import matplotlib.pyplot as plt
from io import BytesIO

DAYS = [7, 28, 84, 365]


def days_range(start_day, end_day):
    return [
        start_day + datetime.timedelta(days=days)
        for days in range((end_day - start_day).days + 1)
    ]


def selected_days():
    data = GC.seasonMetrics()
    return days_range(data["date"][0], data["date"][-1])


def calculate_rolling_total(number_of_days):
    rolling_per_day = {}
    for d in days_for_analysis:
        old_day = max(d - datetime.timedelta(days=number_of_days - 1), all_days[0])
        range_of_interest = days_range(old_day, d)
        total = 0
        for interesting_day in range_of_interest:
            total += per_day[interesting_day]
        rolling_per_day[d] = total
    return rolling_per_day


def get_rolling_svg(rolling):
    fig, ax = plt.subplots()
    ax.plot(days_for_analysis, [rolling[d] for d in days_for_analysis])
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    ax.set_title("Rolling Total")
    ax.minorticks_on()
    ax.grid(b=True, which="both", axis="y")

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format="svg")
    svg = tmpfile.getvalue().decode("utf-8")
    # Release memory
    plt.close(fig)

    return svg


DATA = GC.seasonMetrics(all=True)
all_days = days_range(DATA["date"][0], DATA["date"][-1])
per_day = {}
for d in all_days:
    per_day[d] = 0
for i in range(len(DATA["Distance"])):
    if DATA["Sport"][i] == "Run":
        per_day[DATA["date"][i]] += DATA["Distance"][i]

days_for_analysis = selected_days()
rolling_per_day = map(calculate_rolling_total, DAYS)

svgs = (chr(10)).join(map(get_rolling_svg, rolling_per_day))
html = "<html><body>" + svgs + "</body></html>"

NAME = "/tmp/gc-rolling-total.html"
with open(NAME, "w") as f:
    f.write(html)
GC.webpage(pathlib.Path(NAME).as_uri())
