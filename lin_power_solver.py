import numpy
import os
root_path = os.path.dirname(os.path.abspath(__file__))

from processing.builders import build_filename_format
from settings import CURRENT_WEEK

name_source = '%s/constants/names.txt' % root_path

names = []
idx_lookup = {}
with open(name_source, 'r') as f:
    idx = 0
    for line in f:
        raw_name, _ = line.strip().split(",")
        if idx < 129:
            names.append(raw_name)
            idx_lookup[raw_name] = idx
            idx += 1
        else:
            print ("Skipped %s" % line)
            constant_team = raw_name


raw_a = []
raw_b = []
raw_offdef_a = []
raw_offdef_b = []
def get_coefficients_from_schedule(team):
    # [H-A] * HFA + N * self - (1 * opp) for each = differential
    filename_format_name = build_filename_format(team)
    schedule_source = '%s/output/schedule_ratings/%s.csv' % (root_path, filename_format_name)
    coefficients = [0] * 129
    total_differential = 0
    location_adv = 0
    own_idx = idx_lookup[team]
    with open(schedule_source) as f:
        for line in f:
            coefficients[own_idx] += 1
            columns = line.strip().split(',')
            if columns[0] == "H":
                location_adv += 2.8
            elif columns[0] == "A":
                location_adv -= 2.8
            opponent = columns[1]
            if opponent in idx_lookup:
                coefficients[idx_lookup[opponent]] -= 1
            if columns[6] == "True":
                if int(columns[5]) > 0:
                    total_differential += 0.5
                else:
                    total_differential -= 0.5
            else:
                total_differential += int(columns[5])
    raw_a.append(coefficients)
    raw_b.append(total_differential - location_adv)

for name in names:
    get_coefficients_from_schedule(name)


a = numpy.array(raw_a)
b = numpy.array(raw_b)
x = numpy.linalg.solve(a, b)

power_ratings = []
for idx, name in enumerate(names):
    power_ratings.append({'name': name, 'rating': x[idx] + 30})
power_ratings.append({'name': constant_team, 'rating': 30})

rnk = 1
output_file = '%s/output/custom-power-week%s.csv' % (root_path, CURRENT_WEEK)
with open(output_file, 'w+') as f:
    for team in sorted(power_ratings, key=lambda team: team['rating'], reverse=True):
        f.write('%s,%s,%s\n' % (rnk, team['name'], team['rating']))
        print('%s %s %s' % (rnk, team['name'], team['rating']))
        rnk += 1
