import datetime
import os

import goldencheetah

# TODO Get rid of this hack in this headless version (or keep it so I can make
# TODO a hybrid script that also runs in GC?)
# Clumsy way because the usual way creates an actual new line when saved in GC
# so a syntax error when loading it back in afterwards
NEWLINE = chr(10)

HARDCODED_EXCUSES = {
    datetime.date(2025, 10, 13): "Lazy (and maybe slightly sick)",
    datetime.date(2025, 10, 9): "Sick",
    datetime.date(2025, 8, 8): "Flying",
    datetime.date(2025, 8, 6): "No tracking, some short walks",
    datetime.date(2025, 7, 24): "Flying",
    datetime.date(2025, 7, 4): "Flying",
    datetime.date(2025, 4, 22): "Right achilles pain",
    datetime.date(2025, 3, 7): "Flying",
    datetime.date(2025, 2, 2): "Left patella tendon says no",
    datetime.date(2025, 1, 25): "Left patella tendon says no",
    datetime.date(2024, 12, 30): "Give myself more rest",
    datetime.date(2024, 12, 29): "Flying",
    datetime.date(2024, 12, 25): "Xmas, too tired",
    datetime.date(2024, 12, 24): "Xmas eve, no time",
    datetime.date(2024, 12, 18): "Landing & jetlag",
    datetime.date(2024, 12, 17): "Flying",
    datetime.date(2024, 12, 14): "Too lazy",
    datetime.date(2024, 10, 21): "Interviewing",
    datetime.date(2024, 9, 30): "Twisted ankle, swollen",
    datetime.date(2024, 8, 25): "Flying",
    datetime.date(2024, 7, 30): "Landing & jetlag",
    datetime.date(2024, 6, 5): "Flying",
    datetime.date(2024, 5, 26): "Exhaustion, lying around",
    datetime.date(2024, 4, 27): "Respiratory illness",
    datetime.date(2024, 4, 26): "Respiratory illness",
    datetime.date(2024, 4, 22): "Public defence",
    datetime.date(2024, 3, 22): "Private defence",
    datetime.date(2024, 3, 10): "Montchabrol",
    datetime.date(2024, 2, 21): "Dissertation done ⇒ drinks",
    datetime.date(2024, 1, 14): "Fly (and tired)",
    datetime.date(2024, 1, 13): "Fly (and lazy)",
    datetime.date(2023, 11, 27): "No time",
    datetime.date(2023, 10, 11): "Roughed up by kine (still patella tendinitis…)",
    datetime.date(2023, 10, 9): "Arrive and ded",
    datetime.date(2023, 10, 8): "Fly Bogota→Home",
    datetime.date(2023, 9, 7): "Do nothing, wait for kine apt (patella tendinitis)",
    datetime.date(2023, 9, 6): "Do nothing, wait for kine apt (patella tendinitis)",
    datetime.date(2023, 9, 4): "Do nothing, wait for kine apt (patella tendinitis)",
    datetime.date(2023, 8, 28): "Give knee some more rest (patella tendinitis)",
    datetime.date(2023, 8, 22): "Give knee some rest (eventually: patella tendinitis)",
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
        "m-pace": 6,
        "endurance": 5,
        "ga": 4,
        "recovery": 3,
        "warmup": 3,
        "cooldown": 3,
    }
    return importance.get(workout.lower(), 0)


def format_intervals_for_hover(intervals):
    """Formats interval data into a readable string for hover tooltips."""
    if not intervals:
        return ""

    return "\n".join(interval.to_hover_text() for interval in intervals)


