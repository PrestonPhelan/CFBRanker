import os
import numpy
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from processing.builders import build_markdown_row, build_markdown_barrier
from processing.game_helpers import *
from settings import *
from string_constants import *

def add_ratings_to_teams(teams, overall_coefficients, unit_coefficients):
    num_teams = len(teams)
    average_overall = sum(overall_coefficients) / float(num_teams)
    average_offense, average_defense = calculate_unit_averages(unit_coefficients, num_teams)

    for team in teams.values():
        off_id = get_off_id(team)
        def_id = get_def_id(team)

        raw_offense = unit_coefficients[off_id]
        if is_not_constant_team(team, teams):
            raw_overall = overall_coefficients[team.lin_eq_id]
            raw_defense = unit_coefficients[def_id]
        else:
            raw_overall = 0
            raw_defense = 0

        team.ratings[RATINGS_PURE_POINTS] = raw_overall + 50 - average_overall
        team.ratings[RATINGS_OFFENSE] = raw_offense + average_defense
        team.ratings[RATINGS_DEFENSE] = raw_defense + average_offense
    return True

def create_linear_equation_ids(teams):
    # Teams get id for linear equation coefficients
    # Return a list of teams in position for id lookup
    for idx, team in enumerate(teams.values()):
        team.lin_eq_id = idx
    return True

def build_overall_linear_equations(indexed_teams, HOME_FIELD_ADVANTAGE):
    lin_coeffs = []
    lin_results = []
    lin_eq_size = len(indexed_teams) - 1

    for team in indexed_teams.values():
        if not is_not_constant_team(team, indexed_teams):
            continue
        coefficients = [0] * lin_eq_size
        total_differential = 0
        location_adv = 0
        for game in team.games:
            location_adv += location_adjustment(game.location, HOME_FIELD_ADVANTAGE)
            # Assign counts to teams based on location
            if is_not_constant_team(team, indexed_teams):
                coefficients[team.lin_eq_id] += 1
            if is_not_constant_team(game.opponent, indexed_teams):
                coefficients[game.opponent.lin_eq_id] -= 1
            # Score Differential
            if OVERTIME_ADJUSTMENT and game.overtime == "True":
                if game.own_score < game.opp_score:
                    total_differential -= 0.5
                else:
                    total_differential += 0.5
            else:
                total_differential += game.own_score - game.opp_score
        lin_coeffs.append(coefficients)
        lin_results.append(total_differential - location_adv)
    return lin_coeffs, lin_results

def build_unit_linear_equations(indexed_teams, HOME_FIELD_ADVANTAGE):
    lin_coeffs = []
    lin_results = []
    lin_eq_size = len(indexed_teams) * 2 - 1

    for team in indexed_teams.values():
        # Assign coefficient ids
        off_id = get_off_id(team)
        if is_not_constant_team(team, indexed_teams):
            def_id = get_def_id(team)
        else:
            def_id = None

        # Setup variables to track
        off_coefficients = [0] * lin_eq_size
        def_coefficients = [0] * lin_eq_size
        total_points = 0
        total_points_allowed = 0
        location_adv = 0

        for game in team.games:
            off_coefficients[off_id] += 1
            if is_not_constant_team(game.opponent, indexed_teams):
                opponent_def_id = get_def_id(game.opponent)
                off_coefficients[opponent_def_id] += 1

            if def_id is not None:
                def_coefficients[def_id] += 1
                opponent_off_id = get_off_id(game.opponent)
                def_coefficients[opponent_off_id] += 1

            location_adv += location_adjustment(game.location, HOME_FIELD_ADVANTAGE) / 2.0

            total_points += game.own_score
            total_points_allowed += game.opp_score

        # Add to an array of arrays
        lin_coeffs.append(off_coefficients)
        if def_id is not None:
            lin_coeffs.append(def_coefficients)
        # Append differential to results
        lin_results.append(total_points - location_adv)
        if def_id is not None:
            lin_results.append(total_points_allowed - location_adv)

    return lin_coeffs, lin_results

def calculate_overall_coefficients(teams, HOME_FIELD_ADVANTAGE):
    lin_coeffs, lin_results = build_overall_linear_equations(teams, HOME_FIELD_ADVANTAGE)
    return linear_equation_solve(lin_coeffs, lin_results)

def calculate_unit_coefficients(teams, HOME_FIELD_ADVANTAGE):
    lin_coeffs, lin_results = build_unit_linear_equations(teams, HOME_FIELD_ADVANTAGE)
    return linear_equation_solve(lin_coeffs, lin_results)

def calculate_unit_averages(unit_coefficients, num_teams):
    total_off = 0
    total_def = 0
    for idx, rating in enumerate(unit_coefficients):
        if idx % 2 == 0:
            total_off += rating
        else:
            total_def += rating
    average_offense = total_off / float(num_teams)
    average_defense = total_def / float(num_teams)
    return average_offense, average_defense

def calculate_standard_deviations(teams, HOME_FIELD_ADVANTAGE):
    total_sse = 0
    total_games = 0
    for team in list(teams.values()):
        residuals = get_residuals(team, HOME_FIELD_ADVANTAGE)

        sum_squared_error = sum([residual * residual for residual in residuals])
        games_played = len(residuals)

        team.ratings[RATINGS_STD] = calculate_sample_standard_deviation(sum_squared_error, games_played, 1)

        total_sse += sum_squared_error
        total_games += games_played

    # Every game is listed twice (from each team's perspective)
    total_sse = total_sse / 2.0
    total_games = total_sse / 2.0
    return calculate_sample_standard_deviation(total_sse, total_games, len(teams) - 1)

