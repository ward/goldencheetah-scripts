import datetime
import os
from io import BytesIO
import matplotlib.pyplot as plt
import goldencheetah

# Constants
GOAL_DISTANCES = [5000, 4000, 3000, 2500, 2000, 1000]
OUTPUT_DIR = "./output"
OUTPUT_FILE = "./output/5mm.html"
CSS_FILE = "5mm.css"
JS_FILE = "5mm.js"

# Configure matplotlib
# Default is [6.4, 4.8] (width, height)
plt.rcParams["figure.figsize"] = [12, 8]


class GoalProgress:
    actual: bool
    """Indicates the GoalProgress object is this year's or a previous year's
    actual running. As opposed to an artificial goal"""

    year: int | None
    """The year, e.g. 2026, this row represents, or None for goal rows"""

    goal: float
    """Distance to run in the current year"""

    per_day: float
    """Units of distance to run per day to reach the given goal"""

    ran_so_far: float
    """Distance run so far in the current year"""

    should_have_ran: float

    per_day_from_now_on: float

    per_day_from_now_on_with_today: float

    current_extrapolated: float
    """Takes distance run this year to date and extrapolates to the entire year"""

    avg_per_day: float
    """Distance per day across the entire year. For goals this is the same as
    avg_so_far_per_day, as we assume entirely steady year round. For current
    year extrapolated, this is also the same as avg_so_far_per_day, as we
    assume steady continuation of what happened so far."""

    avg_so_far_per_day: float

    current_year_ran_so_far: float | None
    """For previous year rows: the current year's ran_so_far, for computing
    diff. I believe that the artificial goal rows use the ran_so_far property
    instead."""

    def __init__(self, actual: bool = False):
        self.actual = actual
        self.year = None
        self.current_year_ran_so_far = None

    def calculate_goal_stats(
        self,
        cumul_per_day: dict[datetime.date, float | None],
        goal: float,
        days: list[datetime.date],
    ):
        self.goal = goal
        today = datetime.date.today()
        current_distance_ran = cumul_per_day[today]
        assert current_distance_ran is not None
        self.ran_so_far = current_distance_ran

        self.per_day = self.goal / len(days)
        # tm_yday starts at 1, so we do not need to do + per_day
        self.should_have_ran = self.per_day * today.timetuple().tm_yday

        days_left = (days[-1] - today).days
        self.per_day_from_now_on = (self.goal - self.ran_so_far) / days_left
        self.per_day_from_now_on_with_today = (self.goal - self.ran_so_far) / (
            days_left + 1
        )

        days_passed = (today - days[0]).days + 1
        total_days = (days[-1] - days[0]).days + 1
        self.avg_so_far_per_day = self.ran_so_far / days_passed
        # This function only gets called for goals (steady throughout the year)
        # and extrapolated current year (where we expect the rest of the year
        # to be steady from today based on what we did so far)
        self.avg_per_day = self.avg_so_far_per_day
        self.current_extrapolated = self.avg_so_far_per_day * total_days


def render_goal_row(gp: GoalProgress, goal_reached: bool = False) -> str:
    if gp.actual:
        current_year = datetime.date.today().year
        if gp.year == current_year:
            tr = f'<tr class="actual" data-series="year-{gp.year}" title="This row is current progress extrapolated">'
        else:
            tr = f'<tr class="year" data-series="year-{gp.year}">'
        diff_cell = "<td></td>"
        if gp.current_year_ran_so_far is not None:
            diff = gp.current_year_ran_so_far - gp.ran_so_far
            diff_cell = f"<td>{diff:,.1f}</td>"
        row = (
            tr + "<td>{}</td>"
            "<td>{:,.1f}</td>"
            "<td>{:,.1f}</td>"
            "<td>{:,.1f}</td>"
            "<td>{:,.1f}</td>"
        ).format(
            gp.year,
            gp.current_extrapolated,
            gp.avg_per_day,
            7 * gp.avg_per_day,
            gp.ran_so_far,
        )
        row += diff_cell
        if goal_reached:
            row += "<td>✓</td><td>✓</td><td>✓</td>"
        elif gp.current_year_ran_so_far is not None:
            to_go = gp.current_extrapolated - gp.current_year_ran_so_far
            days_left = (datetime.date(current_year, 12, 31) - datetime.date.today()).days
            per_day = to_go / days_left if days_left > 0 else 0
            row += f"<td>{to_go:,.1f}</td><td>{per_day:,.1f}</td><td>{7 * per_day:,.1f}</td>"
        else:
            row += "<td></td><td></td><td></td>"
        row += "</tr>"
        return row

    row = (
        "<tr>"
        "<td></td>"
        "<td>{:,.1f}</td>"
        "<td>{:,.1f}</td>"
        "<td>{:,.1f}</td>"
        "<td>{:,.1f}</td>"
        "<td>{:,.1f}</td>"
    )
    row = row.format(
        gp.goal,
        gp.per_day,
        7 * gp.per_day,
        gp.should_have_ran,
        gp.ran_so_far - gp.should_have_ran,
    )

    if goal_reached:
        row += "<td>✓</td><td>✓</td><td>✓</td>"
    else:
        row += "<td>{:,.1f}</td><td>{:,.1f}</td><td>{:,.1f}</td>"
        row = row.format(
            gp.goal - gp.ran_so_far,
            gp.per_day_from_now_on,
            7 * gp.per_day_from_now_on,
        )
    row += "</tr>"

    return row


