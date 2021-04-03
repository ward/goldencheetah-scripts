# Can I easily copy Strava's training log idea?
import math
import datetime
import tempfile
import pathlib

# Clumsy way because the usual way creates an actual new line when saved in GC
# so a syntax error when loading it back in afterwards
NEWLINE = chr(10)


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
        "speed": 7,
        "threshold": 6,
        "endurance": 5,
        "ga": 4,
        "recovery": 3,
        "warmup": 3,
        "cooldown": 3,
    }
    return importance.get(workout.lower(), 0)


def text_summary_of_day(activities_for_the_day):
    text = ""
    text += (
        '<tspan x="-50" dy="1.2em">' + str(activities_for_the_day[0].day) + "</tspan>"
    )
    for activity in activities_for_the_day:
        text += '<tspan x="-50" dy="1.2em">{:.1f}km {}</tspan>'.format(
            activity.distance, activity.workout_code
        )
    return text


def seconds_to_hours_minutes(seconds):
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds - (hours * 3600)) / 60)
    return (hours, minutes)


def write_day(f, activities, idx):
    """Given a list of activities for a day, writes the HTML for it.
    Requires an idx, i.e., the day's number in the week, to know how
    far left/right on the page things need to end up."""
    # TODO Maybe a pie chart for multiple activities? or a cluster like strava
    if len(activities) == 0:
        return
    distance = 0
    workout = ""
    for activity in activities:
        distance = distance + activity.distance
        # Deciding the "main" colour to use for a given day based on which
        # run type is the most interesting.
        if workout == "" or workout_importance(workout) < workout_importance(
            activity.workout_code
        ):
            workout = activity.workout_code
    # Could use <foreignObject>justhtmlhere</foreignObject> for word wrapping
    # SVG doesn't really do it on its own apparently
    day = (
        '<g class="day workout-{}" transform="translate({},80)">'
        '<circle r="{}" />'
        '<text class="distance">{:.1f}</text>'
        '<g class="description">'
        '<rect x="-50" y="-50"></rect>'
        '<text x="-50" y="-50">{description}</text>'
        "</g>"
        "</g>"
    )
    radius = radius_from_distance(distance)
    f.write(
        day.format(
            workout.lower(),
            idx * 100 + 50,
            radius,
            distance,
            description=text_summary_of_day(activities),
        )
    )


def sum_week_distance_time(activities):
    """Given a week of activities, i.e. a dict of day->activitiesforthatday,
    sums up all the distances and times, and returns them"""
    distance = 0
    time = 0
    for day in activities:
        for activity in activities[day]:
            distance = distance + activity.distance
            time = time + activity.time_moving
    return (distance, time)


def write_week(f, activities):
    """Handles writing for a certain week. Input is a dict of
    day -> activities for that day."""
    overview = (
        NEWLINE + '<div class="week">'
        '<div class="overview">'
        "<time>{} - {}</time>"
        '<p class="distance">{:.1f} km</p>'
        '<p class="time">{:d}h{:02d}</p>'
        "</div>"
    )
    days = [*activities]
    first_day = days[0]
    last_day = days[-1]
    distance, time = sum_week_distance_time(activities)
    hours, minutes = seconds_to_hours_minutes(time)
    overview = overview.format(first_day, last_day, distance, hours, minutes)
    header = '<svg height="160" width="825">' '<g class="days">'
    footer = "</g>" "</svg>" "</div>"
    f.write(overview)
    f.write(header)
    for idx, day in enumerate(sorted(activities)):
        write_day(f, activities[day], idx)
    f.write(footer)


def write_training_log(f, activities):
    """Creates HTML page of a training log.
    Activities are in the format as returned by group_by_week."""
    header_a = (
        "<!DOCTYPE html>"
        "<html>"
        "<head><title>Training Log</title>"
        '<meta charset="utf-8" />'
    )
    header_b = NEWLINE.join(
        [
            "</head>",
            "<body>",
            "<p>Generated on {}.</p>".format(
                datetime.datetime.now().strftime("%Y-%m-%d")
            ),
        ]
    )
    footer = NEWLINE + "</body>" "</html>"
    f.write(header_a)
    write_css(f)
    f.write(header_b)
    for week in reversed(sorted(activities)):
        write_week(f, activities[week])
    f.write(footer)


