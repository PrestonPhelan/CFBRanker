import os
import statistics
import math
from processing.builders import build_filename_format
from processing.readers import process_power_name
from constants.name_translations import *

INCLUDE_FCS = False

root_path = os.path.dirname(os.path.abspath(__file__))
combined_ratings = {}
with open(root_path + "/output/ratings-from-combined.csv") as f:
    for line in f:
        _, team, rating = line.strip().split(',')
        if rating == '"ratings"':
            continue
        combined_ratings[team[1:-1]] = float(rating)

power_ratings = {}
with open(root_path + "/output/ratings-from-power.csv") as f:
    for line in f:
        _, team, rating = line.strip().split(',')
        if rating == '"ratings"':
            continue
        team = team[1:-1]
        rating = float(rating)
        if team in POWER_NAMES:
            team = POWER_NAMES[team]
        else:
            team = process_power_name(team)
        power_ratings[team] = rating

team_sor_ratings = []
def get_and_save_rating(name):
    filename_format_name = build_filename_format(name)
    schedule_file = root_path + "/output/schedules/%s.csv" % filename_format_name
    # Open schedule file
    game_list = []
    with open(schedule_file) as f:
        for line in f:
            columns = line.strip().split(',')
            if columns[2] == 'False':
                continue
            if len(columns) == 5:
                location, opponent, _, result, score = columns
            if location == 'vs':
                location = 'H'
            elif location == '@':
                location = 'A'
            # Build list of games
            if opponent in SCHEDULE_NAMES:
                opponent = SCHEDULE_NAMES[opponent]
            if INCLUDE_FCS or opponent in combined_ratings:
                win_score, lose_score = score.split('-')
                overtime = False
                if len(lose_score.split(' ')) > 1:
                    lose_score, _ = lose_score.split(' ')
                    overtime = True
                if result == 'W':
                    differential = int(win_score) - int(lose_score)
                    own_score = win_score
                    opp_score = lose_score
                elif result == 'L':
                    differential = int(lose_score) - int(win_score)
                    own_score = lose_score
                    opp_score = win_score
                else:
                    raise "Invalid result found: %s" % result
                game_list.append({
                    'location': location,
                    'opponent': opponent,
                    'result': result,
                    'own_score': own_score,
                    'opp_score': opp_score,
                    'differential': differential,
                    'overtime': overtime
                })


    # For each game
    for game in game_list:
        # Look up rating from combined
        if game['opponent'] in combined_ratings:
            game['combined_rating'] = combined_ratings[game['opponent']]
            # Look up rating from power
            game['power_rating'] = power_ratings[game['opponent']]
        elif INCLUDE_FCS:
            print("Couldn't find %s" % game['opponent'])
            game['combined_rating'] = 40
            game['power_rating'] = 40
        else:
            game['combined_rating'] = '--'
            game['power_rating'] = '--'

    def calculate_res(result, opp_rating, differential, overtime):
        if overtime:
            if result == 'W':
                return opp_rating + 2.0
            elif result == 'L':
                return opp_rating - 2.0
            else:
                raise 'Unknown result found %s' % result
        else:
            if result == 'W':
                return opp_rating + 4.0 * math.sqrt(differential)
            elif result == 'L':
                return opp_rating - 4.0 * math.sqrt( -1.0 * differential )
            else:
                raise 'Unknown result found %s' % result

    # Write file
    write_file = root_path + '/output/schedule_ratings/%s.csv' % filename_format_name
    with open(write_file, 'w+') as f:
        adjusted_differential = 0
        result_emphasized_differential = 0
        game_count = 0
        game_scores = []
        for game in game_list:
            if game['combined_rating'] != '--':
                game['location_adjustment'] = 0
                if game['location'] == 'H':
                    game['location_adjustment'] = -2.8
                elif game['location'] == 'A':
                        game['location_adjustment'] = 2.8
                game['combined_rating'] = game['combined_rating'] + game['location_adjustment']
                game['power_rating'] = game['power_rating'] + game['location_adjustment']
                game_score = float(game['power_rating']) + game['differential']
                game_scores.append(game_score)
                adjusted_differential += game_score
                result_emphasized_score = calculate_res(game['result'], game['power_rating'], game['differential'], game['overtime'])
                result_emphasized_differential += result_emphasized_score
                game_count += 1
                text = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                    game['location'],
                    game['opponent'],
                    game['combined_rating'],
                    game['power_rating'],
                    game['result'],
                    game['differential'],
                    game['overtime'],
                    game_score,
                    game['own_score'],
                    game['opp_score'])
                f.write(text)


    sorted_games = sorted(game_list, key=lambda game: game['power_rating'], reverse=True)
    reddit_write_file = root_path + '/output/reddit_schedules/%s.txt' % filename_format_name
    with open(reddit_write_file, 'w+') as f:
        columns = ["Opponent", "Loc", "Rating"]
        header = " | ".join(columns) + "\n"
        barrier = "|".join(map(lambda _: "---", columns)) + "\n"
        f.write(header)
        f.write(barrier)
        for game in sorted_games:
            rated_difficulty = round((game['power_rating'] - 35) * 100 / 70)
            opponent = game['opponent']
            if opponent in REDDIT_NAMES:
                opponent = REDDIT_NAMES[opponent]
            else:
                combo_string = "".join(opponent.split(" ")).lower()
                opponent = "[%s](#f/%s) %s" % (opponent, combo_string, opponent)
            text = "%(opponent)s | %(location)s | %(rating)s |\n" % {
                'opponent': opponent,
                'location': game['location'],
                'rating': rated_difficulty,
            }
            f.write(text)

    team_sor_ratings.append({
        'team': name,
        'rating': adjusted_differential / game_count,
        'median': statistics.median(game_scores),
        'results_emphasized_rating': float(result_emphasized_differential) / game_count})
    print('Done with %s' % name)

team_source = root_path + "/constants/names.txt"
with open(team_source, 'r') as f:
    for line in f:
        name, _ = line.strip().split(',')
        get_and_save_rating(name)

sorted_sor = sorted(team_sor_ratings, key=lambda team: team['results_emphasized_rating'], reverse=True)
for idx, team in enumerate(sorted_sor):
    print("%s %s %s %s %s %s" % (idx + 1, team['team'], team['results_emphasized_rating'], team['rating'], team['median'], (team['rating'] + team['median']) / 2.0))