def write_days_activities(activities_for_the_day):
    text = ""
    for activity in activities_for_the_day:
        if activity.sport == "Run":
            strides_text = ""
            if "strides" in activity.keywords:
                strides_text = "<sup>st</sup>"

            # Add hover info for Repetition and VO2max workouts
            title_attr = ""
            if (
                activity.workout_code
                and workout_importance(activity.workout_code.lower()) > 5
            ):
                intervals_text = format_intervals_for_hover(activity.intervals)
                if intervals_text:
                    # HTML escape the title attribute content
                    intervals_text = intervals_text.replace('"', "&quot;")
                    title_attr = f' title="{intervals_text}"'

            text += '<p class="activity"{}>{:.1f}km {}{}</p>'.format(
                title_attr, activity.distance, activity.workout_code, strides_text
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


class WeekSum:
    distance: float = 0
    time: int = 0
    bike_distance: float = 0
    bike_time: int = 0
    walk_distance: float = 0
    walk_time: int = 0
    elliptical_time: int = 0
    swim_distance: float = 0
    swim_time: int = 0

    def add_activity(self, activity):
        if activity.sport == "Run":
            self.distance = self.distance + activity.distance
            self.time = self.time + activity.time_moving
        elif activity.sport == "Bike":
            self.bike_distance = self.bike_distance + activity.distance
            self.bike_time = self.bike_time + activity.time_moving
        elif activity.sport == "Walk":
            self.walk_distance = self.walk_distance + activity.distance
            self.walk_time = self.walk_time + activity.time_moving
        elif activity.sport == "Elliptical":
            self.elliptical_time = self.elliptical_time + activity.time_moving
        elif activity.sport == "Swim":
            self.swim_distance = self.swim_distance + activity.distance
            self.swim_time = self.swim_time + activity.time_moving


def sum_week_distance_time(activities):
    """Given a week of activities, i.e. a dict of day->activitiesforthatday,
    sums up all the distances and times for runs, and returns them"""
    sums = WeekSum()
    for day in activities:
        for activity in activities[day]:
            sums.add_activity(activity)
    return sums


def write_week(f, activities):
    """Handles writing for a certain week. Input is a dict of
    day -> activities for that day."""
    days = [*activities]
    first_day = days[0]
    sums = sum_week_distance_time(activities)
    hours, minutes = goldencheetah.seconds_to_hours_minutes(sums.time)
    isodate = first_day.isocalendar()
    overview = (
        NEWLINE + '<div class="week">'
        '<time class="when">{}W{}</time>'
        '<p class="total-distance">{:.1f} km</p>'
        '<p class="total-time">{:d}h{:02d}</p>'
    )
    overview = overview.format(
        isodate.year, isodate.week, sums.distance, hours, minutes
    )
    if sums.bike_distance > 0:
        bike_html = '<p class="total-biking">{:.0f}km, {:d}h{:02d}</p>'
        hours, minutes = goldencheetah.seconds_to_hours_minutes(sums.bike_time)
        bike_html = bike_html.format(sums.bike_distance, hours, minutes)
        overview += bike_html
    if sums.walk_distance > 0:
        walk_html = '<p class="total-walking">{:.0f}km, {:d}h{:02d}</p>'
        hours, minutes = goldencheetah.seconds_to_hours_minutes(sums.walk_time)
        walk_html = walk_html.format(sums.walk_distance, hours, minutes)
        overview += walk_html
    if sums.swim_distance > 0:
        swim_html = '<p class="total-swimming">{:.0f}m, {:d}h{:02d}</p>'
        hours, minutes = goldencheetah.seconds_to_hours_minutes(sums.swim_time)
        swim_html = swim_html.format(sums.swim_distance * 1000, hours, minutes)
        overview += swim_html
    if sums.elliptical_time > 0:
        ell_html = '<p class="total-elliptical">{:d}h{:02d}</p>'
        hours, minutes = goldencheetah.seconds_to_hours_minutes(sums.elliptical_time)
        ell_html = ell_html.format(hours, minutes)
        overview += ell_html
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


def adjust_date_of_activity(activity: goldencheetah.Activity):
    """Mutates the date(time) of the activity based on finding a `tz:utc±N` in
    the activity's keywords."""
    # TODO: I think GC might just be buggy too? For example:
    # I did an elliptical in Belgium on 16 Jan 2024 at 19:36.
    # This looks correct in the activity's file, 18:36 UTC.
    # In the rideDB.json file the date instead says
    # 17 Jan 2024, 0:36 UTC.
    # Might depend on what timezone I am currently in? Either way, messy.
    # Not sure I can find a good workaround that will work in all cases.
    # Also note that the GC interface correctly(?) says 19:36 while I am in the US!
    # Maybe I should try using filename instead, that seems to be localtime.
    # Will have to find out whether that also is correct for activities done in
    # one timezone, imported into GC in another timezone.
    for kw in activity.keywords:
        if kw.startswith("tz:utc"):
            try:
                offset = int(kw[6:])
                activity.date = activity.date + datetime.timedelta(hours=offset)
                return
            except ValueError:
                pass


all_activities = goldencheetah.get_all_activities(sport=None)
for activity in all_activities:
    adjust_date_of_activity(activity)
all_activities = goldencheetah.group_by_week(all_activities)

try:
    os.mkdir("./output")
except FileExistsError:
    pass

NAME = "./output/diary.html"
with open(NAME, "w") as tmp_f:
    write_training_log(tmp_f, all_activities)
