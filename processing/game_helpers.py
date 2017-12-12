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

def location_adjustment(string, HOME_FIELD_ADVANTAGE):
    return location_coefficient(string) * HOME_FIELD_ADVANTAGE

def predict_diff(team, game, HOME_FIELD_ADVANTAGE):
    own_rating = team.ratings[RATINGS_PURE_POINTS]
    opp_rating = game.opponent.ratings[RATINGS_PURE_POINTS]
    return own_rating - opp_rating + location_adjustment(game.location, HOME_FIELD_ADVANTAGE)
