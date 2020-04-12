import datetime
import tempfile
import pathlib

### Configuration
GOAL = 4500

### Calculations
data = GC.seasonMetrics()
# Keep only runs. Don't use GC filters cause that makes it HELLA slow
distances = [x for i, x in enumerate(data['Distance']) if data['Sport'][i] == 'Run']

today_distance = sum(distances)
today = datetime.date.today()
first_day = datetime.date(year = today.year, month = 1, day = 1)
last_day = datetime.date(year = today.year, month = 12, day = 31)
days_passed = (today - first_day).days + 1
days_to_go = (last_day - today).days
total_days = (last_day - first_day).days + 1

km_per_day = today_distance / days_passed
last_distance_estimate = km_per_day * total_days

today_goal = GOAL / total_days * days_passed

### Create html file
temp_file = tempfile.NamedTemporaryFile(mode="w+t", prefix="GC_", suffix=".html", delete=False)
temp_file.write('<html><body>')
temp_file.write('<p>')
temp_file.write("You have run {:.1f} km so far.".format(today_distance))
temp_file.write('</p>')
temp_file.write('<p>')
temp_file.write("That is an average of {:.1f} km per day.".format(km_per_day))
temp_file.write('</p>')

temp_file.write('<p>')
if today_goal < today_distance:
    temp_file.write("You are {:.1f} km ahead of your {:d} km goal.".format(today_distance - today_goal, GOAL))
else:
    temp_file.write("You are {:.1f} km BEHIND on your {:d} km goal.".format(today_goal - today_distance, GOAL))
temp_file.write('</p>')

temp_file.write('<p>')
temp_file.write("At this rate, you will end up at {:.1f} km.".format(last_distance_estimate))
temp_file.write('</p>')
temp_file.write('</body></html>')
temp_file.close()

### Output
print('DEBUG: File saved at', pathlib.Path(temp_file.name).as_uri())
GC.webpage(pathlib.Path(temp_file.name).as_uri())
