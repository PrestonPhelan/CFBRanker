import scrapy
import time
import datetime
import os, sys
local_path = os.path.dirname(__file__)
root_path = '/'.join(local_path.split('/')[:-3])
sys.path.append(root_path)
import settings

# Spider settings
wait_between_calls = True
seconds_between_calls = 0.5

id_source = "../constants/performance_ids.txt"

class PerformanceSpider(scrapy.Spider):
    name = "performance_ratings"
    write_file = 'performance-ratings-week%s.csv' % settings.CURRENT_WEEK

    def start_requests(self):
        base_url = 'https://www.espn.com/college-football/team/fpi/_/id/'
        with open(id_source) as f:
            for line in f:
                url = base_url + str(line.strip())
                yield scrapy.Request(url=url, callback=self.parse)
                if wait_between_calls:
                    time.sleep(seconds_between_calls)

    def parse(self, response):
        target_rows = response.css('tr.oddrow td:last-of-type::text').extract()[:2]
        ranks = map(lambda row: self._get_rank_from_row(row), target_rows)
        team = response.css("h3[class^='txt-ncf-']::text").extract()
        team_name = team[0]
        # data = [SOR, GC, Team Name]
        data = ranks + [team_name]
        with open(self.write_file, 'a+') as f:
            f.write(','.join(data) + '\n')

    def _get_rank_from_row(self, row):
        split = row.split(' ')
        return split[1][1:-1]
