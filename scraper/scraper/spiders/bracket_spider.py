import os
import sys
import scrapy

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-3])
sys.path.append(ROOT_PATH)

class MothershipSpider(scrapy.Spider):
    name = "mothership_bracket"

    TRANSLATIONS = {
        'UVA': 'Virginia',
        'UNC': 'North Carolina',
        'OSU': 'Ohio State',
        'URI': 'Rhode Island',
        'SF Austin': 'Stephen F. Austin',
        'UNCG': 'UNC Greensboro',
        'CSU Fullerton': 'Cal State Fullerton',
        'Penn': 'Pennsylvania'
    }

    def start_requests(self):
        yield scrapy.Request(url='http://games.espn.com/tournament-challenge-bracket/2018/en/whopickedwhom', callback=self.parse)

    def parse(self, response):
        team_pick_freq = {}
        rows = response.css('tbody tr')
        for row in rows:
            items = row.css('td')
            for idx, item in enumerate(items):
                team = item.css('.teamName::text').extract()[0]
                # print(team)
                rate = item.css('.percentage::text').extract()[0]
                if team not in team_pick_freq:
                    team_pick_freq[team] = [None] * 6
                team_pick_freq[team][idx] = rate
                print(team, rate)
        with open('%s/output/basketball/pick_frequency/mothership.csv' % ROOT_PATH, 'w+') as f:
            for key, val in team_pick_freq.items():
                if key in self.TRANSLATIONS:
                    name = self.TRANSLATIONS[key]
                else:
                    name = key
                f.write(name + ',' + ','.join(val) + '\n')
                print(key, val)
