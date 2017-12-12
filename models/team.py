import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from models.conference import Conference
from models.game import Game
from models.helpers.constructor import build_instance, build_set_from_file
from models.helpers.read_schedule import read_schedule
from processing.builders import build_filename_format
from string_constants import *
from settings import SCHEDULE_GENERIC_PATH, TEAM_PATH

class Team:
    TEAM_SOURCE = TEAM_PATH % ROOT_PATH
    SOURCE_COLUMNS = [
        'id', 'name', 'scrape_id', 'fb_scrape_name', 'bb_scrape_name',
        'schedule_name', 'flair', FB_LEVEL, 'fb_conference_id',
        'bb_conference_id'
    ]

    @classmethod
    def build_all(cls, football=False):
        conferences = Conference.build_all()
        teams = build_set_from_file(
            cls,
            cls.TEAM_SOURCE,
            football=football,
            fb_filter_idx=cls.SOURCE_COLUMNS.index(FB_LEVEL))
        for team in teams.values():
            if football:
                if team.fb_conference_id is None:
                    print(team.name)
                team.conference = conferences[team.fb_conference_id]
            else:
                team.conference = conferences[team.bb_conference_id]
        return teams

    @classmethod
    def build_all_by_schedule_name(cls, teams_by_id=None, football=False):
        if not teams_by_id:
            teams_by_id = Team.build_all(football=football)
        teams_by_schedule_name = {}
        for team in teams_by_id.values():
            teams_by_schedule_name[team.schedule_name] = team
        return teams_by_schedule_name

    @classmethod
    def build_all_with_games(cls, sport):
        SCHEDULE_PATH = SCHEDULE_GENERIC_PATH % (ROOT_PATH, sport)
        football = sport == SPORT_FOOTBALL
        teams_by_id = Team.build_all(football=football)
        teams_by_schedule_name = Team.build_all_by_schedule_name(teams_by_id=teams_by_id, football=football)
        teams = teams_by_id.values()
        for team in teams:
            team.add_all_games(SCHEDULE_PATH, teams_by_schedule_name)
        return teams_by_id

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

    def __init__(self, data):
        build_instance(self, self.SOURCE_COLUMNS, data)
        self.conference = None
        self.games = []
        self.ratings = {}
        self.wins = 0
        self.losses = 0

    def __str__(self):
        return self.name

    def add_all_games(self, schedule_path, teams_by_schedule_name):
        filename_format_name = build_filename_format(self.name)
        schedule_source = schedule_path + filename_format_name + ".csv"
        with open(schedule_source, 'r') as read_file:
            for line in read_file:
                game_data = read_schedule(line, teams_by_schedule_name)
                if game_data:
                    if game_data[GAME_RESULT] == "W":
                        self.wins += 1
                    elif game_data[GAME_RESULT] == "L":
                        self.losses += 1
                    else:
                        raise "Unexpected result %s" % game_data[GAME_RESULT]

                    self.games.append(Game(game_data))

    def calculate_and_add_sor_metrics(self, rating_probabilities, home_field_advantage, overall_std):
        max_p_rating = 0
        max_p = 0
        total_p = 0
        total_rat = 0
        for i in range(101):
            p_rating = rating_probabilities[i]
            p_result = self.calculate_actual_results_probability(i, home_field_advantage, overall_std)
            p_of_i = p_rating * p_result
            total_p += p_of_i
            total_rat += p_of_i * i
            if p_of_i > max_p:
                max_p = p_of_i
                max_p_rating = i
        self.ratings[RATINGS_SOR_WA] = total_rat / total_p
        self.ratings[RATINGS_SOR_MLE] = max_p_rating

    def calculate_actual_results_probability(self, rating, home_field_advantage, overall_std):
        p = 1
        for game in self.games:
            p_win = game.calculate_win_probability(rating, home_field_advantage, overall_std)
            if game.result == "W":
                p = p * p_win
            elif game.result == "L":
                p = p * (1.0 - p_win)
            else:
                raise "Unexpected result %s" % game.result
        return p

    def get_flair_with_name(self):
        return " ".join([self.flair, self.name])

    def get_record(self):
        return "%s-%s" % (self.wins, self.losses)

    def composite_rating(self):
        metrics = [
            self.ratings[RATINGS_PURE_POINTS], self.ratings[RATINGS_PURE_POINTS_ADJUSTED],
            self.ratings[RATINGS_SOR_WA], self.ratings[RATINGS_SOR_MLE]]
        return sum(metrics) / float(len(metrics))

    # def set_power_mean(self, rating):
    #     self.power_mean = rating
    #     if self.strength_of_record and self.game_control:
    #         self.set_combined_rating()
    #
    # def set_performance_metrics(self, strength_of_record, game_control):
    #     self.strength_of_record = strength_of_record
    #     self.game_control = game_control
    #     if self.power_mean is not None:
    #         self.set_combined_rating()
    #
    # def get_combined_rating(self):
    #     if self.combined_rating is None:
    #         self.set_combined_rating()
    #     return self.combined_rating
    #
    # def set_combined_rating(self):
    #     self.combined_rating = self.calculate_combined_rating()
    #
    # def calculate_combined_rating(self):
    #     rating = 0.5 * (self.calculate_power_rating() + self.calculate_performance_rating())
    #     return rating
    #
    # def calculate_power_rating(self):
    #     return self.power_mean
    #
    # def calculate_performance_rating(self):
    #     return (self.strength_of_record * 2 + self.game_control) / 3.0
    #
    # def get_reddit_rating(self):
    #     if self.reddit_rating is None:
    #         self.calculate_reddit_rating()
    #     return self.reddit_rating
    #
    # def calculate_reddit_rating(self):
    #     self.reddit_rating = round(100*(130-self.get_combined_rating())/129, 1)
    #
    # def composite_avg_by(self, rank_set):
    #     return (self.ratings['bucket_estimates'][rank_set] + self.ratings['pure_points'] + self.ratings['sor_wa']) / 3.0
