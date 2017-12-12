import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from processing.schedule_output import write_pretty_schedule_files
from processing.pure_points import calculate_pure_points_ratings_and_standard_deviation
from processing.strength_of_record import SORCalculator
from models.team import Team

def run_all(sport):
    teams = Team.build_all_with_games(sport)
    team_list = teams.values()
    overall_std = calculate_pure_points_ratings_and_standard_deviation(teams, sport)
    print("DONE: Pure points")
    print("Game standard deviation is %s" % round(overall_std, 2))
    write_pretty_schedule_files(team_list, sport)
    print("DONE: Human schedules")
    SORCalculator(team_list, sport, overall_std)
