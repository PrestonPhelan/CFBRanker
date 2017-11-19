import scrapy
import os, sys
local_path = os.path.dirname(__file__)
root_path = '/'.join(local_path.split('/')[:-3])
sys.path.append(root_path)
from settings import CURRENT_WEEK

class StandingsSpider(scrapy.Spider):
    name = "standings"

    def start_requests(self):
        url = 'https://www.ncaa.com/standings/football/fbs'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = '%s/output/standings-week%s.csv' % (root_path, CURRENT_WEEK)
        records = self._parse_records(response)

        with open(filename, 'wb') as f:
            for team, record in records.items():
                text = "%s,%s\n" % (team, record)
                f.write(text)

    def _parse_records(self, response):
        teams = response.css("td.ncaa-standing-conference-team a span::text").extract()
        if len(teams) != 130:
            raise "Wrong number of teams found"
        records = response.css("td.conference-boundary::text").extract()
        records = filter(lambda text: text != "W-L", records)
        if len(records) != 130:
            raise "Wrong number of records"
        result = {}
        for idx, team in enumerate(teams):
            result[team] = records[idx]

        return result
