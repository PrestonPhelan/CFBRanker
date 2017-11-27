import os
from processing.builders import build_filename_format
from processing.readers import process_power_name
from constants.name_translations import *

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
                location, opponent, _, _, _ = columns
            else:
                location, opponent, _ = columns
            if location == 'vs':
                location = 'H'
            elif location == '@':
                location = 'A'
            # Build list of games
            if opponent in SCHEDULE_NAMES:
                opponent = SCHEDULE_NAMES[opponent]
            game_list.append({'location': location, 'opponent': opponent})


    # For each game
    for game in game_list:
        # Look up rating from combined
        if game['opponent'] in combined_ratings:
            game['combined_rating'] = combined_ratings[game['opponent']]
            # Look up rating from power
            game['power_rating'] = power_ratings[game['opponent']]
        else:
            print("Couldn't find %s" % game['opponent'])
            game['combined_rating'] = 40
            game['power_rating'] = 40

    # Write file
    write_file = root_path + '/output/schedule_ratings/%s.csv' % filename_format_name
    with open(write_file, 'w+') as f:
        for game in game_list:
            game['location_adjustment'] = 0
            if game['location'] == 'H':
                game['location_adjustment'] = -2.8
            elif game['location'] == 'A':
                    game['location_adjustment'] = 2.8
            game['combined_rating'] = game['combined_rating'] + game['location_adjustment']
            game['power_rating'] = game['power_rating'] + game['location_adjustment']
            text = "%s,%s,%s,%s\n" % (game['location'], game['opponent'], game['combined_rating'], game['power_rating'])
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
                'rating': rated_difficulty
            }
            f.write(text)

    print('Done with %s' % name)

team_source = root_path + "/constants/names.txt"
with open(team_source, 'r') as f:
    for line in f:
        name, _ = line.strip().split(',')
        get_and_save_rating(name)
