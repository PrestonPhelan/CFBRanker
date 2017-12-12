import os
import numpy
import sys

from scipy.stats import norm
from statistics import median

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from processing.builders import build_markdown_row, build_markdown_barrier
from processing.game_helpers import calc_product, choose
from processing.options_util import import_options
from settings import NUM_SIMS, COMPOSITE_GENERIC_PATH
from string_constants import *

class SORCalculator:
    def __init__(self, team_list, sport, overall_sd):
        self.team_list = team_list
        self.overall_sd = overall_sd
        self.sport = sport
        self.combos = {}

        options = import_options(sport)
        self.home_field_advantage = options[OPTIONS_HOME_FIELD_ADVANTAGE]
        self.current_week = options[OPTIONS_CURRENT_WEEK]
        composite_path = COMPOSITE_GENERIC_PATH % (ROOT_PATH, self.sport, self.current_week)
        self.output_csv = composite_path + ".csv"
        self.output_md = composite_path + ".md"

        self.calculate_sor_metrics()

    def estimate_rating_standard_deviation(self):
        if self.sport == SPORT_FOOTBALL:
            filtered_teams = self.filter_for_fbs()
        else:
            filtered_teams = self.team_list

        ratings = list(map(lambda team: team.ratings[RATINGS_PURE_POINTS], filtered_teams))
        self.ratings_sd = numpy.std(ratings, ddof=1)
        return self.ratings_sd

    def filter_for_fbs(self):
        return list(filter(lambda team: team.fb_level == "FBS", self.team_list))

    def filtered_average(self):
        filtered_teams = self.filter_for_fbs()
        return sum(list(map(lambda team: team.ratings[RATINGS_PURE_POINTS], filtered_teams))) / len(filtered_teams)

    def generate_rating_probabilities(self):
        self.estimate_rating_standard_deviation()
        rating_probabilities = {}
        for i in range(101):
            rating_probabilities[i] = norm.pdf(i, 50, self.ratings_sd)
        self.rating_probabilities = rating_probabilities
        return self.rating_probabilities

    def calculate_performance_probabilities(self, team, rating):
        win_probs = [game.calculate_win_probability(rating, self.home_field_advantage, self.overall_sd) for game in team.games]
        sum_of_probs = 0
        for current_loss_counter in range(team.losses):
            sum_of_probs += self.calculate_schedule_probability(win_probs, current_loss_counter)
        p_better = sum_of_probs
        p_equal = self.calculate_schedule_probability(win_probs, team.losses)
        p_worse = 1 - (p_better + p_equal)
        return [p_better, p_equal, p_worse]

    def calculate_schedule_probability(self, win_probs, losses):
        if losses == 0:
            return calc_product(win_probs)
        num_games = len(win_probs)
        combinations = None
        lookup_string = '%s-%s' % (num_games, losses)
        if lookup_string in self.combos:
            combinations = self.combos[lookup_string]
        else:
            combinations = choose(num_games, losses)
            self.combos[lookup_string] = combinations
        total_prob = 0
        for loss_list in combinations:
            total_prob += calc_product(win_probs, loss_list)
        return total_prob

    def estimate_best_rating(self):
        if self.sport == SPORT_FOOTBALL:
            # Originally did 1.0 / (NUM_TEAMS * 2) to center in bucket
            # But this led to overestimate based on simulating max values
            # 1.75 gives better estimate
            est_best_rating = norm.ppf(1 - (1.0 / (len(self.team_list) * 1.75)), self.filtered_average(), self.ratings_sd)
        else:
            est_best_rating = norm.ppf(1 - (1.0 / (len(self.team_list) * 1.75)), 50, self.ratings_sd)
        return est_best_rating

    def sim_estimate_of_best_rating(self):
        if self.sport == SPORT_FOOTBALL:
            mu = self.filtered_average()
        else:
            mu = 50
        sigma = self.ratings_sd
        maximums = []
        for i in range(NUM_SIMS):
            ratings = [numpy.random.normal(mu, sigma) for j in range(len(self.team_list))]
            maximums.append(max(ratings))
            if (i + 1) % 100 == 0:
                print("Finished sim %s" % str(i + 1))
        print ("Median was %s" % str(median(maximums)))
        return sum(maximums) / NUM_SIMS

    def calculate_p_record_metrics(self):
        est_best_rating = self.estimate_best_rating()

        for idx, team in enumerate(self.team_list):
            p_better, p_equal, p_worse = self.calculate_performance_probabilities(team, est_best_rating)
            team.ratings[RATINGS_P_BEST] = p_worse + 0.5 * p_equal
            team.ratings[RATINGS_P_BEST_WORSE] = p_worse
            if (idx + 1) % 25 == 0:
                print("%s of P(r) calculations done." % str(idx + 1))
        return True

    def ranked_teams(self):
        return sorted(self.team_list, key=lambda team: team.composite_rating(), reverse=True)

    def write_to_csv(self):
        with open(self.output_csv, 'w+') as f:
            for idx, team in enumerate(self.ranked_teams()):
                columns = self.formatted_ratings(team)
                columns.insert(0, team.name)
                columns.insert(0, idx + 1)
                f.write(','.join([str(item) for item in columns]) + "\n")

    def write_to_md(self):
        with open(self.output_md, 'w+') as f:
            column_names = [
                'Rnk', 'Team', 'W-L', 'Conf', 'Rating', 'Rating-PP',
                'Rating-PP-Adj', 'Rating-SOR-WA', 'Rating-SOR-MLE',
                'P-Val Best', 'P-Val Best Worse'
            ]

            if self.sport == SPORT_FOOTBALL:
                column_names.insert(4, 'Lvl')
                
            f.write(build_markdown_row(column_names))
            f.write(build_markdown_barrier(column_names))

            for idx, team in enumerate(self.ranked_teams()):

                if self.sport == SPORT_FOOTBALL:
                    conference_flair = team.conference.fb_flair
                elif self.sport == SPORT_BASKETBALL:
                    conference_flair = team.conference.bb_flair
                else:
                    raise "Unexpected/undefined sport %s" % sport

                static_columns = [
                    idx + 1, team.get_flair_with_name(),
                    team.get_record(), conference_flair]

                if self.sport == SPORT_FOOTBALL:
                    if team.fb_level == 'FBS':
                        level_flair = FBS_FLAIR
                    elif team.fb_level == 'FCS':
                        level_flair = FCS_FLAIR
                    else:
                        raise "Unexpected level %s" % team.fb_level
                    static_columns.append(level_flair)

                rating_columns = self.formatted_ratings(team)

                columns = static_columns + rating_columns
                f.write(build_markdown_row(columns))


    def formatted_ratings(self, team):
        p_best_for_print = team.ratings[RATINGS_P_BEST] * 100
        p_best_worse_for_print = team.ratings[RATINGS_P_BEST_WORSE] * 100
        columns = [
            team.composite_rating(), team.ratings[RATINGS_PURE_POINTS],
            team.ratings[RATINGS_PURE_POINTS_ADJUSTED], team.ratings[RATINGS_SOR_WA],
            team.ratings[RATINGS_SOR_MLE], p_best_for_print, p_best_worse_for_print]
        columns = [str(round(item, 2)) for item in columns]
        return columns

    def calculate_sor_metrics(self):
        self.generate_rating_probabilities()

        for idx, team in enumerate(self.team_list):
            team.calculate_and_add_sor_metrics(self.rating_probabilities, self.home_field_advantage, self.overall_sd)
            if (idx + 1) % 25 == 0:
                print("%s of %s SOR complete" % (idx + 1, len(self.team_list)))

        self.calculate_p_record_metrics()

        self.write_to_csv()
        self.write_to_md()

        # for idx, team in enumerate(ranked_teams):
        #
        #
        #     print(" ".join(columns))
