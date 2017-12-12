import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from models.team import Team
from processing.pure_points import calculate_pure_points_ratings_and_standard_deviation
from string_constants import SPORT_BASKETBALL

SPORT = SPORT_BASKETBALL

teams = Team.build_all_with_games(SPORT)
overall_std = calculate_pure_points_ratings_and_standard_deviation(teams, SPORT)
