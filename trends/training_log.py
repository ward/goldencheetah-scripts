# Can I easily copy Strava's training log idea?
import math
import datetime
import tempfile
import pathlib


def radius_from_distance(distance):
    """No logic to this formula, just playing around with numbers."""
    base_size = 15
    if distance < 5:
        return base_size
    else:
        return base_size + max(0, math.log((distance - 4) / 2, 1.1))


def workout_importance(workout):
    importance = {
        "race": 10,
        "vo2max": 9,
        "interval": 9,
        "race pace": 9,
        "cv": 8,
        "repetition": 7,
        "threshold": 6,
        "endurance": 5,
        "ga": 4,
        "recovery": 3,
        "warmup": 3,
        "cooldown": 3,
    }
    return importance.get(workout.lower(), 0)


def text_summary_of_day(activities):
    text = ""
    text += str(activities[0][0])
    for activity in activities:
        _day, work, dist = activity
        text += "\n{:.1f}km {}".format(dist, work)
    return text


def write_day(f, activities, idx):
    # TODO Maybe a pie chart for multiple activities? or a cluster like strava
    if len(activities) == 0:
        return
    distance = 0
    workout = ""
    for activity in activities:
        day, work, dist = activity
        distance = distance + dist
        if workout == "" or workout_importance(workout) < workout_importance(work):
            workout = work
    day = (
        '<g class="day workout-{}" transform="translate({},80)">'
        "<title>{}</title>"
        '<circle r="{}" />'
        '<text class="distance">{:.1f}</text>'
        "</g>"
    )
    radius = radius_from_distance(distance)
    f.write(
        day.format(
            workout.lower(),
            idx * 100 + 50,
            text_summary_of_day(activities),
            radius,
            distance,
        )
    )


def write_week(f, activities):
    header = '<svg height="160" width="825">' '<g class="days">'
    footer = "</g>" "</svg>"
    f.write(header)
    for idx, day in enumerate(sorted(activities)):
        write_day(f, activities[day], idx)
    f.write(footer)


def write_training_log(f, activities):
    header_a = "<!DOCTYPE html>" "<html>" "<head>"
    header_b = "</head>" "<body>"
    footer = "</body>" "</html>"
    f.write(header_a)
    write_css(f)
    f.write(header_b)
    for week in reversed(sorted(activities)):
        write_week(f, activities[week])
    f.write(footer)


def write_css(f):
    css = (
        '<style type="text/css">'
        ":root {"
        "--endurance: #0072b2;"
        "--ga: #0094e4;"
        "--recovery: #00a1f7;"
        "--interval: #e69f00;"
        "--race: #d55e00;"
        "--repetition: #f0e442;"
        "--threshold: #009e73;"
        "--cv: #5afff2;"
        "}"
        "circle {"
        "stroke: black;"
        "}"
        "g.workout-endurance circle {"
        "fill: var(--endurance);"
        "}"
        "g.workout-ga circle {"
        "fill: var(--ga);"
        "}"
        "g.workout-interval circle, g.workout-vo2max circle {"
        "fill: var(--interval);"
        "}"
        "g.workout-race circle {"
        "fill: var(--race);"
        "stroke: gold;"
        "stroke-width: 3px;"
        "}"
        "g.workout-recovery circle,"
        "g.workout-warmup circle,"
        "g.workout-cooldown circle {"
        "fill: var(--recovery);"
        "}"
        "g.workout-repetition circle {"
        "fill: var(--repetition);"
        "}"
        "g.workout-threshold circle {"
        "fill: var(--threshold);"
        "}"
        "g.workout-cv circle {"
        "fill: var(--cv);"
        "}"
        "g.day text.distance {"
        "text-anchor: middle;"
        "translate: 0px 5px;"
        "font-family: sans-serif;"
        "}"
        "</style>"
    )
    f.write(css)


def days_range(start_day, end_day):
    # Set start_day to the Monday (.weekday() is 0 based)
    start_day = start_day - datetime.timedelta(days=start_day.weekday())
    # Set end_day to the Sunday
    end_day = end_day + datetime.timedelta(days=6 - end_day.weekday())
    return [
        start_day + datetime.timedelta(days=days)
        for days in range((end_day - start_day).days + 1)
    ]


def group_by_week(activities):
    all_days = days_range(activities[0][0], activities[-1][0])
    activities_by_day = {}
    for day in all_days:
        activities_by_day[day] = list()

    for activity in activities:
        activities_by_day[activity[0]].append(activity)

    activities_by_week = {}
    for day, activities in activities_by_day.items():
        week = day.strftime("%G-%V")
        try:
            activities_by_week[week]
        except KeyError:
            activities_by_week[week] = {}
        activities_by_week[week][day] = activities

    return activities_by_week


TEST_ACTIVITIES = [
    (datetime.date(2020, 3, 30), "race", 42.195),
    # (datetime.date(2020, 3, 31), 'recovery', 10),
    (datetime.date(2020, 4, 1), "repetition", 17),
    (datetime.date(2020, 4, 2), "recovery", 10),
    (datetime.date(2020, 4, 3), "ga", 14),
    (datetime.date(2020, 4, 4), "threshold", 16.5),
    (datetime.date(2020, 4, 5), "recovery", 10),
    (datetime.date(2020, 4, 6), "endurance", 22.5),
    (datetime.date(2020, 4, 7), "recovery", 10),
    (datetime.date(2020, 4, 8), "repetition", 17),
    # (datetime.date(2020, 4, 9), 'recovery', 10),
    # (datetime.date(2020, 4, 10), 'ga', 14),
    (datetime.date(2020, 4, 11), "threshold", 16.5),
    (datetime.date(2020, 4, 11), "warmup", 10),
    (datetime.date(2020, 4, 12), "recovery", 10),
]


try:
    DATA = GC.seasonMetrics()
    runs = []
    for i in range(len(DATA["Distance"])):
        if DATA["Sport"][i] == "Run":
            run = (DATA["date"][i], DATA["Workout_Code"][i], DATA["Distance"][i])
            runs.append(run)
except NameError:
    runs = TEST_ACTIVITIES
runs = group_by_week(runs)
with tempfile.NamedTemporaryFile(
    mode="w+t", prefix="GC_", suffix=".html", delete=False
) as tmp_f:
    write_training_log(tmp_f, runs)
    NAME = pathlib.Path(tmp_f.name).as_uri()
    print(NAME)
try:
    GC.webpage(NAME)
except NameError:
    pass
