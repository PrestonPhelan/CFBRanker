import os
import sys

ROOT_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_PATH)

from string_constants import OPTIONS_CURRENT_WEEK
from string_constants import OPTIONS_HOME_FIELD_ADVANTAGE
from string_constants import OPTIONS_ADJUSTED_RATING_COEFFICIENT


CONFERENCE_PATH = "%s/constants/conferences.csv"
TEAM_PATH = "%s/constants/teams.csv"
SCHEDULE_GENERIC_PATH = "%s/output/%s/schedules/"
PRETTY_SCHEDULE_GENERIC_PATH = "%s/output/%s/reddit_schedules/"
SOR_GENERIC_PATH = "%s/output/%s/sor-week%s.md"
COMPOSITE_GENERIC_PATH = "%s/output/%s/composite-week%s"

CALCULATE_P_OF_R = False
OVERTIME_ADJUSTMENT = True
NUM_SIMS = 10000

COMPOSITE_RATING_INCLUDES_PURE_POINTS = True
CONSISTENCY_ADJUSTMENT = False

BB_OPTIONS = {
    OPTIONS_CURRENT_WEEK: 17,
    OPTIONS_HOME_FIELD_ADVANTAGE: 3.2,
    OPTIONS_ADJUSTED_RATING_COEFFICIENT: 1.0
}

FB_OPTIONS = {
    OPTIONS_CURRENT_WEEK: 17,
    OPTIONS_HOME_FIELD_ADVANTAGE: 3.0,
    OPTIONS_ADJUSTED_RATING_COEFFICIENT: 0.9
}
