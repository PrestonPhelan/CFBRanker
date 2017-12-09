import numpy
import os
root_path = os.path.dirname(os.path.abspath(__file__))

from scipy.stats import norm

from constants.name_translations import translate_schedule_name
from processing.builders import build_filename_format
from models.game import Game
from models.team import Team

ESTIMATE_LOCATION_COEFF = False
OVERTIME_ADJUSTMENT = True
NUM_TEAMS = 351
CONSTANT_ID = NUM_TEAMS - 1

HOME_FIELD_ADVANTAGE = 3.3
RATING_RANGE_HIGH = 85
RATING_RANGE_LOW = 15

GAME_STD = 11.0

if ESTIMATE_LOCATION_COEFF:
    LIN_EQ_SIZE = NUM_TEAMS
else:
    LIN_EQ_SIZE = NUM_TEAMS - 1

combos = {}

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

def pure_points_standard_deviation(team, total_sse, total_games):
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
        total_sse += residual * residual
        total_games += 1
    return [numpy.sqrt(sum_sq_err / float(len(team.games) - 1)), total_sse, total_games]

def game_difficulty(game):
    return game.opponent.ratings['pure_points'] - location_adjustment(game.location)

def adjusted_rating(rating):
    return round(float(rating - RATING_RANGE_LOW) * 100 / (RATING_RANGE_HIGH - RATING_RANGE_LOW))

def choose_iter(elements, length):
    for i, _ in enumerate(elements):
        if length == 1:
            yield (elements[i],)
        else:
            for next in choose_iter(elements[i+1:len(elements)], length-1):
                yield (elements[i],) + next

def choose(pop_size, num_elements_to_choose):
    nums = range(pop_size)
    return list(choose_iter(nums, num_elements_to_choose))

def calculate_game_probability(own_rating, game_rating):
    z_score = (own_rating - game_rating) / GAME_STD
    return norm.cdf(z_score)

def calc_product(num_list, loss_list = {}):
    product = 1
    for idx, num in enumerate(num_list):
        if idx in loss_list:
            product = product * (1 - num)
        else:
            product = product * num
    return product

def get_performance_probability(team, rating):
    win_probs, losses = calculate_probabilities(team, rating)
    sum_of_probs = 0
    current_loss_counter = 0
    while current_loss_counter < losses:
        sum_of_probs += calculate_schedule_probability(win_probs, current_loss_counter)
        current_loss_counter += 1
    sum_of_probs += 0.5 * calculate_schedule_probability(win_probs, current_loss_counter)
    return sum_of_probs

def calculate_probabilities(team, rating):
    win_probs = []
    losses = 0
    for game in team.games:
        p_win = calculate_game_probability(rating, game.difficulty(location_adjustment))
        win_probs.append(p_win)
        if game.result == "L":
            losses += 1
    return [win_probs, losses]

def calculate_schedule_probability(win_probs, losses):
    if losses == 0:
        return calc_product(win_probs)
    num_games = len(win_probs)
    combinations = None
    lookup_string = '%s-%s' % (num_games, losses)
    if lookup_string in combos:
        combinations = combos[lookup_string]
    else:
        combinations = choose(num_games, losses)
        combos[lookup_string] = combinations
    total_prob = 0
    for loss_list in combinations:
        total_prob += calc_product(win_probs, loss_list)
    return total_prob

def calculate_actual_results_probability(team, rating):
    p = 1
    for game in team.games:
        p_win = calculate_game_probability(rating, game.difficulty(location_adjustment))
        if game.result == "W":
            p = p * p_win
        elif game.result == "L":
            p = p * (1.0 - p_win)
        else:
            raise "Unexpected result %s" % game.result
    return p


bb_team_list_source = "%s/constants/bb_names.txt" % root_path
teams = Team.build_teams_from_file(bb_team_list_source)

team_list_source = "%s/constants/names.txt" % root_path
fbs_teams = Team.build_teams_from_file(team_list_source)
for name, team in fbs_teams.items():
    if name not in teams:
        teams[name] = team

skipped_teams = set()

schedule_root = '%s/output/basketball/schedules/' % root_path
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
            location, opponent, result, score = columns

            if result not in ["W", "L"]:
                continue

            opponent = translate_schedule_name(opponent)
            if opponent not in teams:
                skipped_teams.add(opponent)
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

total_sse = 0
total_games = 0
for team in list(teams.values()):
    team.ratings['pure_points_std'], total_sse, total_games = pure_points_standard_deviation(team, total_sse, total_games)

total_sse = float(total_sse) / 2.0
total_games = float(total_games) / 2.0
OVERALL_STD = numpy.sqrt(total_sse / (total_games - (NUM_TEAMS - 1)))

sorted_teams = sorted(teams.values(), key=lambda team: team.ratings['pure_points'], reverse=True)
for idx, team in enumerate(sorted_teams):
    print ("%(rank)s %(name)s %(rating)s %(offense)s %(defense)s %(std)s" % {
        'rank': idx + 1,
        'name': team.name,
        'rating': round(team.ratings['pure_points'], 2),
        'offense': round(team.ratings['pp_offense'], 2),
        'defense': round(team.ratings['pp_defense'], 2),
        'std': round(team.ratings['pure_points_std'], 2)
    })

# WRITE SCHEDULE RATING FILES
for team in list(teams.values()):
    filename_format_name = build_filename_format(team.name)
    write_file = '%s/output/basketball/reddit_schedules/%s.txt' % (root_path, filename_format_name)
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

ratings = list(map(lambda team: team.ratings['pure_points'], list(teams.values())))
ratings_std = numpy.std(ratings, ddof=1)

# GENERATE WEIGHTED AVERAGE
rating_probabilities = {}
for i in range(101):
    rating_probabilities[str(i)] = norm.pdf(i, 50, ratings_std)

for team in list(teams.values()):
    max_p_rating = 0
    max_p = 0
    total_p = 0
    total_rat = 0
    for i in range(101):
        p_rating = rating_probabilities[str(i)]
        p_result = calculate_actual_results_probability(team, i)
        p_of_i = p_rating * p_result
        total_p += p_of_i
        total_rat += p_of_i * i
        if p_of_i > max_p:
            max_p = p_of_i
            max_p_rating = i
    team.ratings['sor_wa'] = total_rat / total_p
    team.ratings['sor_mle'] = max_p_rating

est_best_rating = norm.ppf(1 - (1.0 / (NUM_TEAMS * 2)), 50, ratings_std)

for team in list(teams.values()):
    print("Calculating %s" % team.name)
    p_record = get_performance_probability(team, est_best_rating)
    team.ratings['p_best'] = 1 - p_record

for idx, team in enumerate(sorted(list(teams.values()), key=lambda team: (team.ratings['sor_wa'] + team.ratings['pure_points']) / 2.0, reverse=True)):
    print("%s %s %s %s %s" % (
        idx + 1,
        team.name,
        round((team.ratings['sor_wa'] + team.ratings['pure_points']) / 2.0, 2),
        round(team.ratings['pure_points'], 2),
        round(team.ratings['sor_wa'], 2)
        ))

for idx, team in enumerate(sorted(list(teams.values()), key=lambda team: team.ratings['p_best'], reverse=True)):
    print("%s %s %s" % (idx + 1, team.name, team.ratings['p_best']))
