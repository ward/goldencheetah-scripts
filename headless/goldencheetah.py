# Parse GC data to create graphs without needing to start up GoldenCheetah

import math
import json
import datetime
import pickle

RIDEDB_FILE = "./rideDB.json"
PICKLE_FILE = "./rideDB.pickle"


def parse_ridedb():
    # This encoding handles the BOM character at the start of the file
    with open(RIDEDB_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
        return data["RIDES"]


class Activity:
    distance: float
    """Distance of the activity in kilometer. 0 if no distance metric found"""

    def __init__(self, ridedb_entry):
        """Parse from a ridedb entry"""
        # This time seems to be UTC... so that is annoying. Going to start to
        # make a habit of marking some activities with a `tz:utc±N` in the
        # keywords. Feels like a bandaid, but works also for activities without
        # a GPS track to use for a location.
        self.date = datetime.datetime.strptime(
            ridedb_entry["date"], "%Y/%m/%d %H:%M:%S %Z"
        )
        self.sport = ridedb_entry["sport"]
        try:
            self.distance = float(ridedb_entry["METRICS"]["total_distance"])
        except KeyError:
            self.distance = float(0)
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

        # Keywords
        self.keywords: list[str] = []
        try:
            keywords: list[str] = ridedb_entry["TAGS"]["Keywords"].split(",")
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword != "":
                    self.keywords.append(keyword)
                if keyword.startswith("datetime-"):
                    # Magic keyword overrides datetime property
                    try:
                        self.date = datetime.datetime.strptime(
                            keyword[9:], "%Y%m%dT%H%M%S"
                        )
                    except ValueError:
                        print(
                            "Failed to parse magic keyword 'datetime-YYYYMMDDTHHMMSS'"
                        )
        except KeyError:
            pass

        # Laps / intervals. Skipping the "entire activity" one. Keeping same
        # order as given.
        self.intervals = []
        for interval in ridedb_entry.get("INTERVALS", []):
            try:
                i = ActivityInterval(interval)
                if i.name != "Entire Activity":
                    self.intervals.append(i)
            except:
                pass

    def __str__(self):
        return "{} on {}: {} km in {} s".format(
            self.sport, self.date, self.distance, self.time_moving
        )


class ActivityInterval:
    def __init__(self, intervaldict: dict):
        self._startSeconds = int(intervaldict["start"])
        self._stopSeconds = int(intervaldict["stop"])
        self._startKm = float(intervaldict["startKM"])
        self._stopKm = float(intervaldict["stopKM"])
        self.name = intervaldict["name"].strip()

    def distance(self):
        """Kilometer"""
        return round(self._stopKm - self._startKm, 1)

    def time(self):
        """Seconds"""
        return self._stopSeconds - self._startSeconds

    def pace(self) -> int:
        """Seconds per km"""
        d = self._stopKm - self._startKm
        if d == 0:
            return 0
        else:
            t = self._stopSeconds - self._startSeconds
            return int(t / d)

    def to_hover_text(self):
        """Format interval as text for hover tooltips."""
        t = self.time()
        if t > 0:
            m, s = math.floor(t / 60), t % 60
            return f"{self.name}: {self.distance():.1f}km in {m}:{s:02d}"
        else:
            return f"{self.name}: {self.distance():.1f}km"


def ridedb_to_pickle():
    ridedb = parse_ridedb()
    activities = list(map(lambda d: Activity(d), ridedb))
    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(activities, f)


def pickle_to_activities() -> list[Activity]:
    """Read in the pickle file that has parsed activities."""
    with open(PICKLE_FILE, "rb") as f:
        activities = pickle.load(f)
        return activities


def get_all_activities(sport="Run") -> list[Activity]:
    """Reads activities from pickle. Filters on given sport. No filtering if
    sport is None."""
    activities = pickle_to_activities()
    if sport is None:
        return activities
    else:
        runs: list[Activity] = list(filter(lambda act: act.sport == sport, activities))
        return runs


def days_range(start_day, end_day):
    """Return a list with every day from start_day to end_day (inclusive)."""
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


def days_range_normalised_to_week(
    start_day: datetime.date, end_day: datetime.date
) -> list[datetime.date]:
    """Create a list with every day from Monday of the week of start_day to
    Sunday of the week of the end_day (inclusive)."""
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
    all_days = days_range_normalised_to_week(
        activities[0].date.date(), activities[-1].date.date()
    )
    activities_by_day: dict[datetime.date, list[Activity]] = {}
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
    runs = get_all_activities(sport="Run")
    for run in runs:
        print(run)
