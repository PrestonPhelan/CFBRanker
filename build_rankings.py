import os, sys
from processing.team import Team
from processing.readers import *
from processing.builders import *
from constants.name_translations import *
from settings import CURRENT_WEEK

# TODO Fix Input Files For Generated CSVs, Automate LastWeek
root_path = os.path.dirname(os.path.abspath(__file__))
sources = {}
sources['power'] = '%s/scraper/composite-cf.csv' % root_path
sources['performance'] = '%s/scraper/performance-ratings.csv' % root_path
sources['names'] = '%s/constants/names.txt' % root_path
sources['last_week'] = '%s/last_week.txt' % root_path
sources['conferences'] = '%s/constants/conferences.txt' % root_path
sources['records'] = '%s/scraper/standings.csv' % root_path

data = {}
for key, sourcefile in sources.items():
    with open(sourcefile) as f:
        data[key] = list(f)

teams = Team.build_teams_from_file(sources['names'])
conference_flairs = build_conference_flairs(data['conferences'])
dropped_out = Team.set_last_week(data['last_week'], teams)

def build_result_string(team):
    name = team.name
    power = team.power_mean
    string_power = str(power)
    # while len(string_power) < 6:
    #     string_power = " " + string_power

    performance = round(team.calculate_performance_rating(), 2)
    string_performance = str(performance)
    # while len(string_performance) < 6:
    #     string_performance = " " + string_performance

    combined = round(team.get_combined_rating(), 2)
    string_combined = str(combined)
    # while len(string_combined) < 6:
    #     string_combined = " " + string_combined

    reddit = team.get_reddit_rating()
    string_reddit = str(reddit)
    # while len(string_reddit) < 4:
    #     string_reddit = " " + string_reddit

    return ",".join([string_power, string_performance, string_combined, string_reddit, name])

def build_reddit_string(rank, team, conference_flairs):
    result = ""
    result += str(rank) + " | "
    result += str(team.last_week) + " | "
    result += team.get_flair_string(REDDIT_NAMES)
    result += " | "
    result += team.record
    result += " | "
    result += conference_flairs[team.conference]
    result += " | "
    result += str(team.get_reddit_rating())
    result += " |\n"
    return result

for data_line in data['power']:
    raw_data = read_composite_line(data_line)
    team = process_power_name(raw_data['name'])
    if team in POWER_NAMES[0]:
        team = POWER_NAMES[0][team]
    teams[team].set_power_mean(raw_data['mean'])

for data_line in data['performance']:
    raw_data = read_performance_line(data_line)
    raw_name = raw_data['name']
    if raw_name in PERFORMANCE_NAMES:
        name = PERFORMANCE_NAMES[raw_name]
    else:
        name = find_match(raw_name, teams)
    teams[name].set_performance_metrics(
        raw_data['strength_of_record'],
        raw_data['game_control']
    )

for data_line in data['records']:
    raw_name, record = data_line.strip().split(",")
    name = raw_name
    if raw_name in NCAA_NAMES:
        name = NCAA_NAMES[raw_name]
    teams[name].record = record


rankings = sorted(list(teams.values()), key=lambda team: team.get_combined_rating())

result_filename = '%s/output/results-week%s.csv' % (root_path, CURRENT_WEEK - 1)
with open(result_filename, 'w+') as f:
    rank = 1
    for team in rankings:
        result_string = build_result_string(team)
        string_rank = str(rank)
        # while len(string_rank) < 3:
        #     string_rank = " " + string_rank
        f.write(string_rank + "," + result_string + "\n")
        rank += 1

reddit_filename = 'reddit.txt'
with open(reddit_filename, 'w+') as f:
    f.write("Rnk | LW | Team | W-L | Conf | Rating \n")
    f.write("---|---|---|---|---|---| \n")
    rank = 1
    for team in rankings[:25]:
        text = build_reddit_string(rank, team, conference_flairs)
        f.write(text)
        if team.name in dropped_out:
            del dropped_out[team.name]
        rank += 1
    f.write("\n")
    f.write("**Next:**\n")
    f.write("\n")
    for team in rankings[25:30]:
        text = team.get_flair_string(REDDIT_NAMES)
        text += " ("
        text += str(team.get_reddit_rating())
        text += ")\n"
        f.write(text)
        f.write("\n")
    f.write("**Dropped Out:**\n")
    f.write("\n")
    print(dropped_out)
    for key, val in dropped_out.items():
        team_name = key
        flair = teams[team_name].get_flair_string(REDDIT_NAMES)
        f.write("(" + val + ") " + flair)
