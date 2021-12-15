import datetime
import math
import pathlib
import tempfile

# Doing all this extra effort writing in it Python because GoldenCheetah has a
# bug. Specifically, for their built-in charts, you cannot add, say, "Time
# Moving" twice with different filters (e.g., I want to add Time Moving for
# just Run and again for just Elliptical). Their graphs mess up entirely when
# doing this.
#
# TODO: Can I fix that GC bug?


def days_range(start_day, end_day):
    # Set start_day to the Monday (.weekday() is 0 based)
    start_day = start_day - datetime.timedelta(days=start_day.weekday())
    # Set end_day to the Sunday
    end_day = end_day + datetime.timedelta(days=6 - end_day.weekday())
    return [
        start_day + datetime.timedelta(days=days)
        for days in range((end_day - start_day).days + 1)
    ]


def seconds_to_hour_string(seconds):
    hour = math.floor(seconds / 3600)
    minutes = math.floor((seconds % 3600) / 60)
    return "{}:{:02}".format(hour, minutes)


def optional_future_data(per_week):
    last_completed_week = "2021W02"
    planning = {}
    for week in per_week.keys():
        planning[week] = math.nan
    # Overrides the math.nan
    planning[last_completed_week] = per_week[last_completed_week]["Run"] / 60
    planning["2021W03"] = 140
    planning["2021W04"] = 140
    planning["2021W05"] = 230
    planning["2021W06"] = 230
    planning["2021W07"] = 230
    planning["2021W08"] = 320
    planning["2021W09"] = 320
    planning["2021W10"] = 320
    planning["2021W11"] = 385
    planning["2021W12"] = 385
    planning["2021W13"] = 385
    planning["2021W14"] = 450
    planning["2021W15"] = 450
    planning["2021W16"] = 450
    planning["2021W17"] = 360
    planning["2021W18"] = 495
    planning["2021W19"] = 495
    planning["2021W20"] = 495
    return planning


def write_time_spent(f, all_days, per_week):
    import plotly
    import plotly.graph_objs as go

    all_weeks = sorted(per_week.keys())

    run_time = [per_week[week]["Run"] / 60 for week in all_weeks]
    elliptical_time = [per_week[week]["Elliptical"] / 60 for week in all_weeks]
    data = [
        go.Scatter(
            x=all_weeks, y=run_time, name="Run", mode="lines", marker={"color": "Blue"}
        ),
        go.Scatter(
            x=all_weeks,
            y=elliptical_time,
            name="Elliptical",
            mode="lines",
            marker={"color": "LightBlue"},
        ),
    ]
    # Set to False to disable "future" graphing
    ADD_FUTURE = True
    if ADD_FUTURE:
        planning = optional_future_data(per_week)
        planned_weeks = sorted(planning.keys())
        data.append(
            go.Scatter(
                x=planned_weeks,
                y=[planning[week] for week in planned_weeks],
                name="Future Runs",
                mode="lines",
                marker={"color": "Blue"},
                line={"dash": "dash"},
            )
        )

    plotly.offline.plot(
        {
            "data": list(reversed(data)),
            "layout": {"title": "Time spent per week", "yaxis_title": "Minutes"},
        },
        auto_open=False,
        filename=f.name,
    )


try:
    DATA = GC.seasonMetrics()
    TRACKING_SPORTS = ["Run", "Bike", "Walk", "Elliptical"]
    all_days = days_range(DATA["date"][0], DATA["date"][-1])
    per_day = {}
    for d in all_days:
        per_day[d] = {
            "Run": 0,
            "Bike": 0,
            "Walk": 0,
            "Elliptical": 0,
        }
    for i in range(len(DATA["Time_Moving"])):
        if DATA["Sport"][i] in TRACKING_SPORTS:
            per_day[DATA["date"][i]][DATA["Sport"][i]] += DATA["Time_Moving"][i]

    # Summarise per week
    per_week = {}
    for d in all_days:
        year, week_number, _ = d.isocalendar()
        week_string = "{}W{:02}".format(year, week_number)
        if week_string not in per_week:
            per_week[week_string] = {"Run": 0, "Bike": 0, "Walk": 0, "Elliptical": 0}
        per_week[week_string]["Run"] += per_day[d]["Run"]
        per_week[week_string]["Bike"] += per_day[d]["Bike"]
        per_week[week_string]["Walk"] += per_day[d]["Walk"]
        per_week[week_string]["Elliptical"] += per_day[d]["Elliptical"]
except NameError:
    all_days = []
    per_day = {}

with tempfile.NamedTemporaryFile(
    mode="w+t", prefix="GC_", suffix=".html", delete=False
) as tmp_f:
    write_time_spent(tmp_f, all_days, per_week)
    NAME = pathlib.Path(tmp_f.name).as_uri()
    print(NAME)
try:
    GC.webpage(NAME)
except NameError:
    pass
