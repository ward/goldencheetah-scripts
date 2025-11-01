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

# Configure matplotlib
plt.rcParams["figure.figsize"] = [12, 8]


class GoalProgress:
    actual: bool

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

    _avg_so_far_per_day: float

    def __init__(self, actual: bool = False):
        self.actual = actual

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
        self._avg_so_far_per_day = self.ran_so_far / days_passed
        self.current_extrapolated = self._avg_so_far_per_day * total_days

    def to_html_row(self, goal_reached: bool = False) -> str:
        if self.actual:
            return (
                '<tr class="actual" title="This row is current progress extrapolated">'
                "<td>{:,.1f}</td>"
                "<td>{:,.1f}</td>"
                "<td>{:,.1f}</td>"
                "<td>{:,.1f}</td>"
                "<td></td>"
                "<td></td>"
                "<td></td>"
                "<td></td>"
                "</tr>"
            ).format(
                self.current_extrapolated,
                self._avg_so_far_per_day,
                7 * self._avg_so_far_per_day,
                self.ran_so_far,
            )

        row = (
            "<tr>"
            "<td>{:,.1f}</td>"
            "<td>{:,.1f}</td>"
            "<td>{:,.1f}</td>"
            "<td>{:,.1f}</td>"
            "<td>{:,.1f}</td>"
        )
        row = row.format(
            self.goal,
            self.per_day,
            7 * self.per_day,
            self.should_have_ran,
            self.ran_so_far - self.should_have_ran,
        )

        if goal_reached:
            row += "<td>✓</td>" "<td>✓</td>" "<td>✓</td>"
        else:
            row += "<td>{:,.1f}</td>" "<td>{:,.1f}</td>" "<td>{:,.1f}</td>"
            row = row.format(
                self.goal - self.ran_so_far,
                self.per_day_from_now_on,
                7 * self.per_day_from_now_on,
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


def create_goals_table(cumul_per_day, goals: list[int], days):
    """Return a string that gets rendered as a table in HTML"""
    result = "<table>"

    # Header
    result += (
        "<tr>"
        '<th style="text-align: center" colspan="3">Goal</th>'
        '<th style="text-align: center" colspan="2">So Far</th>'
        '<th style="text-align: center" colspan="3">To Go</th>'
        "</tr>"
    )
    result += (
        "<tr>"
        "<th>total</th>"
        "<th>/d</th>"
        "<th>/w</th>"
        "<th>goal</th>"
        "<th>diff</th>"
        "<th>total</th>"
        "<th>/d</th>"
        "<th>/w</th>"
        "</tr>"
    )

    # Individual rows per goal
    already_added_goal = False
    for goal in goals:
        goal_progress = GoalProgress()
        goal_progress.calculate_goal_stats(cumul_per_day, goal, days)
        goal_reached = goal_progress.ran_so_far >= goal

        if goal_progress.current_extrapolated >= goal and not already_added_goal:
            already_added_goal = True
            actual = GoalProgress(actual=True)
            # The goal distance we add here does not matter, we only care to
            # have progress and such in it.
            actual.calculate_goal_stats(cumul_per_day, 1, days)
            row = actual.to_html_row()
            result += row

        row = goal_progress.to_html_row(goal_reached)

        result += row

    if not already_added_goal:
        actual = GoalProgress(actual=True)
        # The goal distance we add here does not matter, we only care to
        # have progress and such in it.
        actual.calculate_goal_stats(cumul_per_day, 1, days)
        row = actual.to_html_row()
        result += row

    result += "</table>"
    return result


def create_svg(cumul_per_day, days):
    fig, ax = plt.subplots()

    # Straight lines towards goal distance
    for goal_distance in GOAL_DISTANCES:
        ax.plot(
            days,
            create_goal_values(goal_distance, days),
            "--",
            color="lightgrey",
            label=goal_distance,
        )

    # Previous years
    # TODO: Derive range from oldest run
    current_year = datetime.datetime.now().year
    previous_years = list(range(2014, current_year))
    # Make previous two years fatter
    widths = {y: 1 for y in previous_years}
    widths[current_year - 1] = 3
    widths[current_year - 2] = 2
    for year in previous_years:
        # Beware, runs is global
        cumul_for_2024 = count_year_progress(year, runs)
        ax.plot(
            days,
            [cumul_for_2024[day.replace(year=year)] for day in days],
            label=year,
            linewidth=widths[year],
        )

    # Current year
    ax.plot(
        days,
        [cumul_per_day[day] for day in days],
        linewidth=5,
        label="Distance run",
    )

    ax.grid(axis="y")
    ax.legend()
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


def build_html_document(cumul_per_day, years_days):
    """Build the complete HTML document with chart and table."""
    now = datetime.date.today()
    html = (
        "<!DOCTYPE html>"
        + "<html>"
        + '<head><meta charset="utf-8" />'
        + html_css()
        + "<title>5 MEGA METER</title>"
        + "</head><body>"
        + create_svg(cumul_per_day, years_days)
        + create_goals_table(cumul_per_day, GOAL_DISTANCES, years_days)
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

    # Generate HTML
    html = build_html_document(cumul_per_day, years_days)

    # Write output file
    try:
        os.mkdir(OUTPUT_DIR)
    except FileExistsError:
        pass

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
