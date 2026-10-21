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


def create_distance_histogram(distances):
    fig, axs = plt.subplots()
    # +1 for rounding down, +1 for range
    bins = list(range(int(max(distances)) + 2))
    # Bin is [low, high[
    values, _bin_edges, _patches = axs.hist(distances, bins=bins, log=True)
    axs.set_xlabel("Length of run (km)")
    axs.set_ylabel("Number of runs")
    # None makes matplotlib take its own default
    axs.set_ylim([0.5, None])
    axs.minorticks_on()

    # Adding labels
    for i in range(len(values)):
        if values[i] > 0:
            axs.text(
                i + 0.5, values[i], str(int(values[i])), ha="center", fontsize="x-small"
            )
            axs.text(
                i + 0.5,
                0.5,
                str(i),
                ha="center",
                va="bottom",
                fontsize="x-small",
            )

    fig.tight_layout()
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
plt.rcParams["figure.figsize"] = [12, 5]


distance_svg = create_distance_histogram(
    list(map(lambda run: run.distance, longest_distance_runs))
)


def make_table(runs):
    def run_to_row(run):
        hours, minutes = goldencheetah.seconds_to_hours_minutes(run.time_moving)
        return """
            <tr>
                <td>{}</td>
                <td style="text-align:right;">{:.3f}</td>
                <td style="text-align:right;">{}:{:02d}</td>
            </tr>
        """.format(run.date, run.distance, hours, minutes)

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


def number_to_subindex_str(n: int) -> str:
    if n < 0:
        raise RuntimeError

    if n == 0:
        return "₀"

    subindices = {
        0: "₀",
        1: "₁",
        2: "₂",
        3: "₃",
        4: "₄",
        5: "₅",
        6: "₆",
        7: "₇",
        8: "₈",
        9: "₉",
    }
    res = ""
    while n > 0:
        last_digit = n % 10
        res = subindices[last_digit] + res
        n = n // 10
    return res


def h_index(sorted_runs: list[goldencheetah.Activity], multiplier=1):
    """
    Sort of h-index idea from academia. Basically, find the distance n such
    that you have at least n runs that are that distance or longer.

    Expects given runs to be sorted from longest to shortest distance.

    Returns:
        distance that has at least multiplier * distance of activities
        number of activities at the next distance up
    """
    total = 0
    count_at_current_distance = 0
    curr_distance = -1
    for run in sorted_runs:
        d = int(run.distance)
        total += 1
        if curr_distance == d:
            count_at_current_distance += 1
        else:
            count_at_current_distance = 1
            curr_distance = d
        if total >= d * multiplier:
            return d, total - count_at_current_distance
    return 0, total - count_at_current_distance


def h_index_msg(sorted_runs: list[goldencheetah.Activity], multiplier=1):
    """
    Runs sorted from longest to shortest.
    """
    h_idx_dist, total_at_h_idx_up = h_index(sorted_runs, multiplier)
    return "<p>Running distance h{}-index: {} km ({} over {} km for next level).</p>".format(
        number_to_subindex_str(multiplier),
        h_idx_dist,
        ((h_idx_dist + 1) * multiplier - total_at_h_idx_up),
        h_idx_dist + 1,
    )


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
    + h_index_msg(longest_distance_runs, 1)
    + h_index_msg(longest_distance_runs, 2)
    + h_index_msg(longest_distance_runs, 3)
    + h_index_msg(longest_distance_runs, 5)
    + h_index_msg(longest_distance_runs, 10)
    + h_index_msg(longest_distance_runs, 20)
    + h_index_msg(longest_distance_runs, 30)
    + h_index_msg(longest_distance_runs, 50)
    + h_index_msg(longest_distance_runs, 100)
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
