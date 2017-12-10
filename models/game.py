import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from models.helpers.read_schedule import read_schedule
from processing.builders import build_filename_format
from settings import SCHEDULE_GENERIC_PATH
from string_constants import *

class Game:

    def __init__(self, details):
        self.location = details[GAME_LOCATION]
        self.opponent = details[GAME_OPPONENT]
        self.result = details[GAME_RESULT]
        self.own_score = details[GAME_OWN_SCORE]
        self.opp_score = details[GAME_OPP_SCORE]
        self.overtime = details[GAME_OVERTIME]
        self.num_overtimes = details[GAME_NUM_OTS]

    def __str__(self):
        string_to_print = "%(location)s vs. %(opponent)s, %(result)s %(own_score)s-%(opp_score)s" % {
            'location': self.location,
            'opponent': self.opponent,
            'result': self.result,
            'own_score': self.own_score,
            'opp_score': self.opp_score
        }
        if self.overtime:
            if self.num_overtimes > 1:
                string_to_print = string_to_print + " %sOT\n" % self.num_overtimes
            else:
                string_to_print = string_to_print + " OT\n"
        else:
            string_to_print += "\n"

        return string_to_print

    def difficulty(self, location_adjustment_func):
        return self.opponent.ratings['pure_points'] - location_adjustment_func(self.location)

    def _default_location_adjustment(self, string):
        results = {
            'N': 0,
            'H': 3,
            'A': -3
        }
        return results[string]