def write_css(f):
    css = (
        NEWLINE + '<style type="text/css">'
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
        "body {"
        "font-family: sans-serif;"
        "}"
        "circle, rect {"
        "stroke: black;"
        "fill: white;"
        "}"
        "g.workout-endurance circle,"
        "g.workout-endurance rect {"
        "fill: var(--endurance);"
        "stroke: white;"
        "}"
        "g.workout-ga circle,"
        "g.workout-ga rect {"
        "fill: var(--ga);"
        "stroke: white;"
        "}"
        "g.workout-interval circle, g.workout-vo2max circle,"
        "g.workout-interval rect, g.workout-vo2max rect {"
        "fill: var(--interval);"
        "stroke: white;"
        "}"
        "g.workout-race circle,"
        "g.workout-race rect {"
        "fill: var(--race);"
        "stroke: gold;"
        "stroke-width: 3px;"
        "}"
        "g.workout-recovery circle,"
        "g.workout-warmup circle,"
        "g.workout-cooldown circle,"
        "g.workout-recovery rect,"
        "g.workout-warmup rect,"
        "g.workout-cooldown rect {"
        "fill: var(--recovery);"
        "stroke: white;"
        "}"
        "g.workout-repetition circle,"
        "g.workout-speed circle,"
        "g.workout-repetition rect,"
        "g.workout-speed rect {"
        "fill: var(--repetition);"
        "stroke: white;"
        "}"
        "g.workout-threshold circle,"
        "g.workout-tempo circle,"
        "g.workout-threshold rect,"
        "g.workout-tempo rect {"
        "fill: var(--threshold);"
        "stroke: white;"
        "}"
        "g.workout-cv circle,"
        "g.workout-cv rect {"
        "fill: var(--cv);"
        "stroke: white;"
        "}"
        "g.day text.distance {"
        "text-anchor: middle;"
        "translate: 0px 5px;"
        "}"
        "div.week {"
        "display: grid;"
        'grid-template-areas: "overview days";'
        "grid-template-columns: max-content auto;"
        "}"
        "div.week div.overview {"
        "grid-area: overview;"
        "border-right: 1px dotted grey;"
        "padding-right: 1em;"
        "}"
        "div.week div.overview p.distance {"
        "font-size: 1.5em;"
        "font-weight: bold;"
        "}"
        "div.week svg {"
        "grid-area: days;"
        "}"
        "g.day g.description {"
        "display: none;"
        "}"
        "g.description rect {"
        "width: 100px;"
        "height: 100px;"
        "}"
        "g.day:hover g.description {"
        "display: inline;"
        "}"
        "</style>" + NEWLINE
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
    """Given a list of activities, returns a dict with
        week -> dict in which
                day -> activities for that day."""
    all_days = days_range(activities[0].day, activities[-1].day)
    activities_by_day = {}
    for day in all_days:
        activities_by_day[day] = list()

    for activity in activities:
        activities_by_day[activity.day].append(activity)

    activities_by_week = {}
    for day, activities in activities_by_day.items():
        week = day.strftime("%G-%V")
        try:
            activities_by_week[week]
        except KeyError:
            activities_by_week[week] = {}
        activities_by_week[week][day] = activities

    return activities_by_week


class Activity:
    def __init__(self, day, workout_code, distance, time_moving):
        self.day = day
        self.workout_code = workout_code
        self.distance = distance
        self.time_moving = time_moving


TEST_ACTIVITIES = [
    Activity(datetime.date(2020, 3, 30), "race", 42.195, 1000),
    Activity(datetime.date(2020, 3, 31), "recovery", 10, 1000),
    Activity(datetime.date(2020, 4, 1), "repetition", 17, 1000),
    Activity(datetime.date(2020, 4, 2), "recovery", 10, 1000),
    Activity(datetime.date(2020, 4, 3), "ga", 14, 1000),
    Activity(datetime.date(2020, 4, 4), "threshold", 16.5, 1000),
    Activity(datetime.date(2020, 4, 5), "recovery", 10, 1000),
    Activity(datetime.date(2020, 4, 6), "endurance", 22.5, 1000),
    Activity(datetime.date(2020, 4, 7), "recovery", 10, 1000),
    Activity(datetime.date(2020, 4, 8), "repetition", 17, 1000),
    Activity(datetime.date(2020, 4, 9), "recovery", 10, 1000),
    Activity(datetime.date(2020, 4, 10), "ga", 14, 1000),
    Activity(datetime.date(2020, 4, 11), "threshold", 16.5, 1000),
    Activity(datetime.date(2020, 4, 11), "warmup", 10, 1000),
    Activity(datetime.date(2020, 4, 12), "recovery", 10, 1000),
]


try:
    DATA = GC.seasonMetrics()
    runs = []
    for i in range(len(DATA["Distance"])):
        if DATA["Sport"][i] == "Run":
            run = Activity(
                day=DATA["date"][i],
                workout_code=DATA["Workout_Code"][i],
                distance=DATA["Distance"][i],
                time_moving=DATA["Time_Moving"][i],
            )
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
