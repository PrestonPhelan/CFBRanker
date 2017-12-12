import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from string_constants import RATINGS_PURE_POINTS

def location_coefficient(string):
    coefficients = {
        'N': 0,
        'A': -1,
        'H': 1
    }
    return coefficients[string]

def location_adjustment(string, home_field_advantage):
    return location_coefficient(string) * home_field_advantage

def predict_diff(team, game, home_field_advantage):
    own_rating = team.ratings[RATINGS_PURE_POINTS]
    opp_rating = game.opponent.ratings[RATINGS_PURE_POINTS]
    return own_rating - opp_rating + location_adjustment(game.location, home_field_advantage)