def calculate_sample_standard_deviation(sum_squared_error, n, degrees_of_freedom_used):
    return numpy.sqrt(sum_squared_error / float(n - degrees_of_freedom_used))

def get_formatted_ratings_from_team(team):
    overall = round(team.ratings[RATINGS_PURE_POINTS], 2)
    offense = round(team.ratings[RATINGS_OFFENSE], 2)
    defense = round(team.ratings[RATINGS_DEFENSE], 2)
    std = round(team.ratings[RATINGS_STD], 2)
    return [overall, offense, defense, std]

def get_def_id(team):
    return team.lin_eq_id * 2 + 1

def get_off_id(team):
    return team.lin_eq_id * 2

def is_not_constant_team(team, team_list):
    return team.lin_eq_id != len(team_list) - 1

def linear_equation_solve(lin_coeffs, lin_results):
    a = numpy.array(lin_coeffs)
    b = numpy.array(lin_results)
    if len(a[0]) != len(b):
        print(len(a))
        print(len(a[0]))
        print(len(b))
    return numpy.linalg.solve(a, b)

def get_residuals(team, HOME_FIELD_ADVANTAGE):
    residuals = []
    for game in team.games:
        predicted_diff = predict_diff(team, game, HOME_FIELD_ADVANTAGE)
        actual_diff = game.own_score - game.opp_score
        if game.overtime and OVERTIME_ADJUSTMENT:
            # +/- 0.5 depending on if its a win or loss in OT
            actual_diff = actual_diff / (2 * numpy.absolute([actual_diff])[0])
        residuals.append(actual_diff - predicted_diff)
    return residuals

def write_to_csv(sorted_teams, PURE_POINTS_OUTPUT_CSV):
    with open(PURE_POINTS_OUTPUT_CSV, 'w+') as f:
        for idx, team in enumerate(sorted_teams):
            overall, offense, defense, std = get_formatted_ratings_from_team(team)
            columns = [idx + 1, team.name, overall, offense, defense, std]
            f.write(','.join([str(item) for item in columns]) + "\n")

def write_to_md(sorted_teams, PURE_POINTS_OUTPUT_MD, ADJUSTED_RATING_COEFFICIENT, SPORT):
    with open(PURE_POINTS_OUTPUT_MD, 'w+') as f:
        column_names = [
            'Rnk', 'Team', 'Record', 'Conference', 'Raw Rating',
            'Adjusted Rating', 'Offense Adj PPG', 'Defense Adj PPG',
            'Consistency'
        ]

        f.write(build_markdown_row(column_names))
        f.write(build_markdown_barrier(column_names))

        average_std = sum([team.ratings[RATINGS_STD] for team in sorted_teams]) / float(len(sorted_teams))
        for idx, team in enumerate(sorted_teams):
            overall, offense, defense, std = get_formatted_ratings_from_team(team)

            overall_adjusted = overall + (average_std - team.ratings[RATINGS_STD]) * ADJUSTED_RATING_COEFFICIENT
            overall_adjusted = round(overall_adjusted, 2)

            name_with_flair = " ".join([team.flair, team.name])
            record_string = "(%s-%s)" % (team.wins, team.losses)

            if SPORT == SPORT_FOOTBALL:
                conference_flair = team.conference.fb_flair
            elif SPORT == SPORT_BASKETBALL:
                conference_flair = team.conference.bb_flair
            else:
                raise "Unexpected/undefined sport %s" % SPORT

            columns = [
                idx + 1, name_with_flair, record_string, conference_flair,
                overall, overall_adjusted, offense, defense, std
            ]

            f.write(build_markdown_row(columns))

def calculate_pure_points_ratings_and_standard_deviation(teams, SPORT):
    if SPORT == SPORT_FOOTBALL:
        HOME_FIELD_ADVANTAGE = FB_HOME_FIELD_ADVANTAGE
        CURRENT_WEEK = FB_CURRENT_WEEK
        ADJUSTED_RATING_COEFFICIENT = FB_ADJUSTED_RATING_COEFFICIENT
    elif SPORT == SPORT_BASKETBALL:
        HOME_FIELD_ADVANTAGE = BB_HOME_COURT_ADVANTAGE
        CURRENT_WEEK = BB_CURRENT_WEEK
        ADJUSTED_RATING_COEFFICIENT = BB_ADJUSTED_RATING_COEFFICIENT

    PURE_POINTS_ROOT =  '%s/output/%s/pure-points-week%s' % (ROOT_PATH, SPORT, CURRENT_WEEK)
    PURE_POINTS_OUTPUT_CSV = PURE_POINTS_ROOT + '.csv'
    PURE_POINTS_OUTPUT_MD = PURE_POINTS_ROOT + '.md'

    create_linear_equation_ids(teams)

    overall_coefficients = calculate_overall_coefficients(teams, HOME_FIELD_ADVANTAGE)
    unit_coefficients = calculate_unit_coefficients(teams, HOME_FIELD_ADVANTAGE)

    add_ratings_to_teams(teams, overall_coefficients, unit_coefficients)

    overall_std = calculate_standard_deviations(teams, HOME_FIELD_ADVANTAGE)

    sorted_teams = sorted(teams.values(), key=lambda team: team.ratings[RATINGS_PURE_POINTS], reverse=True)

    write_to_csv(sorted_teams, PURE_POINTS_OUTPUT_CSV)
    write_to_md(sorted_teams, PURE_POINTS_OUTPUT_MD, ADJUSTED_RATING_COEFFICIENT, SPORT)

    return overall_std
