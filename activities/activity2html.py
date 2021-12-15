import tempfile
import pathlib
import math


def seconds_to_min_sec(seconds):
    seconds = math.floor(seconds)
    s = seconds % 60
    m = math.floor(seconds / 60)
    return "{}:{:02}".format(m, s)


def write_activity(f, metrics):
    f.write("<html><head><meta charset='utf-8' /></head><body>")

    title = metrics["Sport"]
    if metrics["Workout_Code"] != "":
        title = metrics["Workout_Code"] + " " + title
    f.write("<h1>{}</h1>".format(title))

    f.write("<ul>")
    f.write("<li>{:.1f} km</li>".format(metrics["Distance"]))
    f.write(
        "<li>{} (elapsed: {})</li>".format(
            seconds_to_min_sec(metrics["Time_Moving"]),
            seconds_to_min_sec(metrics["Time_Recording"]),
        )
    )
    pace = 0
    if metrics["Average_Speed"] > 0:
        pace = 3600 / metrics["Average_Speed"]
    pace = seconds_to_min_sec(pace)
    f.write("<li>{} / km</li>".format(pace))
    f.write("<li>{:.0f} HR</li>".format(metrics["Average_Heart_Rate"]))

    f.write("</ul>")

    # Write in unicode to try to avoid GC's (de)serialising breaking the code
    notes = metrics["Notes"].replace("\u000A", "<br />")
    f.write("<p>{}</p>".format(notes))

    # Debug the metrics
    f.write("<hr /><ul>")
    the_keys = sorted(metrics.keys())
    for metric in the_keys:
        f.write("<li>{}: {}</li>".format(metric, metrics[metric]))
    f.write("</ul>")

    f.write("</body></html>")


with tempfile.NamedTemporaryFile(
    mode="w+t", prefix="GC_activity_", suffix=".html", delete=False
) as tmp_f:
    try:
        metrics = GC.activityMetrics()
    except NameError:
        metrics = {}

    write_activity(tmp_f, metrics)
    NAME = pathlib.Path(tmp_f.name).as_uri()
    print(NAME)
try:
    GC.webpage(NAME)
except NameError:
    pass
