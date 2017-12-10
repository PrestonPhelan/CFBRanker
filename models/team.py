import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-3])
sys.path.append(ROOT_PATH)

from models.helpers.constructor import build_instance

class Team:
    SOURCE_COLUMNS = [
        'name', 'scrape_id', 'fb_scrape_name', 'bb_scrape_name',
        'schedule_name', 'flair', 'fb_level', 'fb_conference_id',
        'bb_conference_id'
    ]

    @classmethod
    def build_teams_from_file(cls, sourcefile):
        teams = {}
        with open(sourcefile) as f:
            for line in f:
                name, conference = line.strip().split(',')
                teams[name] = Team(name, conference)
        return teams

    @classmethod
    def set_last_week(cls, last_week_data, teams):
        top_25 = last_week_data[:25]
        result = {}
        for line in top_25:
            columns = line.strip().split(',')
            rank = columns[0]
            team_name = columns[-1]
            result[team_name] = rank
            team = teams[team_name]
            team.last_week = rank
        return result

    def __init__(self, name, conference):
        self.name = name
        self.conference = conference
        self.record = None
        self.games = set()
        self.id = None
        self.ratings = {}
        self.rankings = {}

        self.power_mean = None
        self.strength_of_record = None
        self.game_control = None
        self.combined_rating = None
        self.reddit_rating = None
        self.last_week = "NR"
        self.flair_string = None

        self.sim_championships = 0.0
        self.wins_this_sim = 0

    def __str__(self):
        return self.name
    #     return ", ".join([self.name, str(self.get_combined_rating())[:5]])

    def set_power_mean(self, rating):
        self.power_mean = rating
        if self.strength_of_record and self.game_control:
            self.set_combined_rating()

    def set_performance_metrics(self, strength_of_record, game_control):
        self.strength_of_record = strength_of_record
        self.game_control = game_control
        if self.power_mean is not None:
            self.set_combined_rating()

    def get_combined_rating(self):
        if self.combined_rating is None:
            self.set_combined_rating()
        return self.combined_rating

    def set_combined_rating(self):
        self.combined_rating = self.calculate_combined_rating()

    def calculate_combined_rating(self):
        rating = 0.5 * (self.calculate_power_rating() + self.calculate_performance_rating())
        return rating

    def calculate_power_rating(self):
        return self.power_mean

    def calculate_performance_rating(self):
        return (self.strength_of_record * 2 + self.game_control) / 3.0

    def get_reddit_rating(self):
        if self.reddit_rating is None:
            self.calculate_reddit_rating()
        return self.reddit_rating

    def calculate_reddit_rating(self):
        self.reddit_rating = round(100*(130-self.get_combined_rating())/129, 1)

    def get_flair_string(self, translations):
        if self.flair_string is None:
            if self.name in translations:
                self.flair_string = translations[self.name]
            else:
                combo_string = "".join(self.name.split(" ")).lower()
                self.flair_string = "[%s](#f/%s) %s" % (self.name, combo_string, self.name)
        return self.flair_string

    def composite_avg_by(self, rank_set):
        return (self.ratings['bucket_estimates'][rank_set] + self.ratings['pure_points'] + self.ratings['sor_wa']) / 3.0