def count_year_progress(year: int, runs: list):
    start_year = datetime.date(year=year, month=1, day=1)
    end_year = datetime.date(year=year, month=12, day=31)
    years_days = goldencheetah.days_range(start_year, end_year)

    # Set 0 distance on every day, creates the keys in dict
    distance_per_day: dict[datetime.date, float] = {}
    for day in years_days:
        distance_per_day[day] = 0

    # Sum all relevant distances
    for run in runs:
        day = run.date.date()
        if day in distance_per_day:
            distance_per_day[day] += run.distance

    # Count the cumul. Set None once past today (so it won't get plotted).
    cumul_per_day: dict[datetime.date, float | None] = {}
    current_sum = 0
    today = datetime.date.today()
    for day in years_days:
        if day > today:
            cumul_per_day[day] = None
            continue
        current_sum += distance_per_day[day]
        cumul_per_day[day] = current_sum

    return cumul_per_day


def create_goal_values(goal, days):
    """For a given goal to hit at the end of the days range, return a list of
    what to hit on each day in the range. For example to hit 14 in a week, you
    will get [2,4,6,8,10,12,14]."""
    per_day = goal / len(days)
    return [per_day + per_day * i for i in range(len(days))]


def compute_goal_stats(
    cumul_per_day: dict[datetime.date, float | None],
    goals: list[int],
    days: list[datetime.date],
    cumul_previous: dict[int, dict[datetime.date, float | None]],
) -> list[tuple[GoalProgress, bool]]:
    """Compute goal stats for each goal distance and year, sorted descending
    by total (goal distance, year-end total, or current extrapolated).

    Year/actual rows are placed before goal rows with the same total."""
    today = datetime.date.today()
    current_year = today.year

    # (GoalProgress, goal_reached, sort_key)
    # Sort key: (total, priority) where priority 1 = year rows (sort first),
    # 0 = goal rows, when totals are equal.
    rows: list[tuple[GoalProgress, bool, tuple[float, int]]] = []

    # Goal rows
    for goal in goals:
        goal_progress = GoalProgress()
        goal_progress.calculate_goal_stats(cumul_per_day, goal, days)
        goal_reached = goal_progress.ran_so_far >= goal
        rows.append((goal_progress, goal_reached, (goal_progress.goal, 0)))

    # Actual row (current year extrapolated)
    actual = GoalProgress(actual=True)
    # The goal distance we add here does not matter, we only care to
    # have progress and such in it.
    actual.calculate_goal_stats(cumul_per_day, 1, days)
    actual.year = current_year
    current_ran_so_far = actual.ran_so_far
    rows.append((actual, False, (actual.current_extrapolated, 1)))

    # Previous year rows
    days_passed = today.timetuple().tm_yday
    for year, cumul in cumul_previous.items():
        year_end_total = cumul[datetime.date(year=year, month=12, day=31)]
        assert year_end_total is not None
        try:
            lookup_date = today.replace(year=year)
        except ValueError:
            # Feb 29 in a non-leap year: fall back to Feb 28
            lookup_date = today.replace(year=year, day=28)
        ran_on_this_date = cumul[lookup_date]
        assert ran_on_this_date is not None

        prev = GoalProgress(actual=True)
        prev.year = year
        prev.ran_so_far = ran_on_this_date
        prev.avg_so_far_per_day = ran_on_this_date / days_passed
        total_days = (days[-1] - days[0]).days + 1
        prev.avg_per_day = year_end_total / total_days
        prev.current_extrapolated = year_end_total
        prev.current_year_ran_so_far = current_ran_so_far
        year_surpassed = current_ran_so_far >= year_end_total
        rows.append((prev, year_surpassed, (year_end_total, 1)))

    rows.sort(key=lambda r: r[2], reverse=True)
    return [(gp, reached) for gp, reached, _ in rows]


