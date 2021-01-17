import datetime
import math
import pathlib
import tempfile


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


def write_day(f, day, day_info):
    f.write("<tr>")
    f.write("<td>{}</td>".format(day))
    f.write("<td>{}</td>".format(seconds_to_hour_string(day_info["Elliptical"])))
    f.write("<td>{}</td>".format(seconds_to_hour_string(day_info["Bike"])))
    f.write("<td>{}</td>".format(seconds_to_hour_string(day_info["Run"])))
    f.write("<td>{}</td>".format(seconds_to_hour_string(day_info["Walk"])))
    f.write("</tr>")


def write_body(f, all_days, per_day):
    table_start = (
        "<table>"
        "<thead>"
        "<tr>"
        "<th>Day</th>"
        "<th>Elliptical</th>"
        "<th>Bike</th>"
        "<th>Run</th>"
        "<th>Walk</th>"
        "</tr></thead><tbody>"
    )
    table_end = "</tbody></table>"
    f.write(table_start)
    for day in all_days:
        write_day(f, day, per_day[day])
    f.write(table_end)


def write_css(f):
    css = (
        '<style type="text/css">'
        "body { font-family: 'Ubuntu, Roboto, sans-serif'; }"
        "th, td {"
        "text-align: right;"
        "min-width: 5em;"
        "}"
        "</style>"
    )
    f.write(css)


def write_time_spent(f, all_days, per_day):
    header_a = "<!DOCTYPE html>" "<html>" "<head><title>Training Log</title>"
    header_b = "</head>" "<body>"
    footer = "</body>" "</html>"
    f.write(header_a)
    write_css(f)
    f.write(header_b)
    write_body(f, all_days, per_day)
    f.write(footer)


try:
    DATA = GC.seasonMetrics()
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
        per_day[DATA["date"][i]][DATA["Sport"][i]] += DATA["Time_Moving"][i]
except NameError:
    all_days = []
    per_day = {}

with tempfile.NamedTemporaryFile(
    mode="w+t", prefix="GC_", suffix=".html", delete=False
) as tmp_f:
    write_time_spent(tmp_f, all_days, per_day)
    NAME = pathlib.Path(tmp_f.name).as_uri()
    print(NAME)
try:
    GC.webpage(NAME)
except NameError:
    pass
