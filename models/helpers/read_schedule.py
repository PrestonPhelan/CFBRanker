import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-2])
sys.path.append(ROOT_PATH)

from string_constants import *

WIN_SCORE = 'win_score'
LOSE_SCORE = 'lose_score'

def read_schedule(line, teams_by_schedule_name):
    location, opponent, result, score = line.strip().split(",")
    if result == UNPLAYED_INDICATOR:
        return None
    if opponent not in teams_by_schedule_name:
        return None
    opponent = teams_by_schedule_name[opponent]
    location = translate_location(location)
    result_details = read_score(score)
    own_score, opp_score = assign_scores(result, result_details)
    return {
        GAME_LOCATION: location,
        GAME_OPPONENT: opponent,
        GAME_RESULT: result,
        GAME_OWN_SCORE: int(own_score),
        GAME_OPP_SCORE: int(opp_score),
        GAME_OVERTIME: result_details[GAME_OVERTIME],
        GAME_NUM_OTS: result_details[GAME_NUM_OTS]
    }

def translate_location(string):
    translations = {
        'N': 'N',
        'vs': 'H',
        '@': 'A'
    }
    return translations[string]

def read_score(score_string):
    win_score, lose_score = score_string.split('-')
    overtime = False
    num_overtimes = None
    if len(lose_score.split(' ')) > 1:
        lose_score, ot_string = lose_score.split(' ')
        overtime = True
        if len(ot_string) > 2:
            num_overtimes = int(ot_string[0])
        else:
            num_overtimes = 1
    return {
        WIN_SCORE: win_score,
        LOSE_SCORE: lose_score,
        GAME_OVERTIME: overtime,
        GAME_NUM_OTS: num_overtimes
    }

def assign_scores(result, result_details):
    if result == 'W':
        return [result_details[WIN_SCORE], result_details[LOSE_SCORE]]
    elif result == 'L':
        return [result_details[LOSE_SCORE], result_details[WIN_SCORE]]
    else:
        raise "Unexpected result %s" % result
