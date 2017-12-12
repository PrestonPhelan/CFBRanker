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

def choose_iter(elements, length):
    for i, _ in enumerate(elements):
        if length == 1:
            yield (elements[i],)
        else:
            for next in choose_iter(elements[i+1:len(elements)], length-1):
                yield (elements[i],) + next

def choose(pop_size, num_elements_to_choose):
    nums = range(pop_size)
    return list(choose_iter(nums, num_elements_to_choose))

def calc_product(num_list, loss_list = {}):
    product = 1
    for idx, num in enumerate(num_list):
        if idx in loss_list:
            product = product * (1 - num)
        else:
            product = product * num
    return product
