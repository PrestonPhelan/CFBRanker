import os
root_path = os.path.dirname(os.path.abspath(__file__))

from constants.name_translations import translate_ncaa_name, translate_schedule_name
from processing.builders import build_filename_format
from processing.game import Game
from processing.team import Team
from settings import CURRENT_WEEK

def translate_location(string):
    translations = {
        'N': 'N',
        'vs': 'H',
        '@': 'A'
    }
    return translations[string]

def read_score(score_string):
    win_score, lose_score = score_string.split('-')
    overtime = False
    num_overtimes = None
    if len(lose_score.split(' ')) > 1:
        lose_score, ot_string = lose_score.split(' ')
        overtime = True
        if len(ot_string) > 2:
            num_overtimes = int(ot_string[0])
        else:
            num_overtimes = 1
    return {
        'win_score': win_score,
        'lose_score': lose_score,
        'overtime': overtime,
        'num_overtimes': num_overtimes
    }

def assign_scores(result, result_details):
    if result == 'W':
        return [result_details['win_score'], result_details['lose_score']]
    elif result == 'L':
        return [result_details['lose_score'], result_details['win_score']]
    else:
        raise "Unexpected result %s" % result

### GET INPUT DATA ###
# Create team objects
team_list_source = "%s/constants/names.txt" % root_path
teams = Team.build_teams_from_file(team_list_source)

records_source = "%s/output/standings-week%s.csv" % (root_path, CURRENT_WEEK)
with open(records_source) as f:
    for line in f:
        name, record = line.strip().split(",")
        name = translate_ncaa_name(name)
        teams[name].record = record

# Create game objects
schedule_root = '%s/output/schedules/' % root_path
idx = 0
for name, team in teams.items():
    team.id = idx
    idx += 1
    filename_format_name = build_filename_format(name)
    schedule_source = '%s%s.csv' % (schedule_root, filename_format_name)
    with open(schedule_source) as f:
        for line in f:
            # Read schedule data
            columns = line.strip().split(",")
            if columns[2] == 'False':
                continue
            location, opponent, _, result, score = columns

            opponent = translate_schedule_name(opponent)
            if opponent not in teams:
                print('Skipped %s' % opponent)
                continue

            location = translate_location(location)
            result_details = read_score(score)
            own_score, opp_score = assign_scores(result, result_details)
            # Create a Game Object
            # Add to team's set of games
            team.games.add(Game({
                'location': location,
                'opponent': opponent,
                'result': result,
                'own_score': int(own_score),
                'opp_score': int(opp_score),
                'overtime': result_details['overtime'],
                'num_overtimes': result_details['num_overtimes']
            }))
