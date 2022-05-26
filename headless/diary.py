import datetime
import os

import goldencheetah

# TODO Get rid of this hack in this headless version (or keep it so I can make
# TODO a hybrid script that also runs in GC?)
# Clumsy way because the usual way creates an actual new line when saved in GC
# so a syntax error when loading it back in afterwards
NEWLINE = chr(10)


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
            text += '<p class="activity">{:.1f}km {}</p>'.format(
                activity.distance, activity.workout_code
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
            hours, minutes = goldencheetah.seconds_to_hours_minutes(others_sums[sport]["time"])
            text += '<p class="activity other">Σ {}:{:02d} {}'.format(
                hours, minutes, sport
            )
        else:
            text += '<p class="activity other">Σ {:.1f}km {}'.format(
                others_sums[sport]["distance"], sport
            )
    return text


def write_day(f, activities, idx):
    """Given a list of activities for a day, writes the HTML for it.
    Requires an idx, i.e., the day's number in the week, to know how
    far left/right on the page things need to end up."""
    if len(activities) == 0:
        return
    # Amount *ran* that day
    distance = 0
    workout = None
    run_counter = 0
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
    if workout is None:
        workout = ""
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
    last_day = days[-1]
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
        write_day(f, activities[day], idx)
    f.write(footer)


def write_training_log(f, activities):
    """Creates HTML page of a training log.
    Activities are in the format as returned by group_by_week."""
    header_a = (
        "<!DOCTYPE html>"
        "<html>"
        "<head><title>Diary</title>"
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
    with open("diary.css", "r") as css_file:
        contents = css_file.read()
        css = NEWLINE + '<style type="text/css">' + contents + "</style>" + NEWLINE
        f.write(css)


def days_range(start_day, end_day):
    """Create a list with every day frm start to end (inclusive)"""
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
    all_days = days_range(activities[0].date.date(), activities[-1].date.date())
    activities_by_day = {}
    for day in all_days:
        activities_by_day[day] = list()

    for activity in activities:
        activities_by_day[activity.date.date()].append(activity)

    activities_by_week = {}
    for day, activities in activities_by_day.items():
        week = day.strftime("%G-%V")
        try:
            activities_by_week[week]
        except KeyError:
            activities_by_week[week] = {}
        activities_by_week[week][day] = activities

    return activities_by_week


all_activities = goldencheetah.get_all_activities(sport=None)
all_activities = group_by_week(all_activities)

try:
    os.mkdir("./output")
except FileExistsError:
    pass

NAME = "./output/diary.html"
with open(NAME, "w") as tmp_f:
    write_training_log(tmp_f, all_activities)
