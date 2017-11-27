import os
from processing.builders import build_filename_format
from processing.readers import process_power_name
from constants.name_translations import POWER_NAMES

root_path = os.path.dirname(os.path.abspath(__file__))
print(root_path)
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
            game_list.append({'location': location, 'opponent': opponent})


    # For each game
    for game in game_list:
        # Look up rating from combined
        game['combined_rating'] = combined_ratings[game['opponent']]
        # Look up rating from power
        game['power_rating'] = power_ratings[game['opponent']]

    # Write file
    write_file = root_path + '/output/schedule_ratings/%s.csv' % filename_format_name
    with open(write_file, 'w+') as f:
        for game in game_list:
            location_adjustment = 0
            if game['location'] == 'H':
                location_adjustment = -2.8
            elif game['location'] == 'A':
                    location_adjustment = 2.8
            text = "%s,%s,%s,%s\n" % (game['location'], game['opponent'], game['combined_rating'] + location_adjustment, game['power_rating'] + location_adjustment)
            f.write(text)
    print('Done with %s' % name)

get_and_save_rating('Florida')
