import sys
sys.path.append('./processing')
from teams import build_teams
from readers import *
sys.path = sys.path[:-12]
sys.path.append('./constants')
from name_translations import *

power_source = './scraper/composite-cf.csv'
performance_source = './scraper/performance-ratings.csv'
name_source = './constants/names.txt'
last_week_source = './last_week.txt'
conferences_source = './constants/conferences.txt'
records_source = './scraper/standings.csv'

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

    reddit = team.get_reddit_rating()
    string_reddit = str(reddit)
    while len(string_reddit) < 4:
        string_reddit = " " + string_reddit

    return " ".join([string_power, string_performance, string_combined, string_reddit, name])

def build_reddit_string(rank, team, conference_flairs):
    result = ""
    result += str(rank) + " | "
    result += str(team['team'].last_week) + " | "
    result += get_flair_string(team['name'])
    result += " | "
    result += team['team'].record
    result += " | "
    result += conference_flairs[team['team'].conference]
    result += " | "
    result += str(team['team'].get_reddit_rating())
    result += " |\n"
    return result

def get_flair_string(name):
    result = "[" + name + "](#f/"
    combo_string = "".join(name.split(" ")).lower()
    result += combo_string + ") "
    result += name
    return result

def set_last_week(last_week_data, teams):
    result = {}
    for line in last_week_data:
        rank, name = line.strip().split(',')
        result[name] = rank
        team = teams[name]
        team.last_week = rank
    return result

def read_lines(source):
    source_file = open(source, "r")
    source_data = source_file.readlines()
    source_file.close()
    return source_data

def build_conference_flairs(data):
    result = {}
    for line in data:
        abrev, flair = line.strip().split(',')
        result[abrev] = flair
    return result

teams = build_teams(name_source)
print (teams)

power_data = read_lines(power_source)
performance_data = read_lines(performance_source)
last_week = read_lines(last_week_source)
conference_data = read_lines(conferences_source)
record_data = read_lines(records_source)

conference_flairs = build_conference_flairs(conference_data)
dropped_out = set_last_week(last_week, teams)

for data_line in power_data:
    data = read_composite_line(data_line)
    team = process_massey_name(data['name'])
    if team in MASSEY_NAMES[0]:
        team = MASSEY_NAMES[0][team]
    teams[team].set_power_mean(data['mean'])

for data_line in performance_data:
    data = read_performance_line(data_line)
    raw_name = data['name']
    if raw_name in PERFORMANCE_NAMES:
        name = PERFORMANCE_NAMES[raw_name]
    else:
        name = find_match(raw_name, teams)
    teams[name].set_performance_metrics(
        data['strength_of_record'],
        data['game_control']
    )

for data_line in record_data:
    raw_name, record = data_line.strip().split(",")
    name = raw_name
    if raw_name in NCAA_NAMES:
        name = NCAA_NAMES[raw_name]
    teams[name].record = record

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

reddit_filename = 'reddit.txt'
with open(reddit_filename, 'w+') as f:
    f.write("Rnk | LW | Team | W-L | Conf | Rating \n")
    f.write("---|---|---|---|---|---| \n")
    rank = 1
    for team in rankings[:25]:
        text = build_reddit_string(rank, team, conference_flairs)
        f.write(text)
        if team['name'] in dropped_out:
            del dropped_out[team['name']]
        rank += 1
    f.write("\n")
    f.write("**Next:**\n")
    f.write("\n")
    for team in rankings[25:30]:
        text = get_flair_string(team['name'])
        text += " ("
        text += str(team['team'].get_reddit_rating())
        text += ")\n"
        f.write(text)
        f.write("\n")
    f.write("**Dropped Out:**\n")
    f.write("\n")
    print(dropped_out)
    for key, val in dropped_out.items():
        team_name = key
        flair = get_flair_string(team_name)
        f.write("(" + val + ") " + flair)
