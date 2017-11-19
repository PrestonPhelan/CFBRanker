import os, sys
from processing.team import Team
from processing.readers import *
from processing.builders import *
from constants.name_translations import *
from settings import CURRENT_WEEK

root_path = os.path.dirname(os.path.abspath(__file__))
sources = {}
sources['power'] = '%s/output/power-ratings-week%s.csv' % (root_path, CURRENT_WEEK)
sources['performance'] = '%s/output/performance-ratings-week%s.csv' % (root_path, CURRENT_WEEK)
sources['names'] = '%s/constants/names.txt' % root_path
sources['last_week'] = '%s/output/results-week%s.csv' % (root_path, CURRENT_WEEK - 1)
sources['conferences'] = '%s/constants/conferences.txt' % root_path
sources['records'] = '%s/output/standings-week%s.csv' % (root_path, CURRENT_WEEK)

data = {}
for key, sourcefile in sources.items():
    with open(sourcefile) as f:
        data[key] = list(f)

teams = Team.build_teams_from_file(sources['names'])
conference_flairs = build_conference_flairs(data['conferences'])
dropped_out = Team.set_last_week(data['last_week'], teams)

for data_line in data['power']:
    raw_data = read_power_line(data_line)
    team = process_power_name(raw_data['name'])
    if team in POWER_NAMES:
        team = POWER_NAMES[team]
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

result_filename = '%s/output/results-week%s.csv' % (root_path, CURRENT_WEEK)
with open(result_filename, 'w+') as f:
    for idx, team in enumerate(rankings):
        result_string = build_result_string(team, idx)
        f.write("%s\n" % result_string)

reddit_filename = '%s/output/reddit-week%s.txt' % (root_path, CURRENT_WEEK)
with open(reddit_filename, 'w+') as f:
    f.write(build_reddit_header())
    f.write(build_reddit_barrier())
    for idx, team in enumerate(rankings[:25]):
        text = build_reddit_string(idx, team, conference_flairs, REDDIT_NAMES)
        f.write(text)
        if team.name in dropped_out:
            del dropped_out[team.name]
    f.write("\n**Next:**\n\n")
    for team in rankings[25:30]:
        flair_string = team.get_flair_string(REDDIT_NAMES)
        rating = team.get_reddit_rating()
        text = "%s (%s)\n\n" % (flair_string, rating)
        f.write(text)
    f.write("**Dropped Out:**\n\n")
    for team_name, lw_rank in dropped_out.items():
        flair = teams[team_name].get_flair_string(REDDIT_NAMES)
        text = "(%s) %s \n\n" % (lw_rank, flair)
        f.write(text)

print("DONE")
