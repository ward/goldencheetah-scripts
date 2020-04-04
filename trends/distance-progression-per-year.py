import datetime
import tempfile
import pathlib

GOAL_DISTANCE = 4000

def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

def goal_progression(goal, steps):
    step = goal / steps
    return [i * step for i in range(steps + 1)]

###############################################################################
####### Calculate yearly progression ##########################################
###############################################################################

# Cannot use their filter as it is terribly slow (30 seconds or so)
# Instead, filter afterwards
full_metrics = GC.seasonMetrics(all=True, filter='')
relevant_metrics = zip(full_metrics['date'], full_metrics['Distance'], full_metrics['Sport'])
metrics = list(filter(lambda threetuple: threetuple[2] == 'Run', relevant_metrics))

today = datetime.date.today()
start = datetime.date(year = full_metrics['date'][0].year, month = 1, day = 1)
a_day = datetime.timedelta(days = 1)

distances = {}
while start <= today:
    if not start.year in distances:
        distances[start.year] = [0]

    distance_today = 0
    while metrics and metrics[0][0] <= start:
        distance_today += metrics[0][1]
        metrics = metrics[1:]
    distances[start.year].append(distances[start.year][-1] + distance_today)

    start = start + a_day

###############################################################################
####### Normalise yearly progression ##########################################
###############################################################################

for year in distances:
    if is_leap_year(year):
        # Treat 28 and 29 Feb as if they were a single day
        if len(distances[year]) >= 60:
            distances[year][59] = distances[year].pop(60)
    if len(distances[year]) < 366:
        distances[year] += (366 - len(distances[year])) * [None]

###############################################################################
####### Plotting ##############################################################
###############################################################################

import plotly
import plotly.graph_objs as go

data = [go.Scatter(x = list(range(366)), y = distances[year], mode = 'lines', name = year) for year in distances]
data.append(go.Scatter(x = list(range(366)), y = goal_progression(GOAL_DISTANCE, 365), mode = 'lines', name = 'Goal'))

temp_file = tempfile.NamedTemporaryFile(mode="w+t", prefix="GC_", suffix=".html", delete=False)

f = plotly.offline.plot({
    'data': data
}, auto_open = False, filename=temp_file.name)
GC.webpage(pathlib.Path(f).as_uri())
print("DEBUG: plot saved in", temp_file.name)

