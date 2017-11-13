import sys
sys.path.append('./processing')
from teams import build_teams
from readers import *
sys.path = sys.path[:-12]
sys.path.append('./constants')
from name_translations import *

print(type(MasseyNames))
print(MasseyNames)

power_source = './scraper/composite-cf.csv'
performance_source = './scraper/espn-ratings.csv'
name_source = './constants/names.txt'

def find_match(name, dictionary):
    if name == '':
        raise "Didn't find name"
    search_name = (' ').join(name.split(' ')[:-1])
    if search_name in dictionary:
        return search_name
    else:
        return find_match(search_name, dictionary)

def build_result_string(team):
    name = team.name
    power = team.power_mean
    string_power = str(power)
    while len(string_power) < 6:
        string_power = " " + string_power

    performance = round(team.calculate_performance_rating(), 2)
    string_performance = str(performance)
    while len(string_performance) < 6:
        string_performance = " " + string_performance

    combined = round(team.get_combined_rating(), 2)
    string_combined = str(combined)
    while len(string_combined) < 6:
        string_combined = " " + string_combined

    return " ".join([string_power, string_performance, string_combined, name])

teams = build_teams(name_source)

power_file = open(power_source, "r")
power_data = power_file.readlines()
power_file.close()

performance_file = open(performance_source, "r")
performance_data = performance_file.readlines()
performance_file.close()

for data_line in power_data:
    data = read_composite_line(data_line)
    team = process_massey_name(data['name'])
    if team in MasseyNames[0]:
        team = MasseyNames[0][team]
    teams[team].set_power_mean(data['mean'])

for data_line in performance_data:
    data = read_performance_line(data_line)
    raw_name = data['name']
    if raw_name in ESPNNames:
        name = ESPNNames[raw_name]
    else:
        name = find_match(raw_name, teams)
    teams[name].set_performance_metrics(
        data['strength_of_record'],
        data['game_control']
    )

results = []

for key, val in teams.items():
    results.append({'team': val, 'name': key, 'rating': val.get_combined_rating()})

rankings = sorted(results, key=lambda team: team['rating'])

result_filename = 'results.txt'
with open(result_filename, 'w+') as f:
    rank = 1
    for team in rankings:
        result_string = build_result_string(team['team'])
        string_rank = str(rank)
        while len(string_rank) < 3:
            string_rank = " " + string_rank
        f.write(string_rank + " " + result_string + "\n")
        rank += 1
        print(team['team'])
