import matplotlib.pyplot as plt
import datetime
import os
from io import BytesIO

import goldencheetah


def sum_per_month(list_of_runs):
    """Every run is an Activity, just start counting distance. Not very generic evidently."""
    months = {}
    for run in runs:
        month = "{}-{}".format(run.date.year, run.date.month)
        try:
            months[month] += run.distance
        except KeyError:
            months[month] = run.distance
    return months


def sum_per_year(list_of_runs):
    per_year = {}
    for run in runs:
        # Turning to string for consistency with the other summing.
        # Specifically it otherwise confuses matplotlib's bar coordinates.
        # The string one would go 0..len()-1, while this otherwise would go
        # lowest_year..highest_year
        year = str(run.date.year)
        try:
            per_year[year] += run.distance
        except KeyError:
            per_year[year] = run.distance
    return per_year


def sum_week(week_of_runs):
    sum = 0
    for day, runs_on_day in week_of_runs.items():
        for run in runs_on_day:
            sum += run.distance
    return sum


runs = goldencheetah.get_all_activities(sport="Run")
per_month = sum_per_month(runs)
per_year = sum_per_year(runs)
runs = goldencheetah.group_by_week(runs)

for week in runs.keys():
    runs[week] = sum_week(runs[week])

# Now we have a dict with
# Keys: "2022-22" as week names
# Values: Distance summed up


def create_svg(distance_per_time, timeframe):
    fig, ax = plt.subplots()
    time_units = list(distance_per_time.keys())[-20:]
    distances = [distance_per_time[time_unit] for time_unit in time_units]
    ax.bar(time_units, distances)

    # Put values on the bars
    for i in range(len(time_units)):
        ax.text(
            i,
            distances[i],
            int(distances[i]),
            horizontalalignment="center",
            fontsize="small",
        )

    ax.grid(axis="y")
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    ax.set_title("Distance per {}".format(timeframe))
    second_axis = ax.secondary_yaxis("right")
    second_axis.set_ylabel("Distance (km)")
    plt.xticks(rotation=90)
    # ax.minorticks_on()

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format="svg")
    svg = tmpfile.getvalue().decode("utf-8")
    # Release memory
    plt.close(fig)

    # Remove the <?xml ...><!DOCTYPE svg ... > stuff at the start
    index_of_greater_than = svg.find(">") + 1
    index_of_greater_than = svg.find(">", index_of_greater_than) + 1
    return svg[index_of_greater_than:]

# Change the plot sizes
# Default is [6.4, 4.8] (width, height)
plt.rcParams["figure.figsize"] = [10, 6]
# SVG font defaults to "path", making it look the same in every viewer.
# Setting it to none makes it use actual text so font choice is left to the viewer.
# plt.rcParams["svg.fonttype"] = "none"

now = datetime.date.today()
html = (
    "<!DOCTYPE html>"
    + "<html>"
    + '<head><meta charset="utf-8" />'
    + "<title>Distance per week</title>"
    + "</head><body>"
    + create_svg(runs, "week")
    + create_svg(per_month, "month")
    + create_svg(per_year, "year")
    + "<footer><p>Generated on {}.</p></footer>".format(now)
    + "</body></html>"
)

try:
    os.mkdir("./output")
except FileExistsError:
    pass

NAME = "./output/distancepertime.html"
with open(NAME, "w") as f:
    f.write(html)
