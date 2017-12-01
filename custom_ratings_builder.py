import numpy
import os
root_path = os.path.dirname(os.path.abspath(__file__))

from constants.name_translations import translate_ncaa_name, translate_schedule_name
from processing.builders import build_filename_format
from processing.game import Game
from processing.team import Team
from settings import CURRENT_WEEK

ESTIMATE_LOCATION_COEFF = False
OVERTIME_ADJUSTMENT = True
NUM_TEAMS = 130
CONSTANT_ID = NUM_TEAMS - 1
HOME_FIELD_ADVANTAGE = 3.0

if ESTIMATE_LOCATION_COEFF:
    LIN_EQ_SIZE = NUM_TEAMS
else:
    LIN_EQ_SIZE = NUM_TEAMS - 1

def translate_location(string):
    translations = {
        'N': 'N',
        'vs': 'H',
        '@': 'A'
    }
    return translations[string]

def location_coefficient(string):
    coefficients = {
        'N': 0,
        'A': -1,
        'H': 1
    }
    return coefficients[string]

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

def predict_diff(team, game):
    own_rating = team.ratings['pure_points']
    opp_rating = game.opponent.ratings['pure_points']
    location_adjustment = location_coefficient(game.location) * HOME_FIELD_ADVANTAGE
    return own_rating - opp_rating + location_adjustment

def pure_points_standard_deviation(team):
    sum_sq_err = 0
    for game in team.games:
        predicted_diff = predict_diff(team, game)
        if game.overtime and OVERTIME_ADJUSTMENT:
            if game.own_score > game.opp_score:
                actual_diff = 0.5
            else:
                actual_diff = -0.5
        else:
            actual_diff = game.own_score - game.opp_score
        residual = actual_diff - predicted_diff
        sum_sq_err += residual * residual
        if team.name == "Eastern Michigan":
            print(game)
            print(predicted_diff)
            print(residual)
            print(sum_sq_err)
    return numpy.sqrt(sum_sq_err / float(len(team.games) - 1))

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
                'opponent': teams[opponent],
                'result': result,
                'own_score': int(own_score),
                'opp_score': int(opp_score),
                'overtime': result_details['overtime'],
                'num_overtimes': result_details['num_overtimes']
            }))

## LINEAR EQUATION SYSTEM SOLVE
id_to_team = [None] * NUM_TEAMS
lin_coeffs = []
lin_results = []
constant_team = None
# For each team
for name, team in teams.items():
    id_to_team[team.id] = name
    if team.id == CONSTANT_ID:
        constant_team = team
        continue
    # Build linear phrase & sum differential
    coefficients = [0] * LIN_EQ_SIZE
    total_differential = 0
    location_adv = 0
    for game in team.games:
        if team.id != CONSTANT_ID:
            coefficients[team.id] += 1
        if ESTIMATE_LOCATION_COEFF:
            coefficients[-1] += location_coefficient(game.location)
        else:
            location_adv += location_coefficient(game.location) * HOME_FIELD_ADVANTAGE
        if game.opponent.id != CONSTANT_ID:
            coefficients[game.opponent.id] -= 1
        if OVERTIME_ADJUSTMENT and game.overtime == "True":
            if game.own_score < game.opp_score:
                total_differential -= 0.5
            else:
                total_differential += 0.5
        else:
            total_differential += game.own_score - game.opp_score
    # Add to an array of arrays
    lin_coeffs.append(coefficients)
    # Append differential to results
    lin_results.append(total_differential - location_adv)

a = numpy.array(lin_coeffs)
b = numpy.array(lin_results)
estimated_coefficients = numpy.linalg.solve(a, b)

average = sum(estimated_coefficients) / float(NUM_TEAMS)
for i in range(NUM_TEAMS):
    name = id_to_team[i]
    if i == CONSTANT_ID:
        estimate = 0
    else:
        estimate = estimated_coefficients[i]
    teams[name].ratings['pure_points'] = estimate + 50 - average


for team in list(teams.values()):
    team.ratings['pure_points_std'] = pure_points_standard_deviation(team)

for team in sorted(list(teams.values()), key=lambda team: team.ratings['pure_points'], reverse=True):
    print("%s %s" % (team.name, team.ratings['pure_points']))
