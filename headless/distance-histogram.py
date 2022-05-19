import math
import datetime
from io import BytesIO
import os

import matplotlib.pyplot as plt

import goldencheetah


def seconds_to_hours_minutes(seconds):
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds - (hours * 3600)) / 60)
    return (hours, minutes)


runs = goldencheetah.get_all_activities(sport="Run")

# Lazier than looping ourselves, probably a bit slower though.
longest_distance_runs = sorted(runs, key=lambda a: a.distance, reverse=True)
longest_time_runs = sorted(runs, key=lambda a: a.time_moving, reverse=True)

# for run in longest_distance_runs[:10]:
#     print(run.distance, run.date)

# for run in longest_time_runs[:10]:
#     print(seconds_to_hours_minutes(run.time_moving), run.date)


# Some copy pasting of rolling-total.py
def create_distance_histogram(distances):
    fig, axs = plt.subplots()
    # +1 for rounding down, +1 for range
    bins = list(range(int(max(distances)) + 2))
    # Bin is [low, high[
    axs.hist(distances, bins=bins, log=True)
    axs.set_xlabel("Length of run (km)")
    axs.set_ylabel("Number of runs")
    # None makes matplotlib take its own default
    axs.set_ylim([1, None])
    axs.minorticks_on()

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format="svg")
    svg = tmpfile.getvalue().decode("utf-8")
    # Release memory
    plt.close(fig)

    # Remove the <?xml ...><!DOCTYPE svg ... > stuff at the start
    index_of_greater_than = svg.find(">") + 1
    index_of_greater_than = svg.find(">", index_of_greater_than) + 1
    return svg[index_of_greater_than:]


distance_svg = create_distance_histogram(
    list(map(lambda run: run.distance, longest_distance_runs))
)

now = datetime.date.today()
html = (
    "<!DOCTYPE html>"
    + "<html>"
    + '<head><meta charset="utf-8" />'
    + "<title>Distance histogram</title>"
    + "</head><body>"
    + distance_svg
    + "<p>Longest distance: {}.<br />Longest time: {}.</p>".format(
        longest_distance_runs[0], longest_time_runs[0]
    )
    + "<footer><p>Generated on {}.</p></footer>".format(now)
    + "</body></html>"
)

try:
    os.mkdir("./output")
except FileExistsError:
    pass

NAME = "./output/distance-histogram.html"
with open(NAME, "w") as f:
    f.write(html)
