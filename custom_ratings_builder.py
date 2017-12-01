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
RATING_RANGE_HIGH = 85
RATING_RANGE_LOW = 15
RESULTS_EMPHASIZED_RATING_CONSTANT = 7
RESULTS_EMPHASIZED_RATING_COEFFICIENT = 0.5

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

def location_adjustment(string):
    return location_coefficient(string) * HOME_FIELD_ADVANTAGE

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
    return numpy.sqrt(sum_sq_err / float(len(team.games) - 1))

def game_difficulty(game):
    return game.opponent.ratings['pure_points'] - location_adjustment(game.location)

def adjusted_rating(rating):
    return round(float(rating - RATING_RANGE_LOW) * 100 / (RATING_RANGE_HIGH - RATING_RANGE_LOW))

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
lin_results_rer = []
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
    rer_differential = 0
    location_adv = 0
    for game in team.games:
        if team.id != CONSTANT_ID:
            coefficients[team.id] += 1
        if ESTIMATE_LOCATION_COEFF:
            coefficients[-1] += location_coefficient(game.location)
        else:
            game_location_adv = location_coefficient(game.location) * HOME_FIELD_ADVANTAGE
            location_adv += game_location_adv
        if game.opponent.id != CONSTANT_ID:
            coefficients[game.opponent.id] -= 1
        if OVERTIME_ADJUSTMENT and game.overtime == "True":
            if game.result == "W":
                total_differential -= 0.5
                rer_differential -= RESULTS_EMPHASIZED_RATING_CONSTANT / 2.0
            elif game.result == "L":
                total_differential += 0.5
                rer_differential += RESULTS_EMPHASIZED_RATING_CONSTANT / 2.0
            else:
                raise "Unexpected result: %s" % result
        else:
            raw_differential = game.own_score - game.opp_score
            total_differential += raw_differential
            rer_differential += raw_differential * 0.5
            if game.result == "W":
                rer_differential += 7
            elif game.result == "L":
                rer_differential -= 7
            else:
                raise "Unexpected result: %s" % result
    # Add to an array of arrays
    lin_coeffs.append(coefficients)
    # Append differential to results
    lin_results.append(total_differential - location_adv)
    lin_results_rer.append(rer_differential - location_adv * 0.5)

a = numpy.array(lin_coeffs)
b = numpy.array(lin_results)
b_rer = numpy.array(lin_results_rer)
estimated_coefficients = numpy.linalg.solve(a, b)
estimated_coeff_rer = numpy.linalg.solve(a, b_rer)



lin_coeffs_offdef = []
lin_results_offdef = []
for name, team in teams.items():
    off_id = team.id * 2
    def_id = None
    if team.id != CONSTANT_ID:
        def_id = team.id * 2 + 1
    # Build linear phrase & sum differential
    off_coefficients = [0] * (NUM_TEAMS * 2 - 1)
    def_coefficients = [0] * (NUM_TEAMS * 2 - 1)
    total_points = 0
    total_points_allowed = 0
    location_adv = 0
    for game in team.games:
        off_coefficients[off_id] += 1
        if def_id is not None:
            def_coefficients[def_id] += 1
            def_coefficients[game.opponent.id * 2] += 1
        if ESTIMATE_LOCATION_COEFF:
            off_coefficients[-1] += location_coefficient(game.location)
            def_coefficients[-1] += location_coefficient(game.location)
        else:
            location_adv += location_coefficient(game.location) * HOME_FIELD_ADVANTAGE / 2.0
        if game.opponent.id != CONSTANT_ID:
            off_coefficients[game.opponent.id * 2 + 1] += 1
        total_points += game.own_score
        total_points_allowed += game.opp_score
    # Add to an array of arrays
    lin_coeffs_offdef.append(off_coefficients)
    if def_id is not None:
        lin_coeffs_offdef.append(def_coefficients)
    # Append differential to results
    lin_results_offdef.append(total_points - location_adv)
    if def_id is not None:
        lin_results_offdef.append(total_points_allowed - location_adv)

a_od = numpy.array(lin_coeffs_offdef)
b_od = numpy.array(lin_results_offdef)
estimated_coefficients_offdef = numpy.linalg.solve(a_od, b_od)

