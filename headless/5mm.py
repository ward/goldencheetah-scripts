import math
import datetime
import os
from io import BytesIO
import matplotlib.pyplot as plt
import goldencheetah

# How much we are hoping to hit in a year
GOAL_DISTANCES = [5000, 4000, 3000]

# Get runs
runs = goldencheetah.get_all_activities(sport="Run")

# Generate days for current year
current_year = datetime.datetime.now().year
start_year = datetime.date(year=current_year, month=1, day=1)
end_year = datetime.date(year=current_year, month=12, day=31)
years_days = goldencheetah.days_range(start_year, end_year)

# Set 0 distance on every day, creates the keys in dict
distance_per_day = {}
for day in years_days:
    distance_per_day[day] = 0

# Sum all relevant distances
for run in runs:
    day = run.date.date()
    if day in distance_per_day:
        distance_per_day[day] += run.distance

# Count the cumul. Set None once past today (so it won't get plotted).
cumul_per_day = {}
current_sum = 0
today = datetime.date.today()
for day in years_days:
    if day > today:
        cumul_per_day[day] = None
        continue
    current_sum += distance_per_day[day]
    cumul_per_day[day] = current_sum


def create_goal_values(goal, days):
    """For a given goal to hit at the end of the days range, return a list of
    what to hit on each day in the range. For example to hit 14 in a week, you
    will get [2,4,6,8,10,12,14]."""
    per_day = goal / len(days)
    return [per_day + per_day * i for i in range(len(days))]


def calculate_goal_stats(cumul_per_day, goal, days):
    today = datetime.date.today()
    current_distance_ran = cumul_per_day[today]

    per_day = goal / len(days)
    # tm_yday starts at 1, so we do not need to do + per_day
    goal_distance_ran = per_day * today.timetuple().tm_yday

    days_left = (days[-1] - today).days
    per_day_from_now_on = (goal - current_distance_ran) / days_left
    per_day_from_now_on_with_today = (goal - current_distance_ran) / (days_left + 1)
    return {
        "per_day": per_day,
        "ran_so_far": current_distance_ran,
        "should_have_ran": goal_distance_ran,
        "per_day_from_now_on": per_day_from_now_on,
        "per_day_from_now_on_with_today": per_day_from_now_on_with_today,
    }


def create_textual_overview(cumul_per_day, goal, days):
    stats = calculate_goal_stats(cumul_per_day, goal, days)
    result = "<p>You have run {:,.1f} km so far. "
    if stats["ran_so_far"] > stats["should_have_ran"]:
        result += "You are {:,.1f} km ahead of where you should be today ({:,.1f}). "
    else:
        result += "You are {:,.1f} km behind where you should be today ({:,.1f}). "
    result += "To reach your goal, you need {:,.1f} per day ({:,.1f} per week) from here on out. "
    result += "If you still have to run today, that is {:,.1f} per day and {:,.1f} per week.</p>"
    result = result.format(
        stats["ran_so_far"],
        abs(stats["ran_so_far"] - stats["should_have_ran"]),
        stats["should_have_ran"],
        stats["per_day_from_now_on"],
        7 * stats["per_day_from_now_on"],
        stats["per_day_from_now_on_with_today"],
        7 * stats["per_day_from_now_on_with_today"],
    )
    return result


def create_svg(cumul_per_day, days):
    fig, ax = plt.subplots()
    ax.plot(days, [cumul_per_day[day] for day in days], label="Distance run")
    for goal_distance in GOAL_DISTANCES:
        ax.plot(
            days,
            create_goal_values(goal_distance, days),
            "--",
            color="grey",
            label=goal_distance,
        )
    ax.grid(axis="y")
    ax.legend()
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    ax.set_title("5 MEGA METER")
    ax.set_xlim(days[0], days[-1])
    # plt.xticks(rotation=45)
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
plt.rcParams["figure.figsize"] = [10, 5]

now = datetime.date.today()
html = (
    "<!DOCTYPE html>"
    + "<html>"
    + '<head><meta charset="utf-8" />'
    + "<title>5 MEGA METER</title>"
    + "</head><body>"
    + create_svg(cumul_per_day, years_days)
    + create_textual_overview(cumul_per_day, GOAL_DISTANCES[0], years_days)
    + "<footer><p>Generated on {}.</p></footer>".format(now)
    + "</body></html>"
)

try:
    os.mkdir("./output")
except FileExistsError:
    pass

NAME = "./output/5mm.html"
with open(NAME, "w") as f:
    f.write(html)