def create_goals_table(goal_stats: list[tuple[GoalProgress, bool]]):
    """Return a string that gets rendered as a table in HTML"""
    result = "<table>"

    # Header
    result += (
        "<tr>"
        '<th rowspan="2"></th>'
        '<th style="text-align: center" colspan="3">Goal</th>'
        '<th style="text-align: center" colspan="2">So Far</th>'
        '<th style="text-align: center" colspan="3">To Go</th>'
        "</tr>"
    )
    result += (
        "<tr>"
        '<th class="sortable" data-col="1">total</th>'
        "<th>/d</th>"
        "<th>/w</th>"
        '<th class="sortable" data-col="4"></th>'
        "<th>diff</th>"
        "<th>total</th>"
        "<th>/d</th>"
        "<th>/w</th>"
        "</tr>"
    )

    for gp, goal_reached in goal_stats:
        result += render_goal_row(gp, goal_reached)

    result += "</table>"
    return result


def create_svg(cumul_per_day, cumul_previous, days):
    """Create an SVG chart showing yearly running progress."""
    fig, ax = plt.subplots()

    series_keys = []

    # Straight lines towards goal distance
    for goal_distance in GOAL_DISTANCES:
        (line,) = ax.plot(
            days,
            create_goal_values(goal_distance, days),
            "--",
            color="lightgrey",
            label=goal_distance,
        )
        key = f"goal-{goal_distance}"
        line.set_gid(key)
        series_keys.append(key)

    # Previous years
    current_year = datetime.datetime.now().year
    for year, cumul_for_year in cumul_previous.items():
        # Make the two most recent years fatter
        width = {1: 3, 2: 2}.get(current_year - year, 1)
        (line,) = ax.plot(
            days,
            [cumul_for_year[day.replace(year=year)] for day in days],
            label=year,
            linewidth=width,
        )
        key = f"year-{year}"
        line.set_gid(key)
        series_keys.append(key)

    # Current year
    (line,) = ax.plot(
        days,
        [cumul_per_day[day] for day in days],
        linewidth=5,
        label="Distance run",
    )
    key = f"year-{current_year}"
    line.set_gid(key)
    series_keys.append(key)

    ax.grid(axis="y")
    legend = ax.legend()
    # This assumes legend order is the same as plotting order, which I think
    # holds by default
    for key, leg_line, leg_text in zip(
        series_keys, legend.get_lines(), legend.get_texts()
    ):
        leg_line.set_gid(f"legend-line-{key}")
        leg_text.set_gid(f"legend-text-{key}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    ax.set_title("5 MEGA METER")
    ax.set_xlim(days[0], days[-1])
    # plt.xticks(rotation=45)
    # ax.minorticks_on()

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


def html_css():
    """Read CSS file and return it wrapped in a style tag."""
    with open(CSS_FILE, "r") as css:
        contents = css.read()
        return '<style type="text/css">' + contents + "</style>"


def html_js():
    """Read JS file and return it wrapped in a script tag."""
    with open(JS_FILE, "r") as js:
        contents = js.read()
        return "<script>" + contents + "</script>"


def build_html_document(cumul_per_day, cumul_previous, goal_stats, years_days):
    """Build the complete HTML document with chart and table."""
    now = datetime.date.today()
    html = (
        "<!DOCTYPE html>"
        + "<html>"
        + '<head><meta charset="utf-8" />'
        + html_css()
        + html_js()
        + "<title>5 MEGA METER</title>"
        + "</head><body>"
        + create_svg(cumul_per_day, cumul_previous, years_days)
        + create_goals_table(goal_stats)
        + "<footer><p>Generated on {}.</p></footer>".format(now)
        + "</body></html>"
    )
    return html


def main():
    # Get all running activities
    runs = goldencheetah.get_all_activities(sport="Run")

    # Generate days for current year
    current_year = datetime.datetime.now().year
    start_year = datetime.date(year=current_year, month=1, day=1)
    end_year = datetime.date(year=current_year, month=12, day=31)
    years_days = goldencheetah.days_range(start_year, end_year)

    # Calculate cumulative progress
    cumul_per_day = count_year_progress(current_year, runs)

    # Calculate previous years' cumulative progress
    first_year = min(r.date.year for r in runs)
    cumul_previous = {
        year: count_year_progress(year, runs)
        for year in range(first_year, current_year)
    }

    # Compute goal stats
    goal_stats = compute_goal_stats(
        cumul_per_day, GOAL_DISTANCES, years_days, cumul_previous
    )

    # Generate HTML
    html = build_html_document(cumul_per_day, cumul_previous, goal_stats, years_days)

    # Write output file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
