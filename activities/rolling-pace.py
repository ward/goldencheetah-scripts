import plotly
import plotly.graph_objs as go
import tempfile
import pathlib
import numpy as np

# Currently disabled because of the following. Note: that GPS distance is not
# as precise as a race, so this versus average pace might look further/closer
# than it actually is.
# GOAL_PACE = 3 * 60 + 47.5
# Over what distance (km) to average out the pace
ROLLING_INTERVAL_LENGTH = 5.000
# Crude way to get rid of pace variance at the start of the run: just
# provide some index, those first few are clipped when deciding the yaxis
# for the graph.
CLIP_FIRST_IDX = 200
# How often to show pacing ticks
YAXIS_TICK_INTERVAL = 5
# How much buffer to show above and below the min/max pace
YAXIS_TICK_BUFFER = 2.5


def secs_to_minsec(s):
    if s is None or math.isnan(s):
        return ""
    s = math.floor(s)
    m = math.floor(s / 60)
    s = s % 60
    return "{}:{:0>2}".format(m, s)


def speed_to_pace(kph):
    """Take a speed in km per hour and turn it into a pace of minutes per km"""
    if kph is None or math.isnan(kph):
        return float("nan")
    # Avoid division by zero
    if kph == 0:
        return float("nan")
    return 3600 / kph


# goldencheetag.PythonDataSeries objects
t = GC.activity()["seconds"]
d = GC.activity()["distance"]

# km / s * 3600 = km / h
average_speed = d[-1] / t[-1] * 3600
# seconds per km
average_pace = 3600 / average_speed

rolling_time = []
rolling_speed = []

previous_rolling_index = 0
# Assumption: all those series are the same length for an activity.
for i in range(len(t)):
    if t[i] == 0:
        rolling_speed.append(None)
        rolling_time.append(None)
        continue

    if d[i] < ROLLING_INTERVAL_LENGTH:
        rolling_speed.append(d[i] / t[i] * 3600)
        rolling_time.append(None)
        continue

    # Increase previous_rolling_index till the difference to the one _after_ it
    # is smaller than the interval we care about.
    while d[i] - d[previous_rolling_index + 1] > ROLLING_INTERVAL_LENGTH:
        previous_rolling_index += 1

    d_diff = d[i] - d[previous_rolling_index]
    t_diff = t[i] - t[previous_rolling_index]
    current_rolling_speed = d_diff / t_diff * 3600
    rolling_speed.append(current_rolling_speed)
    rolling_time.append(t_diff)

# seconds per km
rolling_pace = [speed_to_pace(s) for s in rolling_speed]
# string of "m:ss" (per km)
rolling_pace_names = [secs_to_minsec(s) for s in rolling_pace]


###########################################
###########################################
###########################################
###########################################
###########################################
###########################################
###########################################


# Changing y-axis range to avoid GPS fun at the start ruining the graph.
y_axis_cleaned_min = np.nanmin(rolling_pace[CLIP_FIRST_IDX:]) - YAXIS_TICK_BUFFER
y_axis_cleaned_max = np.nanmax(rolling_pace[CLIP_FIRST_IDX:]) + YAXIS_TICK_BUFFER

# Making the ticks on the y-axis look nice
y_ticks_start = math.floor(y_axis_cleaned_min / YAXIS_TICK_INTERVAL)
y_ticks_end = math.ceil(y_axis_cleaned_max / YAXIS_TICK_INTERVAL)
y_ticks = [YAXIS_TICK_INTERVAL * i for i in range(y_ticks_start, y_ticks_end)]
y_ticks_text = [secs_to_minsec(s) for s in y_ticks]


###########################################
# Actual plotting
temp_file = tempfile.NamedTemporaryFile(
    mode="w+t", prefix="GC_", suffix=".html", delete=False
)
f = plotly.offline.plot(
    {
        "data": [
            go.Scatter(
                x=list(d),
                y=rolling_pace,
                text=rolling_pace_names,
                name="Pace",
                hoverinfo="text",
            ),
            go.Scatter(
                x=list(d),
                y=[average_pace for _ in d],
                text="Avg pace ({})".format(secs_to_minsec(average_pace)),
                hoverinfo="text",
                name="Average pace",
                # line=dict(dash="dash"),
            ),
            # go.Scatter(
            #     x=list(d),
            #     y=[GOAL_PACE for _ in d],
            #     text="Goal pace ({})".format(secs_to_minsec(GOAL_PACE)),
            #     hoverinfo="text",
            #     name="Goal pace ({})".format(secs_to_minsec(GOAL_PACE)),
            #     line=dict(dash="dash"),
            # ),
        ],
        "layout": go.Layout(
            yaxis=dict(
                tickvals=y_ticks,
                ticktext=y_ticks_text,
                # autorange="reversed",
                range=[y_axis_cleaned_max, y_axis_cleaned_min],
            )
        ),
    },
    auto_open=False,
    filename=temp_file.name,
)

GC.webpage(pathlib.Path(f).as_uri())
