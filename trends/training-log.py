# Can I easily copy Strava's training log idea?
import math

def radius_from_distance(distance):
    """No logic to this formula, just playing around with numbers."""
    base_size = 15
    if distance < 5:
        return base_size
    else:
        return base_size + max(0, math.log((distance - 4) / 2, 1.1))

def write_day(f, activities, idx):
    # Only consider first activity for now
    # TODO Maybe a pie chart? or a cluster like strava
    workout, distance = activities[0]
    day = (
            '<g class="day workout-{}">'
            '<circle cx="{}" cy="80" r="{}" />'
            '</g>'
            )
    r = radius_from_distance(distance)
    print('debug', distance, 'km =', r, 'pixel radius')
    f.write(day.format(workout, idx * 100 + 50, r))

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
            '--ga: #56b4e9;'
            '--interval: #e69f00;'
            '--race: #ff00ff;'
            '--repetition: #f0e442;'
            '--threshold: #009e73;'
            '}'
            'circle {'
            'stroke: gray;'
            '}'
            'g.workout-endurance circle {'
            'fill: var(--endurance);'
            '}'
            'g.workout-ga circle {'
            'fill: var(--ga);'
            '}'
            'g.workout-interval circle {'
            'fill: var(--interval);'
            '}'
            'g.workout-race circle {'
            'fill: var(--race);'
            '}'
            'g.workout-recovery circle {'
            'fill: var(--ga);'
            '}'
            'g.workout-repetition circle {'
            'fill: var(--repetition);'
            '}'
            'g.workout-threshold circle {'
            'fill: var(--threshold);'
            '}'
            '</style>'
            )
    f.write(css)

test_activities = [
        [
            [('recovery', 10)],
            [('threshold', 16.5)],
            [('ga', 14)],
            [('recovery', 10)],
            [('repetition', 17)],
            [('recovery', 10)],
            [('endurance', 22.5)]],
        [[('recovery', x)] for x in range(1, 8)],
        [[('recovery', x)] for x in range(8, 15)],
        [[('recovery', x)] for x in range(15, 22)],
        [[('recovery', x)] for x in range(22, 29)],
        [[('recovery', x)] for x in range(29, 36)],
        [
            [('recovery', 10)],
            [('threshold', 16.5)],
            [('ga', 14)],
            [('recovery', 10)],
            [('repetition', 17)],
            [('recovery', 10)],
            [('race', 42.195)]
            ]
        ]

if __name__ == '__main__':
    with open('./output.html', 'w') as f:
        write_training_log(f, test_activities)
