import scrapy
import re
import os, sys
local_path = os.path.dirname(__file__)
root_path = '/'.join(local_path.split('/')[:-3])
sys.path.append(root_path)
from settings import FB_CURRENT_WEEK

class PowerSpider(scrapy.Spider):
    name = "power_ratings"

    def start_requests(self):
        url = 'https://www.masseyratings.com/cf/compare.htm'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        write_file = '%s/output/power-ratings-week%s.csv' % (root_path, CURRENT_WEEK)

        teams_in_order = response.css("a[href^='../team.php']::text").extract()[0:-11]
        if len(teams_in_order) != 130:
            raise "Wrong number of team names fetched."
        team_metrics = self._parse_team_metrics(response)
        if len(team_metrics) != 130:
            raise "Wrong number of metrics fetched."

        with open(write_file, 'wb') as f:
            for idx, team in enumerate(teams_in_order):
                metric_string = ','.join(team_metrics[idx])
                text = "%s,%s,%s\n" % (metric_string, str(idx + 1), team)
                f.write(text)
        self.log('Saved file %s' % write_file)

    def _parse_team_metrics(self, response):
        # REGEX VARIABLES
        start_of_lines = re.compile(r' ')
        decimal = re.compile(r'.')

        # CALLBACKS
        split_line = lambda line: line.split(' ')
        select_decimals = lambda results: filter(decimal.search, results)[-3:]
        parse_to_floats = lambda results: map(lambda result: float(result), results)

        raw_lines = response.text.split('\n')
        team_lines = filter(start_of_lines.match, raw_lines)[10:140]
        split_team_lines = map(split_line, team_lines)
        decimal_results = map(select_decimals, split_team_lines)
        return decimal_results
