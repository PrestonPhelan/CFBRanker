import scrapy

class StandingsSpider(scrapy.Spider):
    name = "standings"

    def start_requests(self):
        url = 'https://www.ncaa.com/standings/football/fbs'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = 'standings.csv'
        records = self._parse_records(response)

        with open(filename, 'wb') as f:
            for key, val in records.items():
                f.write(key + "," + val + "\n")

    def _parse_records(self, response):
        teams = response.css("td.ncaa-standing-conference-team a span::text").extract()
        # if len(teams) != 130:
        #     raise "Wrong number of teams found"
        records = response.css("td.conference-boundary::text").extract()
        records = filter(lambda text: text != "W-L", records)
        # if len(records) != 130:
        #     raise "Wrong number of records"

        result = {}
        for idx, team in enumerate(teams):
            result[team] = records[idx]

        return result
