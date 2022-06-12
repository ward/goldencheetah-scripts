# Parse GC data to create graphs without needing to start up GoldenCheetah

import math
import json
import datetime

RIDEDB_FILE = "./rideDB.json"


def parse_ridedb():
    # This encoding handles the BOM character at the start of the file
    with open(RIDEDB_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
        return data["RIDES"]


def get_activities(ridedb, activity_type="Run"):
    if activity_type == None:
        return ridedb
    else:
        return filter(lambda activity: activity["sport"] == activity_type, ridedb)


class Activity:
    def __init__(self, ridedb_entry):
        """Parse from a ridedb entry"""
        self.date = datetime.datetime.strptime(
            ridedb_entry["date"], "%Y/%m/%d %H:%M:%S %Z"
        )
        self.sport = ridedb_entry["sport"]
        try:
            self.distance = float(ridedb_entry["METRICS"]["total_distance"])
        except KeyError:
            self.distance = 0
        self.time_elapsed = ridedb_entry["METRICS"]["workout_time"]
        # Assume if recording, we're moving. GC also has time_riding.
        try:
            self.time_moving = ridedb_entry["METRICS"]["time_recording"]
        except KeyError:
            self.time_moving = ridedb_entry["METRICS"]["workout_time"]
        self.time_moving = int(float(self.time_moving))

        try:
            workout_code = ridedb_entry["TAGS"]["Workout Code"].strip()
        except KeyError:
            workout_code = ""
        if workout_code == "":
            self.workout_code = None
        else:
            self.workout_code = workout_code

    def __str__(self):
        return "{} on {}: {} km in {} s".format(
            self.sport, self.date, self.distance, self.time_moving
        )


def get_all_activities(sport="Run"):
    """Parses rideDB into list of Activity. Filters on given sport. No filtering if sport is None."""
    data = parse_ridedb()
    runs = get_activities(data, sport)
    parsed = map(lambda d: Activity(d), runs)
    return list(parsed)


def days_range(start_day, end_day):
    return [
        start_day + datetime.timedelta(days=days)
        for days in range((end_day - start_day).days + 1)
    ]


def get_distance_per_day(sport="Run"):
    activities = get_all_activities(sport)
    start_day = activities[0].date.date()
    end_day = datetime.date.today()
    all_days = days_range(start_day, end_day)
    per_day = {}
    for d in all_days:
        per_day[d] = 0

    for activity in activities:
        per_day[activity.date.date()] += activity.distance

    return per_day


def seconds_to_hours_minutes(seconds):
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds - (hours * 3600)) / 60)
    return (hours, minutes)


def days_range(start_day, end_day):
    """Create a list with every day from Monday of the week of the start to
    Sunday of the week of the end (inclusive)."""
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


if __name__ == "__main__":
    data = parse_ridedb()
    runs = get_activities(data, "Run")
    parsed = map(lambda d: Activity(d), runs)
    for a in parsed:
        print(a)
