import datetime
import os
from io import BytesIO

import matplotlib.pyplot as plt

import goldencheetah

DAYS = [7, 28, 84, 365]
OUTPUT_FILE = "./output/rolling-total.html"

# Matplotlib settings
plt.rcParams["figure.figsize"] = [10, 5]


def days_range(start_day: datetime.date, end_day: datetime.date) -> list[datetime.date]:
    """
    Returns a list of dates from the `start_day` till the `end_day`
    (inclusive).
    """
    return [
        start_day + datetime.timedelta(days=days)
        for days in range((end_day - start_day).days + 1)
    ]


def calculate_rolling_total(
    window_size: int,
    dist_per_day: dict[datetime.date, float],
) -> dict[datetime.date, float]:
    """
    Calculates rolling total combining a certain number of days. Rolling total
    is calculated for every day in dist_per_day

    Params:
        window_size: number of days to use for rolling total
        dist_per_day: number of km ran for every given day
    """
    rolling_per_day: dict[datetime.date, float] = {}
    # TODO: I should be using sliding window here instead of loop in loop
    for d in dist_per_day.keys():
        old_day = d - datetime.timedelta(days=window_size - 1)
        range_of_interest = days_range(old_day, d)
        total = 0
        for interesting_day in range_of_interest:
            total += dist_per_day.get(interesting_day, 0)
        rolling_per_day[d] = total
    return rolling_per_day


def get_rolling_svg(
    rolling: dict[datetime.date, float],
    days_for_analysis: list[datetime.date],
    window_size: int,
) -> str:
    """
    Creates SVG showing the given rolling total
    """
    fig, ax = plt.subplots()
    ax.plot(days_for_analysis, [rolling[d] for d in days_for_analysis])
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    ax.set_title("Rolling {} Day Total".format(window_size))
    ax.minorticks_on()
    ax.grid(visible=True, which="both", axis="y")
    (_, y_upper) = ax.get_ylim()
    ax.set_ylim(0, y_upper)

    # Second y axis on the right hand side
    if window_size != 7:
        secax = ax.secondary_yaxis(
            "right",
            functions=(lambda x: x / window_size * 7, lambda x: x / 7 * window_size),
        )
        secax.set_ylabel("eq distance per week")

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format="svg")
    svg = tmpfile.getvalue().decode("utf-8")
    # Release memory
    plt.close(fig)

    # Remove the <?xml ...><!DOCTYPE svg ... > stuff at the start
    index_of_greater_than = svg.find(">") + 1
    index_of_greater_than = svg.find(">", index_of_greater_than) + 1
    return svg[index_of_greater_than:]


def main():
    distance_per_day = goldencheetah.get_distance_per_day(sport="Run")

    now = datetime.date.today()
    if distance_per_day[now] == 0:
        # In case we are generating prior to today's run, pretend it is yesterday
        # still. Reason is otherwise you get a dip at the end of the graph for no
        # good reason.
        now = now - datetime.timedelta(days=1)
    fivehundred_days_ago = now - datetime.timedelta(days=500)
    days_for_analysis = days_range(fivehundred_days_ago, now)

    # Calculate rolling totals, generate SVGs
    svgs = []
    for window_size in DAYS:
        rolling_per_day = calculate_rolling_total(window_size, distance_per_day)
        svg = get_rolling_svg(rolling_per_day, days_for_analysis, window_size)
        svgs.append(svg)

    html = (
        "<!DOCTYPE html>"
        + "<html>"
        + '<head><meta charset="utf-8" />'
        + "<title>Rolling Total</title>"
        + "</head><body>"
        + "\n".join(svgs)
        + "<footer><p>Generated on {}.</p></footer>".format(now)
        + "</body></html>"
    )

    os.makedirs("./output", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
