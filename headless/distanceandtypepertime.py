import matplotlib.pyplot as plt
import datetime
import os
from io import BytesIO

import goldencheetah


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
        self.colourmap["GA"] = "#0094e4"
        self.colourmap["Endurance"] = "#0072b2"
        self.colourmap["Threshold"] = "#009e73"
        self.colourmap["Race"] = "#d55e00"
        self.colourmap["Repetition"] = "#f0e442"
        self.colourmap["CV"] = "#5afff2"
        self.colourmap["VO2max"] = "#e69f00"
        self.colourmap["Race pace"] = "#e69f00"

    def colour(self):
        try:
            return self.colourmap[self.label]
        except:
            return "#000000"

    def normalise_name(name):
        if name == "Warmup" or name == "Cooldown":
            return "Recovery"
        elif name == "LT" or name == "Tempo":
            return "Threshold"
        # TODO Fix in GC
        elif name == "VO2Max":
            return "VO2max"
        else:
            return name


def days_to_weeks(list_of_days):
    """Specifically, weeks represented as a "YYYY-MM" string."""
    all_weeks = []
    for day in list_of_days:
        that_week = day.isocalendar()
        if (
            len(all_weeks) == 0
            or all_weeks[-1].year != that_week.year
            or all_weeks[-1].week != that_week.week
        ):
            all_weeks.append(that_week)
    return list(map(lambda iso: "{}-{}".format(iso.year, iso.week), all_weeks))


class Summary:
    def __init__(self, datekeys=[]):
        self.types = {}
        self.datekeys = [k for k in datekeys]

    def set_default_datekeys(self, datekeys):
        self.datekeys = datekeys

    def add_value(self, typee, datekey, value):
        if typee not in self.types:
            self.types[typee] = {}
            for dk in self.datekeys:
                self.types[typee][dk] = 0
        self.types[typee][datekey] += value

    def to_plottable(self):
        summaries = []
        for typee in self.types:
            rsp = RunSummaryPer()
            rsp.label = typee
            rsp.keys = list(self.types[typee].keys())
            rsp.values = list(self.types[typee].values())
            summaries.append(rsp)
        return summaries


def create_run_summaries(list_of_runs):
    all_days = goldencheetah.days_range(
        list_of_runs[0].date.date(), datetime.date.today()
    )
    all_weeks = days_to_weeks(all_days)
    # The list(dict.fromkeys( is a hacky way to get rid of duplicates
    all_years = list(dict.fromkeys(map(lambda d: d.year, all_days)))

    day_summary = Summary(all_days)
    week_summary = Summary(all_weeks)
    year_summary = Summary(all_years)

    for run in list_of_runs:
        workout_code = RunSummaryPer.normalise_name(run.workout_code)
        dist = run.distance
        day = run.date.date()
        week = "{}-{}".format(run.date.isocalendar().year, run.date.isocalendar().week)
        year = run.date.year
        day_summary.add_value(workout_code, day, dist)
        week_summary.add_value(workout_code, week, dist)
        year_summary.add_value(workout_code, year, dist)

    return (day_summary, week_summary, year_summary)


runs = goldencheetah.get_all_activities(sport="Run")
(day_summary, week_summary, year_summary) = create_run_summaries(runs)


def create_svg(summaries, time_name):
    BAR_COUNT = 30
    summaries = summaries.to_plottable()
    fig, ax = plt.subplots()

    # Can be too big on first iteration, doesnt matter since all 0s
    # The zip in the for loop cuts it to the right size
    bottoms = [0 for _ in summaries[0].keys]
    for summary in summaries:
        # Filter to not fill up the legend with stuff not in the bar chart
        if any(map(lambda x: x != 0, summary.values[-BAR_COUNT:])):
            ax.bar(
                summary.keys[-BAR_COUNT:],
                summary.values[-BAR_COUNT:],
                label=summary.label,
                color=summary.colour(),
                bottom=bottoms[-BAR_COUNT:],
            )
            bottoms = [x + y for (x, y) in zip(bottoms, summary.values)]

    ax.legend()
    ax.grid(axis="y")
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    ax.set_title("Distance and workouts per {}".format(time_name))
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
    + create_svg(day_summary, "day")
    + create_svg(week_summary, "week")
    + create_svg(year_summary, "year")
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
