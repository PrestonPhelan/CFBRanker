import time
import os
import sys

import scrapy

from settings import CURRENT_WEEK
from constants.name_translations import PERFORMANCE_NAMES, find_match
from processing.builders import build_filename_format

local_path = os.path.dirname(__file__)
root_path = '/'.join(local_path.split('/')[:-3])
sys.path.append(root_path)
# Spider settings
wait_between_calls = False
seconds_between_calls = 0.25

id_source = "%s/constants/performance_ids.txt" % root_path
bb_id_source = "%s/constants/bb_performance_ids.txt" % root_path

class MothershipSpider(scrapy.Spider):
    def start_requests(self):
        base_url = 'https://www.espn.com/college-football/team/fpi/_/id/'
        with open(id_source) as f:
            for line in f:
                url = base_url + str(line.strip())
                yield scrapy.Request(url=url, callback=self.parse)
                if wait_between_calls:
                    time.sleep(seconds_between_calls)

    def _get_team_name(self, response):
        team = response.css("h3[class^='txt-ncf-']::text").extract()
        return team[0]

    def parse(self, response):
        pass

class PerformanceSpider(MothershipSpider):
    name = "performance_ratings"
    write_file = '%s/output/performance-ratings-week%s.csv' % (root_path, CURRENT_WEEK)

    def parse(self, response):
        target_rows = response.css('tr.oddrow td:last-of-type::text').extract()[:2]
        ranks = map(lambda row: self._get_rank_from_row(row), target_rows)
        team_name = self._get_team_name(response)
        # data = [SOR, GC, Team Name]
        data = ranks + [team_name]
        with open(self.write_file, 'a+') as f:
            f.write(','.join(data) + '\n')

    def _get_rank_from_row(self, row):
        split = row.split(' ')
        return split[1][1:-1]

class ScheduleSpider(MothershipSpider):
    name = "schedules"
    write_directory = '%s/output/schedules/' % root_path
    names = set()

    def start_requests(self):
        name_source = '%s/constants/names.txt' % root_path
        with open(name_source) as f:
            name_list = list(f)
            for line in name_list:
                name, _ = line.strip().split(',')
                self.names.add(name)
        requests = super(ScheduleSpider, self).start_requests()
        for request in requests:
            yield request

    def parse(self, response):
        team_name = self._get_team_name(response)
        if team_name in PERFORMANCE_NAMES:
            standardized_name = PERFORMANCE_NAMES[team_name]
        else:
            standardized_name = find_match(team_name, self.names)
        filename_format_name = build_filename_format(standardized_name)
        filename_format_name += '.csv'
        write_file = self.write_directory + filename_format_name
        locations = self._extract_locations(response)
        opponents = self._extract_opponents(response)
        played = self._game_played(response)
        game_results = self._extract_scores(response)
        idx = 0
        with open(write_file, 'w+') as f:
            skips = 0
            while idx < len(opponents):
                location = locations[idx]
                opponent = opponents[idx]
                if opponent.endswith('*'):
                    location = 'N'
                    opponent = opponent[:-1]
                if played[idx]:
                    result_string = "%s,%s" % (
                        game_results['results'][idx - skips],
                        game_results['scores'][idx - skips])
                else:
                    result_string = "--,--"
                    skips += 1
                line = "%s,%s,%s,%s\n" % (location, opponent, played[idx], result_string)
                f.write(line)
                idx += 1

    def _extract_locations(self, response):
        raw_locations = response.css('.game-schedule .game-status:not(.loss):not(.win)::text').extract()
        locations = map(lambda location: location.strip(), raw_locations)
        additional_text = map(lambda response: map(lambda item: item.strip(), response.css('li::text').extract()), response.css('li.team-name'))
        for idx, text_items in enumerate(additional_text):
            if '*' in text_items:
                locations[idx] = 'N'
        return locations

    def _extract_opponents(self, response):
        return response.css('li.team-name a::text').extract()

    def _extract_scores(self, response):
        results = response.css('.game-status.loss ::text,.game-status.win ::text').extract()
        scores = response.css('.score a::text').extract()
        return { 'results': results, 'scores': scores }

    def _game_played(self, response):
        game_scores = response.css(".tablehead tr:last-of-type .tablehead tr[class$='row'] td:last-of-type::text").extract()
        return map(lambda score: score != u'--', game_scores)

class BBScheduleSpider(MothershipSpider):
    name = "bb_schedules"
    write_directory = '%s/output/basketball/schedules/' % root_path
    names = set()

    def start_requests(self):
        base_url = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/"
        bb_name_source = '%s/constants/bb_names.txt' % root_path
        name_source = '%s/constants/names.txt' % root_path
        with open(bb_name_source) as f:
            name_list = list(f)
            for line in name_list:
                name, _ = line.strip().split(',')
                self.names.add(name)
        with open(name_source) as f:
            name_list = list(f)
            for line in name_list:
                name, _ = line.strip().split(',')
                self.names.add(name)
        with open(id_source) as f:
            for line in f:
                url = base_url + str(line.strip())
                yield scrapy.Request(url=url, callback=self.parse)
                if wait_between_calls:
                    time.sleep(seconds_between_calls)
        with open(bb_id_source) as f:
            for line in f:
                url = base_url + str(line.strip())
                yield scrapy.Request(url=url, callback=self.parse)
                if wait_between_calls:
                    time.sleep(seconds_between_calls)

    def parse(self, response):
        name = response.css("h2 a b::text").extract()[0]
        if name in PERFORMANCE_NAMES:
            matched_name = PERFORMANCE_NAMES[name]
        else:
            matched_name = find_match(name, self.names)
        filename_format_name = build_filename_format(matched_name)
        filename_format_name += '.csv'
        write_file = self.write_directory + filename_format_name
        locations = self._extract_locations(response)
        opponents = self._extract_opponents(response)
        game_results = self._extract_scores(response)
        idx = 0
        with open(write_file, 'w+') as f:
            while idx < len(opponents):
                location = locations[idx]
                opponent = opponents[idx]
                if opponent.endswith('*'):
                    location = 'N'
                    opponent = opponent[:-1]
                if idx < len(game_results['results']):
                    result_string = "%s,%s" % (
                        game_results['results'][idx],
                        game_results['scores'][idx])
                else:
                    result_string = "--,--"
                line = "%s,%s,%s\n" % (location, opponent, result_string)
                f.write(line)
                idx += 1

    def _extract_locations(self, response):
        raw_locations = response.css('.game-schedule .game-status:not(.loss):not(.win)::text').extract()
        locations = map(lambda location: location.strip(), raw_locations)
        additional_text = map(lambda response: map(lambda item: item.strip(), response.css('li::text').extract()), response.css('li.team-name'))
        for idx, text_items in enumerate(additional_text):
            if '*' in text_items:
                locations[idx] = 'N'
        return locations

    def _extract_opponents(self, response):
        candidates = response.css('li.team-name::text, li.team-name a::text').extract()
        opponents = filter(lambda string: string != u'*' and not string.startswith('#'), candidates)
        return opponents

    def _extract_scores(self, response):
        results = response.css('.game-status.loss ::text,.game-status.win ::text').extract()
        scores = response.css('.score a::text').extract()
        return { 'results': results, 'scores': scores }
