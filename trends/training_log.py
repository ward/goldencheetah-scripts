# Can I easily copy Strava's training log idea?
import math
import datetime
import itertools
import tempfile
import pathlib

# TODO Everything ends up left aligned cause empty days get skipped. Not
# noticeable if you don't skip any day.


def radius_from_distance(distance):
    """No logic to this formula, just playing around with numbers."""
    base_size = 15
    if distance < 5:
        return base_size
    else:
        return base_size + max(0, math.log((distance - 4) / 2, 1.1))


def workout_importance(workout):
    importance = {
            'race': 10,
            'vo2max': 9,
            'interval': 9,
            'race pace': 9,
            'cv': 8,
            'repetition': 7,
            'threshold': 6,
            'endurance': 5,
            'ga': 4,
            'recovery': 3,
            'warmup': 3,
            'cooldown': 3
            }
    return importance.get(workout.lower(), 0)


def write_day(f, activities, idx):
    # Only consider first activity for now
    # TODO Maybe a pie chart? or a cluster like strava
    date = activities[0][0]
    distance = 0
    workout = ''
    for activity in activities:
        day, work, dist = activity
        distance = distance + dist
        if workout == '' or workout_importance(workout) < workout_importance(work):
            workout = work
    day = (
            '<g class="day workout-{}" transform="translate({},80)">'
            '<circle r="{}" />'
            '<text class="distance">{}</text>'
            '</g>'
            )
    r = radius_from_distance(distance)
    # print('debug', distance, 'km =', r, 'pixel radius')
    f.write(day.format(workout.lower(), idx * 100 + 50, r, distance))


def write_week(f, activities):
    header = (
            '<svg height="160" width="825">'
            '<g class="days">'
            )
    footer = (
            '</g>'
            '</svg>'
            )
    f.write(header)
    for idx, day in enumerate(activities):
        write_day(f, day, idx)
    f.write(footer)


def write_training_log(f, activities):
    header_a = (
            '<!DOCTYPE html>'
            '<html>'
            '<head>'
            )
    header_b = (
            '</head>'
            '<body>'
            )
    footer = (
            '</body>'
            '</html>'
            )
    f.write(header_a)
    write_css(f)
    f.write(header_b)
    for week in activities:
        write_week(f, week)
    f.write(footer)


def write_css(f):
    css = (
            '<style type="text/css">'
            ':root {'
            '--endurance: #0072b2;'
            '--ga: #0094e4;'
            '--recovery: #00a1f7;'
            '--interval: #e69f00;'
            '--race: #d55e00;'
            '--repetition: #f0e442;'
            '--threshold: #009e73;'
            '--cv: #5afff2;'
            '}'
            'circle {'
            'stroke: black;'
            '}'
            'g.workout-endurance circle {'
            'fill: var(--endurance);'
            '}'
            'g.workout-ga circle {'
            'fill: var(--ga);'
            '}'
            'g.workout-interval circle, g.workout-vo2max circle {'
            'fill: var(--interval);'
            '}'
            'g.workout-race circle {'
            'fill: var(--race);'
            'stroke: gold;'
            'stroke-width: 3px;'
            '}'
            'g.workout-recovery circle, g.workout-warmup circle, g.workout-cooldown circle {'
            'fill: var(--recovery);'
            '}'
            'g.workout-repetition circle {'
            'fill: var(--repetition);'
            '}'
            'g.workout-threshold circle {'
            'fill: var(--threshold);'
            '}'
            'g.workout-cv circle {'
            'fill: var(--cv);'
            '}'
            'g.day text.distance {'
            'text-anchor: middle;'
            'translate: 0px 5px;'
            'font-family: sans-serif;'
            '}'
            '</style>'
            )
    f.write(css)


def group_function(activity):
    act_date, workout, distance = activity[0]
    # Iso year and week
    return act_date.strftime("%G-%V")


def group_by_week(activities):
    activities_by_day = []
    for _day, activities_in_day in itertools.groupby(activities, lambda activity: activity[0]):
        activities_by_day.append(list(activities_in_day))

    activities_by_week = []
    for _week, activities_in_week in itertools.groupby(activities_by_day, group_function):
        activities_by_week.append(list(activities_in_week))

    return list(reversed(activities_by_week))


TEST_ACTIVITIES = [
        (datetime.date(2020, 4, 12), 'recovery', 10),
        (datetime.date(2020, 4, 11), 'threshold', 16.5),
        (datetime.date(2020, 4, 11), 'warmup', 10),
        (datetime.date(2020, 4, 10), 'ga', 14),
        (datetime.date(2020, 4, 9), 'recovery', 10),
        (datetime.date(2020, 4, 8), 'repetition', 17),
        (datetime.date(2020, 4, 7), 'recovery', 10),
        (datetime.date(2020, 4, 6), 'endurance', 22.5),
        (datetime.date(2020, 4, 5), 'recovery', 10),
        (datetime.date(2020, 4, 4), 'threshold', 16.5),
        (datetime.date(2020, 4, 3), 'ga', 14),
        (datetime.date(2020, 4, 2), 'recovery', 10),
        (datetime.date(2020, 4, 1), 'repetition', 17),
        (datetime.date(2020, 3, 31), 'recovery', 10),
        (datetime.date(2020, 3, 30), 'race', 42.195)
        ]


try:
    data = GC.seasonMetrics()
    activities = []
    for i in range(len(data['Distance'])):
        if data['Sport'][i] == 'Run':
            activity = (data['date'][i], data['Workout_Code'][i], data['Distance'][i])
            activities.append(activity)
except NameError:
    activities = TEST_ACTIVITIES
activities = group_by_week(activities)
# name = ''
with tempfile.NamedTemporaryFile(mode="w+t", prefix="GC_", suffix=".html", delete=False) as f:
    write_training_log(f, activities)
    NAME = pathlib.Path(f.name).as_uri()
    print(NAME)
try:
    GC.webpage(NAME)
except NameError:
    pass
