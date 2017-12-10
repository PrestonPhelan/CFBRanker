### All spiders associated with scraping from the mothership
### Should only gather information - not interpret or process
### Unless absolutely necessary (i.e., neutral location identification)

import time
import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-3])
sys.path.append(ROOT_PATH)

import scrapy

from settings import CURRENT_WEEK, TEAM_PATH
from constants.name_translations import PERFORMANCE_NAMES, SCHEDULE_NAMES, find_match
from processing.builders import build_filename_format

# Spider Settings
WAIT_BETWEEN_CALLS = False
SECONDS_BETWEEN_CALLS = 0.5

# Web Base URLs
FB_BASE_URL = 'https://www.espn.com/college-football/team/fpi/_/id/'
BB_BASE_URL = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/"

# Local sources
TEAM_SOURCE = TEAM_PATH % ROOT_PATH

# Other Constants
RESULT_KEY = 'results'
SCORE_KEY = 'scores'
UNPLAYED_RESULT_STRING = "--,--"

# Helper Methods
def extract_locations(response):
    # Extract location data from either page, return as an array
    raw_locations = response.css('.game-schedule .game-status:not(.loss):not(.win)::text').extract()
    locations = map(lambda location: location.strip(), raw_locations)
    additional_text = map(lambda response: map(lambda item: item.strip(), response.css('li::text').extract()), response.css('li.team-name'))
    for idx, text_items in enumerate(additional_text):
        if '*' in text_items:
            locations[idx] = 'N'
    return locations

def extract_opponents(response):
    # Extract opponent name from either page
    candidates = response.css('li.team-name::text, li.team-name a::text').extract()
    # Must filter out results from additional text added to items: neutral site indicators and rank indicators
    opponents = filter(lambda string: string != u'*' and not string.startswith('#'), candidates)
    return opponents

def extract_scores(response):
    # Extract result character and score from either page, return as object of arrays
    results = response.css('.game-status.loss ::text,.game-status.win ::text').extract()
    scores = response.css('.score a::text, .score::text, tr[class$=row] td span::text').extract()
    scores = [el for el in scores if is_score(el) or el in ["Canceled", "Postponed"]]
    if len(results) != len(scores):
        # Scores will capture 'Canceled' games
        cancelled_idx = [idx for idx, text in enumerate(scores) if not is_score(text)]
        for idx in cancelled_idx:
            results.insert(idx, scores[idx])
    if len(results) != len(scores):
        raise "Something went wrong in accounting for cancelled games"
    return { RESULT_KEY: results, SCORE_KEY: scores }

def is_score(string):
    # Checks to see if a string is a score string
    return len(string.split('-')) > 1

class MothershipSpider(scrapy.Spider):
    # Used for matching name+nickname scraped from file to eligible names
    names = {}

    def start_requests(self):
        self._build_standard_name_object()
        requests = self._yield_requests_from_file(self.BASE_URL, self.FOOTBALL)
        for request in requests:
            yield request

    def parse(self, response):
        name = self.names[response.url.split("/")[-1]]
        write_file = self._build_ouput_file_path(name)
        locations = extract_locations(response)
        opponents = extract_opponents(response)
        game_results = extract_scores(response)
        with open(write_file, 'w+') as f:
            for idx in range(len(opponents)):
                if idx < len(game_results[RESULT_KEY]) and is_score(game_results[SCORE_KEY][idx]):
                    result = game_results[RESULT_KEY][idx]
                    score = game_results[SCORE_KEY][idx]
                    result_string = ",".join([result, score])
                else:
                    result_string = UNPLAYED_RESULT_STRING
                location = locations[idx]
                opponent = opponents[idx]
                line = ",".join([location, opponent, result_string]) + "\n"
                f.write(line)

    def _build_ouput_file_path(self, standard_name):
        # Takes in a raw name from a performance page, returns the write file path
        # param @standard_name: string, standardized name
        # Output: string, file path to csv file created from standardized name to filname convention
        filename_format_name = build_filename_format(standard_name) + '.csv'
        return self.WRITE_DIRECTORY + filename_format_name

    def _build_standard_name_object(self):
        # Get all needed standard names from constant file(s)
        with open(TEAM_SOURCE) as f:
            for line in f:
                columns = line.strip().split(",")
                standard_name = columns[0]
                scrape_id = columns[1]
                self.names[scrape_id] = standard_name

    def _yield_requests_from_file(self, base_url, fb=False):
        # Read in the url id numbers from a file, yield requests to those pages
        with open(TEAM_SOURCE) as f:
            for line in f:
                columns = line.strip().split(",")
                if fb and columns[-3] == "None":
                    continue
                scrape_id = columns[1]
                url = base_url + scrape_id
                yield scrapy.Request(url=url, callback=self.parse)
                if WAIT_BETWEEN_CALLS:
                    time.sleep(SECONDS_BETWEEN_CALLS)

class FBScheduleSpider(MothershipSpider):
    name = "fb_schedules"
    WRITE_DIRECTORY = '%s/output/football/schedules/' % ROOT_PATH
    BASE_URL = FB_BASE_URL
    FOOTBALL = True

class BBScheduleSpider(MothershipSpider):
    name = "bb_schedules"
    WRITE_DIRECTORY = '%s/output/basketball/schedules/' % ROOT_PATH
    BASE_URL = BB_BASE_URL
    FOOTBALL = False

