import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from scripts.run_all import run_all
from scripts.build_bracket import build_bracket
from string_constants import SPORT_BASKETBALL

SPORT = SPORT_BASKETBALL
teams = run_all(SPORT)
build_bracket(teams)
