import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-3])
sys.path.append(ROOT_PATH)

from models.helpers.constructor import build_instance, build_set_from_file

class Conference:
    SOURCE_COLUMNS = [
        'id', 'long_name', 'display_name',
        'abbreviation', 'fb_flair', 'bb_flair'
    ]

    @classmethod
    def build_all_from(cls, sourcefile):
        return build_set_from_file(cls, sourcefile)

    def __init__(self, data):
        build_instance(self, self.SOURCE_COLUMNS, data)

    def __str__(self):
        return self.display_name
