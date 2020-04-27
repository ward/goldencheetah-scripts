# BIG ASSUMPTION: All intervals are sequential. In other words, this breaks if you add some extra overlapping intervals afterwards.
import plotly
import plotly.graph_objs as go
import math
import tempfile
import pathlib


def secs_to_minsec(s):
    s = math.floor(s)
    m = math.floor(s / 60)
    s = s % 60
    return "{}:{:0>2}".format(m, s)


# GC.activityIntervals is a dictionary where every entry gives a list of the metrics for every interval
intervals = GC.activityIntervals(type="USER")
lap_speed = intervals["Average_Speed"]
lap_speed = [3600 / s for s in lap_speed]
lap_distances = intervals["Distance"]
lap_names = intervals["name"]
total_speed = GC.activityIntervals(type="ALL")["Average_Speed"][0]
total_speed = 3600 / total_speed
# Calculate cumulative distance at the end of every interval
lap_distances_acc = [0]
for distance in lap_distances:
    lap_distances_acc.append(lap_distances_acc[-1] + distance)

# We want the metric for an interval to be repeated for all points in the interval such that we can plot a sort of bar-line graph.
# Create the arrays for all that
filled_speed = []
filled_distance = []
filled_names = []
DISTANCE_STEP_SIZE = 100
for ii in range(0, int(math.ceil(DISTANCE_STEP_SIZE * lap_distances_acc[-1]))):
    i = ii / DISTANCE_STEP_SIZE
    filled_distance.append(i)
    # Find the speed to fill in
    idx = len(list(filter(lambda d: d < i, lap_distances_acc))) - 1
    idx = max(idx, 0)
    idx = min(idx, len(lap_speed) - 1)
    filled_speed.append(lap_speed[idx])
    filled_names.append("{}: {}".format(lap_names[idx], secs_to_minsec(lap_speed[idx])))


###########################################
# Making the ticks on the y-axis look nice
y_ticks_start = math.floor(min(filled_speed) / 15)
y_ticks_end = math.ceil(max(filled_speed) / 15)
y_ticks = [15 * i for i in range(y_ticks_start, y_ticks_end)]
y_ticks_text = [secs_to_minsec(s) for s in y_ticks]
###########################################


###########################################
# Actual plotting
temp_file = tempfile.NamedTemporaryFile(
    mode="w+t", prefix="GC_", suffix=".html", delete=False
)
f = plotly.offline.plot(
    {
        "data": [
            go.Scatter(
                x=filled_distance,
                y=filled_speed,
                text=filled_names,
                name="Speed per interval",
                hoverinfo="text",
            ),
            go.Scatter(
                x=filled_distance,
                y=[total_speed for _ in filled_distance],
                text=secs_to_minsec(total_speed),
                hoverinfo="text",
                name="Average speed",
                line=dict(dash="dash"),
            ),
        ],
        "layout": go.Layout(
            yaxis=dict(tickvals=y_ticks, ticktext=y_ticks_text, autorange="reversed",)
        ),
    },
    auto_open=False,
    filename=temp_file.name,
)

GC.webpage(pathlib.Path(f).as_uri())
