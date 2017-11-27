import os
from scipy.stats import norm
from settings import CURRENT_WEEK
from processing.builders import build_filename_format

root_path = os.path.dirname(os.path.abspath(__file__))
combos = {}
RATING = 97
loss_counts = {}

with open(root_path + '/output/standings-week%s.csv' % CURRENT_WEEK) as f:
    for line in f:
        team, record = line.strip().split(',')
        loss_counts[team] = int(record.split('-')[1])


def choose_iter(elements, length):
    for i, _ in enumerate(elements):
        if length == 1:
            yield (elements[i],)
        else:
            for next in choose_iter(elements[i+1:len(elements)], length-1):
                yield (elements[i],) + next

def choose(l, k):
    nums = range(l)
    return list(choose_iter(nums, k))

def calc_product(num_list, loss_list = {}):
    product = 1
    for idx, num in enumerate(num_list):
        if idx in loss_list:
            product = product * (1 - num)
        else:
            product = product * num
    return product

def get_probabilities(team):
    filename_format_name = build_filename_format(team)
    source = root_path + "/output/schedule_ratings/%s.csv" % filename_format_name
    game_ratings = []
    with open(source, 'r') as f:
        for line in f:
            _, _, _, rating = line.strip().split(',')
            game_ratings.append(float(rating))
    return calculate_probabilities(game_ratings, RATING)

def calculate_probabilities(schedule, rating):
    win_probs = []
    for game_rating in schedule:
        win_prob = calculate_game_probability(rating, game_rating)
        win_probs.append(win_prob)
    return win_probs

def calculate_schedule_probability(win_probs, losses):
    if losses == 0:
        return calc_product(win_probs)
    num_games = len(win_probs)
    combinations = None
    lookup_string = '%s-%s' % (num_games, losses)
    if lookup_string in combos:
        combinations = combos[lookup_string]
    else:
        combinations = choose(num_games, losses)
        combos[lookup_string] = combinations
    total_prob = 0
    for loss_list in combinations:
        total_prob += calc_product(win_probs, loss_list)
    return total_prob

def calculate_game_probability(own_rating, game_rating):
    z_score = (own_rating - game_rating) / 16.0
    return norm.cdf(z_score)

def get_performance_probability(team):
    win_probs = get_probabilities(team)
    losses = loss_counts[team]
    sum_of_probs = 0
    current_loss_counter = 0
    while current_loss_counter <= losses:
        sum_of_probs += calculate_schedule_probability(win_probs, current_loss_counter)
        current_loss_counter += 1
    return sum_of_probs

print(get_performance_probability('Clemson'))
