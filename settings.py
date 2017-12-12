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

OVERTIME_ADJUSTMENT = True

BB_OPTIONS = {
    OPTIONS_CURRENT_WEEK: 7,
    OPTIONS_HOME_FIELD_ADVANTAGE: 3.3,
    OPTIONS_ADJUSTED_RATING_COEFFICIENT: 1.0
}

FB_OPTIONS = {
    OPTIONS_CURRENT_WEEK: 16,
    OPTIONS_HOME_FIELD_ADVANTAGE: 3.0,
    OPTIONS_ADJUSTED_RATING_COEFFICIENT: 0.9
}