average = sum(estimated_coefficients) / float(NUM_TEAMS)

total_off = 0
total_def = 0
for idx, rating in enumerate(estimated_coefficients_offdef):
    if idx % 2 == 0:
        total_off += rating
    else:
        total_def += rating
average_off = total_off / float(NUM_TEAMS)
average_def = total_def / float(NUM_TEAMS)
for i in range(NUM_TEAMS):
    name = id_to_team[i]
    team = teams[name]
    offense = estimated_coefficients_offdef[i * 2]
    if i == CONSTANT_ID:
        estimate = 0
        defense = 0
    else:
        estimate = estimated_coefficients[i]
        defense = estimated_coefficients_offdef[i * 2 + 1]
    team.ratings['pure_points'] = estimate + 50 - average
    team.ratings['pp_offense'] = offense + average_def
    team.ratings['pp_defense'] = defense + average_off

for team in list(teams.values()):
    team.ratings['pure_points_std'] = pure_points_standard_deviation(team)

sorted_teams = sorted(list(teams.values()), key=lambda team: team.ratings['pure_points'], reverse=True)
output_file = '%s/output/custom-power-week%s.csv' % (root_path, CURRENT_WEEK)
with open(output_file, 'w+') as f:
    for idx, team in enumerate(sorted_teams):
        f.write('%(rank)s,%(name)s,%(rating)s,%(offense)s,%(defense)s,%(std)s\n' % {
            'rank': idx + 1,
            'name': team.name,
            'rating': round(team.ratings['pure_points'], 2),
            'offense': round(team.ratings['pp_offense'], 2),
            'defense': round(team.ratings['pp_defense'], 2),
            'std': round(team.ratings['pure_points_std'], 2)
        })

for idx, team in enumerate(sorted(list(teams.values()), key=lambda team: team.ratings['pure_points'], reverse=True)):
    print("%s %s %s %s %s" % (
        idx + 1,
        team.name,
        round(team.ratings['pure_points'], 2),
        round(team.ratings['pp_offense'], 2),
        round(team.ratings['pp_defense'], 2)))

# for idx, team in enumerate(sorted(list(teams.values()), key=lambda team: team.ratings['pp_offense'], reverse=True)):
#     print("%s %s %s" % (
#         idx + 1,
#         team.name,
#         round(team.ratings['pp_offense'], 2),
#         ))
#
# for idx, team in enumerate(sorted(list(teams.values()), key=lambda team: team.ratings['pp_defense'], reverse=False)):
#     print("%s %s %s" % (
#         idx + 1,
#         team.name,
#         round(team.ratings['pp_defense'], 2),
#         ))


# WRITE SCHEDULE RATING FILES
for team in list(teams.values()):
    filename_format_name = build_filename_format(team.name)
    write_file = '%s/output/reddit_schedules/%s.txt' % (root_path, filename_format_name)
    with open(write_file, 'w+') as f:
        label_string = team.name + "(%s)" % team.record
        columns = ["Opponent", "Rec", "Loc", "Difficulty", "Result", "Score", "Game Rating"]
        header = " | ".join(columns) + "\n"
        barrier = "|".join(map(lambda _: "---", columns)) + "\n"
        f.write(header)
        f.write(barrier)
        for game in sorted(list(team.games), key=lambda game: game_difficulty(game), reverse=True):
            score_string = "%s-%s" % (game.own_score, game.opp_score)
            if game.overtime:
                if game.num_overtimes > 1:
                    score_string += " %sOT" % game.num_overtimes
                else:
                    score_string += " OT"
            text = "%(opponent)s | %(record)s | %(location)s | %(difficulty)s | %(result)s | %(score)s | %(game_rating)s |\n" % {
                'opponent': game.opponent.name,
                'location': game.location,
                'record': game.opponent.record,
                'difficulty': adjusted_rating(game_difficulty(game)),
                'result': game.result,
                'score': score_string,
                'game_rating': adjusted_rating(game_difficulty(game) + game.own_score - game.opp_score)
            }
            f.write(text)

# ADD RESULTS EMPHASIZED RATING
