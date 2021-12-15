import json
import datetime


class MyActivity:
    def __init__(self, date, distance, time):
        self.date = date
        self.distance = distance
        self.time = time

        (self.year, self.week, _) = date.isocalendar()

    def to_json(self):
        j = self.jsondict()
        return json.dumps(j)

    def jsondict(self):
        j = {
            "date": self.date.isoformat(),
            "distance": self.distance,
            "time": self.time,
        }
        return j


# Confuse the linter
try:
    GC
except:
    GC = None

data = GC.seasonMetrics()

activities = []
l = len(data["date"])
for i in range(l):
    if data["Sport"][i] == "Run":
        act = MyActivity(data["date"][i], data["Distance"][i], data["Time_Moving"][i])
        activities.append(act)


# Getting this week's data
now = datetime.date.today()
(year, week, _) = now.isocalendar()
thisweek = []
for act in activities:
    if act.year == year and act.week == week:
        thisweek.append(act)

thisweek = [act.jsondict() for act in thisweek]

# Getting per week
perweek = {}
for act in activities:
    if act.year not in perweek:
        perweek[act.year] = {}
    if act.week not in perweek[act.year]:
        perweek[act.year][act.week] = {"Distance": 0, "Time": 0}

    perweek[act.year][act.week]["Distance"] += act.distance
    perweek[act.year][act.week]["Time"] += act.time

EXPORT_PATH = "/home/ward/Downloads/goldencheetah.perweek.json"
with open(EXPORT_PATH, "w") as f:
    f.write(json.dumps(perweek, sort_keys=True, indent=4))
    print("Dumped per week in {}".format(EXPORT_PATH))
