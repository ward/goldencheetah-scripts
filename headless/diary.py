import datetime
import os

import goldencheetah

# TODO Get rid of this hack in this headless version (or keep it so I can make
# TODO a hybrid script that also runs in GC?)
# Clumsy way because the usual way creates an actual new line when saved in GC
# so a syntax error when loading it back in afterwards
NEWLINE = chr(10)

HARDCODED_EXCUSES = {
    datetime.date(2023, 8, 1): "Fly",
    datetime.date(2023, 7, 30): "Ill: breathing, exhaustion + pulled back",
    datetime.date(2023, 7, 29): "Ill: breathing, exhaustion",
    datetime.date(2023, 7, 28): "Ill: breathing, exhaustion",
    datetime.date(2023, 7, 3): "Fly",
    datetime.date(2023, 3, 21): "Stomach bug",
    datetime.date(2023, 3, 20): "Stomach bug",
    datetime.date(2023, 3, 19): "Stomach bug",
    datetime.date(2023, 3, 18): "Stomach bug",
    datetime.date(2023, 1, 23): "Return from USA",
    datetime.date(2023, 1, 9): "Food poisoning",
    datetime.date(2022, 12, 29): "Non-covid respiratory suffering",
    datetime.date(2022, 12, 23): "Fly to USA",
    datetime.date(2022, 8, 15): "Travel London to Carqueiranne",
    datetime.date(2022, 8, 3): "Blood blister + return from USA",
    datetime.date(2022, 7, 15): "Fly to USA",
    datetime.date(2022, 7, 3): "Left hip lateral",
    datetime.date(2022, 6, 20): "COVID19",
    datetime.date(2022, 6, 19): "COVID19",
    datetime.date(2022, 6, 18): "COVID19",
    datetime.date(2022, 6, 17): "COVID19",
    datetime.date(2022, 4, 1): "Return from USA",
    datetime.date(2022, 3, 18): "Headache, tired, fearing Tina's bronchitis",
    datetime.date(2020, 10, 14): "Broken ankle",
    datetime.date(2020, 10, 13): "Broken ankle",
    datetime.date(2020, 10, 1): "Broken ankle",
    datetime.date(2020, 9, 30): "Broken ankle",
    datetime.date(2020, 9, 29): "Broken ankle",
    datetime.date(2020, 9, 28): "Broken ankle",
    datetime.date(2020, 9, 27): "Broken ankle",
    datetime.date(2020, 9, 26): "Broken ankle",
    datetime.date(2020, 9, 25): "Broken ankle",
    datetime.date(2020, 9, 24): "Broken ankle",
    datetime.date(2020, 9, 23): "Broken ankle",
    datetime.date(2020, 9, 22): "Broken ankle",
    datetime.date(2020, 9, 21): "Broken ankle",
    datetime.date(2020, 9, 20): "Broken ankle",
    datetime.date(2020, 9, 19): "Broken ankle",
    datetime.date(2020, 9, 17): "Broken ankle",
    datetime.date(2020, 9, 16): "Broken ankle",
    datetime.date(2020, 9, 15): "Broken ankle",
    datetime.date(2020, 9, 14): "Broken ankle",
    datetime.date(2020, 9, 13): "Broken ankle",
    datetime.date(2020, 9, 12): "Broken ankle",
    datetime.date(2020, 9, 11): "Broken ankle",
    datetime.date(2020, 9, 10): "Broken ankle",
    datetime.date(2020, 9, 9): "Broken ankle",
    datetime.date(2020, 9, 8): "Broken ankle",
    datetime.date(2020, 9, 7): "Broken ankle",
}


def workout_importance(workout):
    if workout is None:
        return 0

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


