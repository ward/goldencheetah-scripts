import goldencheetah

import os
import datetime
import matplotlib.pyplot as plt
from io import BytesIO

DAYS = [7, 28, 84, 365]


def days_range(start_day, end_day):
    return [
        start_day + datetime.timedelta(days=days)
        for days in range((end_day - start_day).days + 1)
    ]


def calculate_rolling_total(number_of_days, first_day, per_day):
    rolling_per_day = {}
    for d in days_for_analysis:
        old_day = max(d - datetime.timedelta(days=number_of_days - 1), first_day)
        range_of_interest = days_range(old_day, d)
        total = 0
        for interesting_day in range_of_interest:
            total += per_day[interesting_day]
        rolling_per_day[d] = total
    return rolling_per_day


def get_rolling_svg(rolling, day_count):
    fig, ax = plt.subplots()
    ax.plot(days_for_analysis, [rolling[d] for d in days_for_analysis])
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    ax.set_title("Rolling {} Day Total".format(day_count))
    ax.minorticks_on()
    ax.grid(b=True, which="both", axis="y")

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format="svg")
    svg = tmpfile.getvalue().decode("utf-8")
    # Release memory
    plt.close(fig)

    # Remove the <?xml ...><!DOCTYPE svg ... > stuff at the start
    index_of_greater_than = svg.find(">") + 1
    index_of_greater_than = svg.find(">", index_of_greater_than) + 1
    return svg[index_of_greater_than:]


distance_per_day = goldencheetah.get_distance_per_day(sport="Run")
first_day = sorted(distance_per_day.keys())[0]

now = datetime.date.today()
six_months_ago = now - datetime.timedelta(days=500)
days_for_analysis = days_range(six_months_ago, now)
rolling_per_day = map(
    lambda number_of_days: calculate_rolling_total(
        number_of_days, first_day, distance_per_day
    ),
    DAYS,
)

# Default is [6.4, 4.8] (width, height)
plt.rcParams['figure.figsize'] = [10, 5]

svgs = "\n".join(map(get_rolling_svg, rolling_per_day, DAYS))
html = (
    "<!DOCTYPE html>"
    + "<html>"
    + '<head><meta charset="utf-8" />'
    + "<title>Rolling Total</title>"
    + "</head><body>"
    + svgs
    + "<footer><p>Generated on {}.</p></footer>".format(now)
    + "</body></html>"
)

try:
    os.mkdir("./output")
except FileExistsError:
    pass

NAME = "./output/rolling-total.html"
with open(NAME, "w") as f:
    f.write(html)
