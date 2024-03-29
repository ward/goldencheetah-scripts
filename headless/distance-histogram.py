import datetime
from io import BytesIO
import os

import matplotlib.pyplot as plt

import goldencheetah


runs = goldencheetah.get_all_activities(sport="Run")

# Lazier than looping ourselves, probably a bit slower though.
longest_distance_runs = sorted(runs, key=lambda a: a.distance, reverse=True)
longest_time_runs = sorted(runs, key=lambda a: a.time_moving, reverse=True)

one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
recent_longest_distance_runs = list(
    filter(lambda r: r.date > one_year_ago, longest_distance_runs)
)
recent_longest_time_runs = list(
    filter(lambda r: r.date > one_year_ago, longest_time_runs)
)

# for run in longest_distance_runs[:10]:
#     print(run.distance, run.date)

# for run in longest_time_runs[:10]:
#     print(goldencheetah.seconds_to_hours_minutes(run.time_moving), run.date)


# Some copy pasting of rolling-total.py
def create_distance_histogram(distances):
    fig, axs = plt.subplots()
    # +1 for rounding down, +1 for range
    bins = list(range(int(max(distances)) + 2))
    # Bin is [low, high[
    values, _bin_edges, _patches = axs.hist(distances, bins=bins, log=True)
    axs.set_xlabel("Length of run (km)")
    axs.set_ylabel("Number of runs")
    # None makes matplotlib take its own default
    axs.set_ylim([0.1, None])
    axs.minorticks_on()

    # Adding labels
    for i in range(len(values)):
        axs.text(i, values[i], int(values[i]), fontsize="x-small")

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format="svg")
    svg = tmpfile.getvalue().decode("utf-8")
    # Release memory
    plt.close(fig)

    # Remove the <?xml ...><!DOCTYPE svg ... > stuff at the start
    index_of_greater_than = svg.find(">") + 1
    index_of_greater_than = svg.find(">", index_of_greater_than) + 1
    return svg[index_of_greater_than:]


# Default is [6.4, 4.8] (width, height)
plt.rcParams["figure.figsize"] = [10, 5]


distance_svg = create_distance_histogram(
    list(map(lambda run: run.distance, longest_distance_runs))
)


def make_table(runs):
    def run_to_row(run):
        hours, minutes = goldencheetah.seconds_to_hours_minutes(run.time_moving)
        return "<tr><td>{}</td><td>{:.3f}</td><td>{}:{:02d}</td></tr>".format(
            run.date, run.distance, hours, minutes
        )

    table = (
        "<table>"
        + "<thead><tr><th>Date</th><th>Distance</th><th>Time</th></tr></thead>"
        + "<tbody>"
        + "".join(
            map(
                run_to_row,
                runs[0:10],
            )
        )
        + "</tbody>"
        + "</table>"
    )
    return table


now = datetime.date.today()
html = (
    "<!DOCTYPE html>"
    + "<html>"
    + '<head><meta charset="utf-8" />'
    + "<title>Distance histogram</title>"
    + "</head><body>"
    + distance_svg
    + "<p>Recent longest distance</p>"
    + make_table(recent_longest_distance_runs[0:10])
    + "<p>Recent longest time</p>"
    + make_table(recent_longest_time_runs[0:10])
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