def write_days_activities(activities_for_the_day):
    text = ""
    for activity in activities_for_the_day:
        if activity.sport == "Run":
            strides_text = ""
            if "strides" in activity.keywords:
                strides_text = "<sup>st</sup>"
            text += '<p class="activity">{:.1f}km {}{}</p>'.format(
                activity.distance, activity.workout_code, strides_text
            )
    others_sums = {}
    for activity in activities_for_the_day:
        if activity.sport != "Run":
            if activity.sport not in others_sums:
                others_sums[activity.sport] = {"distance": 0, "time": 0}
            others_sums[activity.sport]["distance"] += activity.distance
            others_sums[activity.sport]["time"] += activity.time_moving
    for sport in others_sums:
        if sport == "Elliptical":
            hours, minutes = goldencheetah.seconds_to_hours_minutes(
                others_sums[sport]["time"]
            )
            text += '<p class="activity other">Σ {}:{:02d} {}'.format(
                hours, minutes, sport
            )
        else:
            text += '<p class="activity other">Σ {:.1f}km {}'.format(
                others_sums[sport]["distance"], sport
            )
    return text


def write_day(f, activities, excuse, idx):
    """Given a list of activities for a day, writes the HTML for it.
    Requires an idx, i.e., the day's number in the week, to know how
    far left/right on the page things need to end up."""

    # Only write out an excuse if there is no activity that day.
    if len(activities) == 0:
        # If we have an excuse anyway
        if excuse is None:
            return
        day = '<div class="day day-{} workout-excuse">{}</div>'.format(idx, excuse)
        f.write(day)
        return

    # Amount *ran* that day
    distance = 0
    workout = None
    run_counter = 0
    has_sport_other_than_running = False
    for activity in activities:
        if activity.sport == "Run":
            run_counter += 1
            distance = distance + activity.distance
            # Deciding the "main" colour to use for a given day based on which
            # run type is the most interesting.
            if workout is None or workout_importance(workout) < workout_importance(
                activity.workout_code
            ):
                workout = activity.workout_code
        else:
            has_sport_other_than_running = True
    if workout is None:
        if has_sport_other_than_running:
            workout = "not-a-run"
        else:
            workout = "nothing"
    day = '<div class="day day-{} workout-{}">'.format(idx, workout.lower())
    day += "<datetime>" + activities[0].date.strftime("%-d %h") + "</datetime>"
    if run_counter > 1:
        day += '<p class="distance">Σ {:.1f}km</p>'.format(distance)
    day += write_days_activities(activities)
    day += "</div>"
    f.write(day)


def sum_week_distance_time(activities):
    """Given a week of activities, i.e. a dict of day->activitiesforthatday,
    sums up all the distances and times for runs, and returns them"""
    distance = 0
    time = 0
    for day in activities:
        for activity in activities[day]:
            if activity.sport == "Run":
                distance = distance + activity.distance
                time = time + activity.time_moving
    return (distance, time)


def write_week(f, activities):
    """Handles writing for a certain week. Input is a dict of
    day -> activities for that day."""
    days = [*activities]
    first_day = days[0]
    distance, time = sum_week_distance_time(activities)
    hours, minutes = goldencheetah.seconds_to_hours_minutes(time)
    isodate = first_day.isocalendar()
    overview = (
        NEWLINE + '<div class="week">'
        '<time class="when">{}W{}</time>'
        '<p class="total-distance">{:.1f} km</p>'
        '<p class="total-time">{:d}h{:02d}</p>'
    )
    overview = overview.format(isodate.year, isodate.week, distance, hours, minutes)
    header = ""
    footer = "" "</div>"
    f.write(overview)
    f.write(header)
    for idx, day in enumerate(sorted(activities)):
        write_day(f, activities[day], HARDCODED_EXCUSES.get(day), idx)
    f.write(footer)


def write_training_log(f, activities):
    """Creates HTML page of a training log.
    Activities are in the format as returned by group_by_week."""
    header_a = (
        "<!DOCTYPE html>"
        "<html>"
        "<head><title>Diary</title>"
        '<meta charset="utf-8" />'
        '<meta name="viewport" content="width=device-width, initial-scale=1" />'
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
    with open("diary.css", "r") as css_file:
        contents = css_file.read()
        css = NEWLINE + '<style type="text/css">' + contents + "</style>" + NEWLINE
        f.write(css)


all_activities = goldencheetah.get_all_activities(sport=None)
all_activities = goldencheetah.group_by_week(all_activities)

try:
    os.mkdir("./output")
except FileExistsError:
    pass

NAME = "./output/diary.html"
with open(NAME, "w") as tmp_f:
    write_training_log(tmp_f, all_activities)