# DEPRECATED
# class PerformanceSpider(MothershipSpider):
#     name = "performance_ratings"
#     write_file = '%s/output/football/performance-ratings-week%s.csv' % (ROOT_PATH, CURRENT_WEEK)
#
#     def parse(self, response):
#         target_rows = response.css('tr.oddrow td:last-of-type::text').extract()[:2]
#         ranks = map(lambda row: self._get_rank_from_row(row), target_rows)
#         team_name = get_fb_team_name_from_page(response)
#         # data = [SOR, GC, Team Name]
#         data = ranks + [team_name]
#         with open(self.write_file, 'a+') as f:
#             f.write(','.join(data) + '\n')
#
#     def _get_rank_from_row(self, row):
#         split = row.split(' ')
#         return split[1][1:-1]


# class TeamSpider(BBScheduleSpider):
#     ## One time use to build team data
#     name = "teams_collect"
#     write_file = '%s/constants/teams.csv' % ROOT_PATH
#
#     REDDIT_NAMES = {
#     # Unlike others above, this dictionary has keys that
#     # are the standard names, and translates for output
#     # in reddit flairs
#     'East Carolina': '[ECU](#f/eastcarolina)',
#     'Florida Atlantic': '[FAU](#f/fau)',
#     'Hawaii': "[Hawai'i](#f/hawaii)",
#     'Louisiana Monroe': "[ULM](#f/ulm)",
#     'Massachusetts': "[UMass](#f/umass)",
#     'Miami (OH)': "[Miami (OH)](#f/miamioh)",
#     'South Florida': "[USF](#f/usf)",
#     'Texas A&M': "[Texas A&M](#f/texasam)",
#     'Western Kentucky': "[WKU](#f/wku)"
#     }
#
#     fb_ids = set()
#     with open(FB_ID_SOURCE) as f:
#         for line in f:
#             fb_ids.add(line.strip())
#
#     fb_conferences = {}
#     with open('%s/constants/names.txt' % ROOT_PATH) as f:
#         for line in f:
#             team_name, conference = line.strip().split(',')
#             fb_conferences[team_name] = conference
#
#     bb_conferences = {}
#     with open('%s/constants/bb_names.txt' % ROOT_PATH) as f:
#         for line in f:
#             team_name, conference = line.strip().split(',')
#             bb_conferences[team_name] = conference
#
#     conf_by_abbrev = {}
#     conf_by_display_name = {}
#     with open('%s/constants/conferences.csv' % ROOT_PATH) as f:
#         for line in f:
#             conf_id, _, display_name, short_name, _, _ = line.strip().split(',')
#             conf_by_abbrev[short_name] = conf_id
#             conf_by_display_name[short_name] = conf_id
#
#     def parse(self, response):
#         scrape_name = response.css("h2 a b::text").extract()[0]
#         scrape_id = response.url.split("/")[-1]
#         standard_name = self._convert_to_standard_name(scrape_name)
#         schedule_name = None
#         for sch_name, std_name in SCHEDULE_NAMES.items():
#             if std_name == standard_name:
#                 schedule_name = sch_name
#         if schedule_name is None:
#             schedule_name = standard_name
#         flair_string = None
#         if standard_name in self.REDDIT_NAMES:
#             flair_string = self.REDDIT_NAMES[standard_name]
#         else:
#             combo_string = ''
#             for character in standard_name:
#                 if character.isalpha():
#                     combo_string += character.lower()
#             flair_string = "[%s](#f/%s)" % (standard_name, combo_string)
#         if scrape_id in self.fb_ids:
#             football_level = "FBS"
#         else:
#             football_level = "FCS"
#         fb_conf_id = None
#         bb_conf_id = None
#         if standard_name in self.fb_conferences:
#             fb_written_conf = self.fb_conferences[standard_name]
#             if standard_name not in self.bb_conferences:
#                 bb_written_conf = self.fb_conferences[standard_name]
#             else:
#                 bb_written_conf = self.bb_conferences[standard_name]
#         else:
#             fb_written_conf = self.bb_conferences[standard_name]
#             bb_written_conf = self.bb_conferences[standard_name]
#         if fb_written_conf in self.conf_by_abbrev:
#             fb_conf_id = self.conf_by_abbrev[fb_written_conf]
#         elif fb_written_conf in self.conf_by_display_name:
#             fb_conf_id = self.conf_by_display_name[fb_written_conf]
#         if fb_written_conf == bb_written_conf:
#             bb_conf_id = fb_conf_id
#         else:
#             if bb_written_conf in self.conf_by_abbrev:
#                 bb_conf_id = self.conf_by_abbrev[bb_written_conf]
#             elif bb_written_conf in self.conf_by_display_name:
#                 bb_conf_id = self.conf_by_display_name[bb_written_conf]
#
#         if fb_conf_id is None:
#             fb_conf_id = "MISSING"
#         if bb_conf_id is None:
#             bb_conf_id = "MISSING"
#         items = [standard_name, scrape_id, scrape_name, schedule_name, flair_string, football_level, fb_conf_id, bb_conf_id]
#         with open(self.write_file, 'a+') as f:
#             f.write(",".join(items) + '\n')
