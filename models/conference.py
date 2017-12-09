import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-3])
sys.path.append(ROOT_PATH)

from models.helpers.constructor import build_instance

class Conference:
    SOURCE_COLUMNS = [
        'id', 'long_name', 'display_name',
        'abbreviation', 'fb_flair', 'bb_flair'
    ]

    @classmethod
    def build_all_from(cls, sourcefile):
        conferences = {}
        with open(sourcefile, 'r') as f:
            for line in f:
                conference = Conference.create_from(line)
                conferences[conference.id] = conference
        return conferences

    @classmethod
    def create_from(cls, line):
        columns = line.strip().split(',')
        return Conference(columns)

    def __init__(self, data):
        build_instance(self, self.SOURCE_COLUMNS, data)

    def __str__(self):
        return self.display_name
