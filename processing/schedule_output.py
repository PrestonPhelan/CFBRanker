import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from processing.builders import build_filename_format, build_markdown_row, build_markdown_barrier
from processing.game_helpers import location_adjustment
from processing.options_util import import_options
from settings import PRETTY_SCHEDULE_GENERIC_PATH
from string_constants import OPTIONS_HOME_FIELD_ADVANTAGE

def generate_write_file_path(team, sport):
    filename_format_name = build_filename_format(team.name)
    write_file_path = PRETTY_SCHEDULE_GENERIC_PATH % (ROOT_PATH, sport)
    return write_file_path + filename_format_name + ".md"

def write_schedule_file(team, write_file, home_field_advantage):
    with open(write_file, 'w+') as f:
        label_string = "%s (%s)" % (team.get_flair_with_name(), team.get_record())
        column_names = [label_string, "Rec", "Loc", "Difficulty", "Result", "Score", "Game Rating"]
        f.write(build_markdown_row(column_names))
        f.write(build_markdown_barrier(column_names))

        sorted_games = sorted(team.games, key=lambda game: game.difficulty(home_field_advantage), reverse=True)
        for game in sorted_games:
            f.write(schedule_line(game, home_field_advantage))

def schedule_line(game, home_field_advantage):
    columns = [
        game.opponent.get_flair_with_name(), game.opponent.get_record(), game.location,
        game.difficulty(home_field_advantage), game.result, game.get_score_string(),
        game.game_score(home_field_advantage)
    ]
    columns = [str(int(round(item, 0))) if isinstance(item, float) else item for item in columns]
    return " | ".join(columns) + "\n"

def write_pretty_schedule_files(team_list, sport):
    options = import_options(sport)
    home_field_advantage = options[OPTIONS_HOME_FIELD_ADVANTAGE]
    for team in team_list:
        write_file = generate_write_file_path(team, sport)
        write_schedule_file(team, write_file, home_field_advantage)
