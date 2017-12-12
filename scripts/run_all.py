import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from processing.schedule_output import write_pretty_schedule_files
from processing.pure_points import calculate_pure_points_ratings_and_standard_deviation
from models.team import Team

def run_all(sport):
    teams = Team.build_all_with_games(sport)
    overall_std = calculate_pure_points_ratings_and_standard_deviation(teams, sport)
    print("DONE: Pure points")
    print("Game standard deviation is %s" % round(overall_std, 2))
    write_pretty_schedule_files(teams.values(), sport)
    print("DONE: Human schedules")
