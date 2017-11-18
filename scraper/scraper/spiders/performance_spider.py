import scrapy

valid_ids = [
    2005, 2006, 333, 2026, 12, 9, 8, 2032, 349, 2, 2050, 239, 68, 103,
    189, 2084, 252, 25, 2117, 2429, 2132, 228, 324, 38, 36, 41, 150,
    151, 2199, 57, 2226, 2229, 52, 278, 61, 290, 2247, 59, 62, 248, 70,
    356, 84, 2294, 66, 2305, 2306, 2309, 96, 309, 2433, 2348, 97, 99,
    276, 120, 235, 2390, 193, 130, 127, 2393, 135, 344, 142, 2426, 152,
    158, 2440, 167, 166, 153, 249, 2459, 77, 87, 195, 194, 201, 197, 295,
    145, 2483, 204, 213, 221, 2509, 242, 164, 21, 23, 2567, 6, 2579, 58,
    2572, 24, 183, 2628, 218, 2633, 251, 245, 326, 2641, 2649, 2653, 2655,
    202, 5, 2116, 26, 113, 2439, 30, 2636, 254, 328, 2638, 238, 258, 259,
    154, 264, 265, 277, 98, 2711, 275, 2751
]

class PerformanceSpider(scrapy.Spider):
    name = "performance_ratings"

    def start_requests(self):
        base_url = 'https://www.espn.com/college-football/team/fpi/_/id/'
        for num in valid_ids:
            url = base_url + str(num)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = 'performance-ratings.csv'
        target_rows = response.css('tr.oddrow td:last-of-type::text').extract()[:2]
        ranks = map(lambda row: self._get_rank_from_row(row), target_rows)
        team = response.css("h3[class^='txt-ncf-']::text").extract()
        with open(filename, 'a+') as f:
            rank_text = ','.join(ranks)
            team_name = team[0]
            f.write(rank_text + ',' + team_name + '\n')

    def _get_rank_from_row(self, row):
        split = row.split(' ')
        return split[1][1:-1]
