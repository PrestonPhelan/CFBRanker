import scrapy

class MasseySpider(scrapy.Spider):
    name = "massey_composite"

    def start_requests(self):
        url = 'https://www.masseyratings.com/cf/compare.htm'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'composite-%s.txt' % page
        teams_in_order = response.css("a[href^='../team.php']::text").extract()[0:-11]
        print teams_in_order
        with open(filename, 'wb') as f:
            rank = 1
            for team in teams_in_order:
                text = str(rank) + " " + team + "\n"
                f.write(text)
                rank += 1
        self.log('Saved file %s' % filename)
