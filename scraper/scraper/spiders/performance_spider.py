import scrapy
import time
import os, sys
local_path = os.path.dirname(__file__)
root_path = '/'.join(local_path.split('/')[:-3])
sys.path.append(root_path)
from settings import CURRENT_WEEK

# Spider settings
wait_between_calls = True
seconds_between_calls = 0.5

id_source = "%s/constants/performance_ids.txt" % root_path

class MothershipSpider(scrapy.Spider):
    def run_requests(self, callback):
        base_url = 'https://www.espn.com/college-football/team/fpi/_/id/'
        with open(id_source) as f:
            for line in f:
                url = base_url + str(line.strip())
                yield scrapy.Request(url=url, callback=callback)
                if wait_between_calls:
                    time.sleep(seconds_between_calls)


class PerformanceSpider(MothershipSpider):
    name = "performance_ratings"
    write_file = '%s/output/performance-ratings-week%s.csv' % (root_path, CURRENT_WEEK)

    def start_requests(self):
        requests = self.run_requests(self.parse)
        for request in requests:
            yield request

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

class ScheduleSpider(MothershipSpider):
    name = "schedules"
    wirte_directory = '%s/output/schedules' % root_path

    def start_requests(self):
        self.run_requests(self.parse)

    def parse(self, response):
        pass
