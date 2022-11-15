import matplotlib.pyplot as plt
import datetime
import os
from io import BytesIO

import goldencheetah

# Format to aim for to hand to several plt.bar calls
# [
#   RunSummaryPer
# ]


class RunSummaryPer:
    def __init__(self):
        self.label = "NO LABEL"
        # Distance in km
        self.values = []
        # E.g. the days or the months
        self.keys = []
        # Default colours for certain workout codes
        self.colourmap = {}
        self.colourmap["Recovery"] = "#00a1f7"
        self.colourmap["Warmup"] = "#00a1f7"
        self.colourmap["Cooldown"] = "#00a1f7"
        self.colourmap["GA"] = "#0094e4"
        self.colourmap["Endurance"] = "#0072b2"
        self.colourmap["Threshold"] = "#009e73"
        self.colourmap["Race"] = "#d55e00"

    def colour(self):
        try:
            return self.colourmap[self.label]
        except:
            return "#000000"


def create_daily_run_summaries(list_of_runs):
    activity_types = {}
    all_days = goldencheetah.days_range(
        list_of_runs[0].date.date(), datetime.date.today()
    )
    original_all_days = [d for d in all_days]
    ctr = 0
    # To avoid removing from the front the entire time
    all_days.reverse()
    list_of_runs.reverse()

    while len(all_days) > 0 and len(list_of_runs) > 0:
        act = list_of_runs[-1]
        day = all_days[-1]

        next_run_date = act.date.date()
        if next_run_date < day:
            raise Exception("Should not happen")
        elif next_run_date > day:
            all_days.pop()
            ctr += 1
            continue

        # Today is the day
        print(act)
        if act.workout_code not in activity_types:
            new_summ = RunSummaryPer()
            new_summ.label = act.workout_code
            new_summ.keys = [d for d in original_all_days]
            new_summ.values = [0 for _ in original_all_days]
            activity_types[act.workout_code] = new_summ

        activity_types[act.workout_code].values[ctr] += act.distance

        # Remove last since we reversed it
        list_of_runs.pop()
        # Don't remove from all_days, there may be more activities to come
        # Don't inc ctr, same reason

    return list(activity_types.values())


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
summaries = create_daily_run_summaries(runs)
print(summaries[0].values)
print(len(summaries[0].values))
# per_month = sum_per_month(runs)
# per_year = sum_per_year(runs)
# runs = goldencheetah.group_by_week(runs)

# for week in runs.keys():
#    runs[week] = sum_week(runs[week])

# Now we have a dict with
# Keys: "2022-22" as week names
# Values: Distance summed up


def create_svg(summaries):
    fig, ax = plt.subplots()
    # time_units = list(distance_per_time.keys())[-20:]
    # distances = [distance_per_time[time_unit] for time_unit in time_units]
    # ax.bar(time_units, distances)
    bottoms = [0 for _ in summaries[0].keys]
    for summary in summaries:
        ax.bar(
            summary.keys[-30:],
            summary.values[-30:],
            label=summary.label,
            color=summary.colour(),
            bottom=bottoms[-30:],
        )
        print(len(bottoms), len(summary.values))
        bottoms = [x + y for (x, y) in zip(bottoms, summary.values)]

    # Put values on the bars
    # for i in range(len(time_units)):
    #    ax.text(
    #        i,
    #        distances[i],
    #        int(distances[i]),
    #        horizontalalignment="center",
    #        fontsize="small",
    #    )

    # ax.legend()
    ax.grid(axis="y")
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    ax.set_title("Distance per {}".format("days"))
    ax.secondary_yaxis("right")
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
    + "<title>Workouts and shit</title>"
    + "</head><body>"
    + create_svg(summaries)
    + "<footer><p>Generated on {}.</p></footer>".format(now)
    + "</body></html>"
)

try:
    os.mkdir("./output")
except FileExistsError:
    pass

NAME = "./output/distanceandtypepertime.html"
with open(NAME, "w") as f:
    f.write(html)
