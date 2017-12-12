import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from settings import FB_OPTIONS, BB_OPTIONS
from string_constants import SPORT_FOOTBALL, SPORT_BASKETBALL

def import_options(sport):
    if sport == SPORT_FOOTBALL:
        options = FB_OPTIONS
    elif sport == SPORT_BASKETBALL:
        options = BB_OPTIONS
    else:
        raise "Unexpected sport %s" % sport

    return options
