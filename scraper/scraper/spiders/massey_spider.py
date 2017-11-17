import scrapy
import re

class MasseySpider(scrapy.Spider):
    name = "massey_composite"

    def start_requests(self):
        url = 'https://www.masseyratings.com/cf/compare.htm'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'composite-%s.csv' % page
        teams_in_order = self._parse_teams_in_order(response)

        if len(teams_in_order) != 130:
            raise "Wrong number of team names fetched."
        team_metrics = self._parse_team_metrics(response)
        if len(team_metrics) != 130:
            raise "Wrong number of metrics fetched."

        with open(filename, 'wb') as f:
            idx = 0
            while idx < 130:
                team = teams_in_order[idx]
                metrics = map(lambda number: self._standardize_number_length(number), team_metrics[idx])
                metric_string = ','.join(metrics)
                text = metric_string + "," + str(idx + 1) + "," + team + "\n"
                f.write(text)
                idx += 1
        self.log('Saved file %s' % filename)

    def _parse_teams_in_order(self, response):
        return response.css("a[href^='../team.php']::text").extract()[0:-11]

    def _parse_team_metrics(self, response):
        # REGEX VARIABLES
        start_of_lines = re.compile(r' ')
        decimal = re.compile(r'.')

        # CALLBACKS
        split_line = lambda line: line.split(' ')
        select_decimals = lambda results: filter(decimal.search, results)[-3:]
        parse_to_floats = lambda results: map(lambda result: float(result), results)

        raw_lines = response.text.split('\n')
        print(raw_lines)
        team_lines = filter(start_of_lines.match, raw_lines)[10:140]
        split_team_lines = map(split_line, team_lines)
        decimal_results = map(select_decimals, split_team_lines)
        return decimal_results

    def _standardize_number_length(self, number):
        split_number = number.split('.')
        while len(split_number[0]) < 3:
            split_number[0] = ' ' + split_number[0]

        while len(split_number[1]) < 2:
            split_number[1] = split_number[1] + '0'

        return '.'.join(split_number)
