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

from settings import CURRENT_WEEK
from constants.name_translations import PERFORMANCE_NAMES, find_match
from processing.builders import build_filename_format

# Spider Settings
WAIT_BETWEEN_CALLS = False
SECONDS_BETWEEN_CALLS = 0.25

# Local Source Files
FB_ID_SOURCE = "%s/constants/fb_performance_ids.txt" % ROOT_PATH
BB_ID_SOURCE = "%s/constants/bb_performance_ids.txt" % ROOT_PATH
FB_NAME_SOURCE = '%s/constants/names.txt' % ROOT_PATH
BB_NAME_SOURCE = '%s/constants/bb_names.txt' % ROOT_PATH

# Web Base URLs
FB_BASE_URL = 'https://www.espn.com/college-football/team/fpi/_/id/'
BB_BASE_URL = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/"

# Other Constants
RESULT_KEY = 'results'
SCORE_KEY = 'scores'
UNPLAYED_RESULT_STRING = "--,--"

class MothershipSpider(scrapy.Spider):
    # Used for matching name+nickname scraped from file to eligible names
    names = set()

    def start_requests(self):
        requests = self._yield_requests_from_file(FB_ID_SOURCE, FB_BASE_URL)
        for request in requests:
            yield request

    def parse(self, response):
        pass

    def _build_ouput_file_path(self, raw_name):
        # Takes in a raw name from a performance page, returns the write file path
        # param @raw_name: string, name taken directly from webpage
        # Output: string, file path to csv file created from standardized name to filname convention
        standard_name = self._convert_to_standard_name(raw_name)
        filename_format_name = build_filename_format(standard_name) + '.csv'
        return self.write_directory + filename_format_name

    def _convert_to_standard_name(self, name):
        # Takes in a raw name from a performance page, returns the standard name
        if name in PERFORMANCE_NAMES:
            return PERFORMANCE_NAMES[name]
        else:
            return find_match(name, self.names)

    def _extract_locations(self, response):
        # Extract location data from either page, return as an array
        raw_locations = response.css('.game-schedule .game-status:not(.loss):not(.win)::text').extract()
        locations = map(lambda location: location.strip(), raw_locations)
        additional_text = map(lambda response: map(lambda item: item.strip(), response.css('li::text').extract()), response.css('li.team-name'))
        for idx, text_items in enumerate(additional_text):
            if '*' in text_items:
                locations[idx] = 'N'
        return locations

    def _extract_opponents(self, response):
        # Extract opponent name from either page
        candidates = response.css('li.team-name::text, li.team-name a::text').extract()
        # Must filter out results from additional text added to items: neutral site indicators and rank indicators
        opponents = filter(lambda string: string != u'*' and not string.startswith('#'), candidates)
        return opponents

    def _extract_scores(self, response):
        # Extract result character and score from either page, return as object of arrays
        results = response.css('.game-status.loss ::text,.game-status.win ::text').extract()
        scores = response.css('.score a::text').extract()
        return { RESULT_KEY: results, SCORE_KEY: scores }

    def _get_fb_team_name_from_page(self, response):
        # Grab raw name from a FB page
        team = response.css("h3[class^='txt-ncf-']::text").extract()
        return team[0]

    def _get_standard_team_names(self, include_bb=False):
        # Get all needed standard names from constant file(s)
        self._get_standard_names_from_file(FB_NAME_SOURCE)
        if include_bb:
            self._get_standard_names_from_file(BB_NAME_SOURCE)

    def _get_standard_names_from_file(self, name_file_path):
        # Get the standard names from a specific file
        with open(name_file_path) as f:
            for line in f:
                name, _ = line.strip().split(',')
                self.names.add(name)

    def _yield_requests_from_file(self, id_file_path, base_url):
        # Read in the url id numbers from a file, yield requests to those pages
        with open(id_file_path) as f:
            for line in f:
                url = base_url + str(line.strip())
                yield scrapy.Request(url=url, callback=self.parse)
                if WAIT_BETWEEN_CALLS:
                    time.sleep(SECONDS_BETWEEN_CALLS)

class FBScheduleSpider(MothershipSpider):
    name = "fb_schedules"
    write_directory = '%s/output/football/schedules/' % ROOT_PATH

    def start_requests(self):
        self._get_standard_team_names()
        requests = super(FBScheduleSpider, self).start_requests()
        for request in requests:
            yield request

    def parse(self, response):
        team_name = self._get_fb_team_name_from_page(response)
        write_file = self._build_ouput_file_path(team_name)
        locations = self._extract_locations(response)
        opponents = self._extract_opponents(response)
        played = self._extract_game_played(response)
        game_results = self._extract_scores(response)

        with open(write_file, 'w+') as f:
            skips = 0
            for idx, _ in enumerate(opponents):
                game_played = played[idx]
                if game_played:
                    result = game_results[RESULT_KEY][idx - skips]
                    score = game_results[RESULT_KEY][idx - skips]
                    result_string = ",".join([result, score])
                else:
                    result_string = UNPLAYED_RESULT_STRING
                    skips += 1
                location = locations[idx]
                opponent = opponents[idx]
                line = ",".join([location, opponent, str(game_played), result_string]) + "\n"
                f.write(line)

    def _extract_game_played(self, response):
        # Accounts for cancelled games
        game_scores = response.css(".tablehead tr:last-of-type .tablehead tr[class$='row'] td:last-of-type::text").extract()
        return map(lambda score: score != u'--', game_scores)

class BBScheduleSpider(MothershipSpider):
    name = "bb_schedules"
    write_directory = '%s/output/basketball/schedules/' % ROOT_PATH

    def start_requests(self):
        self._get_standard_team_names(include_bb=True)
        fbs_requests = self._yield_requests_from_file(FB_ID_SOURCE, BB_BASE_URL)
        bb_requests = self._yield_requests_from_file(BB_ID_SOURCE, BB_BASE_URL)
        for request in fbs_requests:
            yield request
        for request in bb_requests:
            yield request

    def parse(self, response):
        name = response.css("h2 a b::text").extract()[0]
        write_file = self._build_ouput_file_path(name)
        locations = self._extract_locations(response)
        opponents = self._extract_opponents(response)
        game_results = self._extract_scores(response)
        with open(write_file, 'w+') as f:
            for idx, _ in enumerate(opponents):
                if idx < len(game_results[RESULT_KEY]):
                    result = game_results[RESULT_KEY][idx]
                    score = game_results[SCORE_KEY][idx]
                    result_string = ",".join([result, score])
                else:
                    result_string = UNPLAYED_RESULT_STRING
                location = locations[idx]
                opponent = opponents[idx]
                line = ",".join([location, opponent, result_string]) + "\n"
                f.write(line)

# DEPRECATED
class PerformanceSpider(MothershipSpider):
    name = "performance_ratings"
    write_file = '%s/output/football/performance-ratings-week%s.csv' % (ROOT_PATH, CURRENT_WEEK)

    def parse(self, response):
        target_rows = response.css('tr.oddrow td:last-of-type::text').extract()[:2]
        ranks = map(lambda row: self._get_rank_from_row(row), target_rows)
        team_name = self._get_fb_team_name_from_page(response)
        # data = [SOR, GC, Team Name]
        data = ranks + [team_name]
        with open(self.write_file, 'a+') as f:
            f.write(','.join(data) + '\n')

    def _get_rank_from_row(self, row):
        split = row.split(' ')
        return split[1][1:-1]
