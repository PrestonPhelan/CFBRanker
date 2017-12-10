import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
print(LOCAL_PATH)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
print(ROOT_PATH)
sys.path.append(ROOT_PATH)

from settings import CONFERENCE_PATH
from models.helpers.constructor import build_instance, build_set_from_file

class Conference:
    CONFERENCE_SOURCE = CONFERENCE_PATH % ROOT_PATH
    SOURCE_COLUMNS = [
        'id', 'long_name', 'display_name',
        'abbreviation', 'fb_flair', 'bb_flair'
    ]

    @classmethod
    def build_all(cls):
        return build_set_from_file(cls, cls.CONFERENCE_SOURCE)

    def __init__(self, data):
        build_instance(self, self.SOURCE_COLUMNS, data)

    def __str__(self):
        return self.display_name
