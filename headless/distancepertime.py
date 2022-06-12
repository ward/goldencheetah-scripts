import matplotlib.pyplot as plt
import datetime
import os
from io import BytesIO

import goldencheetah

runs = goldencheetah.get_all_activities(sport="Run")
runs = goldencheetah.group_by_week(runs)


def sum_week(week_of_runs):
    sum = 0
    for day, runs_on_day in week_of_runs.items():
        for run in runs_on_day:
            sum += run.distance
    return sum


for week in runs.keys():
    runs[week] = sum_week(runs[week])

# Now we have a dict with
# Keys: "2022-22" as week names
# Values: Distance summed up


def create_svg(distance_per_week):
    fig, ax = plt.subplots()
    weeks = list(distance_per_week.keys())[-20:]
    ax.bar(weeks, [distance_per_week[week] for week in weeks])
    ax.grid(axis='y')
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    ax.set_title("Distance per week")
    plt.xticks(rotation=45)
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


now = datetime.date.today()
html = (
    "<!DOCTYPE html>"
    + "<html>"
    + '<head><meta charset="utf-8" />'
    + "<title>Distance per week</title>"
    + "</head><body>"
    + create_svg(runs)
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
