import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from models.helpers.read_schedule import read_schedule
from processing.builders import build_filename_format
from processing.game_helpers import location_adjustment
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

    def difficulty(self, home_field_advantage):
        return self.get_opponent_rating() - location_adjustment(self.location, home_field_advantage)

    def game_score(self, home_field_advantage):
        return self.difficulty(home_field_advantage) + self.own_score - self.opp_score

    def get_opponent_rating(self):
        return self.opponent.ratings[RATINGS_PURE_POINTS]

    def get_overtime_string(self):
        if not self.overtime:
            return ""
        elif self.num_overtimes == 1:
            return " OT"
        else:
            return " %sOT" % self.num_overtimes

    def get_score_string(self):
        base = "%s-%s" % (self.own_score, self.opp_score)
        return base + self.get_overtime_string()

    def _default_location_adjustment(self, string):
        results = {
            'N': 0,
            'H': 3,
            'A': -3
        }
        return results[string]
