import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-2])
sys.path.append(ROOT_PATH)

import numpy
from scipy.stats import norm

from models.bracket.bracket_team import BracketTeam

class Bracket:

    POS_TO_SEED = {
        0: 1,
        1: 16,
        2: 8,
        3: 9,
        4: 5,
        5: 12,
        6: 4,
        7: 13,
        8: 6,
        9: 11,
        10: 3,
        11: 14,
        12: 7,
        13: 10,
        14: 2,
        15: 15
    }

    def __init__(self):
        # Initialize instance variables
        self.teams = [[] for i in range(64)]
        self.field = {}
        self.bracket_source = "%s/constants/bracket2018.csv" % ROOT_PATH
        self.pure_points_source = (
            "%s/output/basketball/pure-points-week17.csv" % ROOT_PATH
        )
        self.composite_source = (
            "%s/output/basketball/composite-week17.csv" % ROOT_PATH
        )
        self.output_file = (
            "%s/output/basketball/bracket_projections.csv" % ROOT_PATH
        )

        # Read teams with bracket locations
        self.__read_bracket()
        # Read team ratings
        self.__read_ratings()

        # Build teams with location data
        self.__create_teams()

    def calculate(self):
        self.__calculate_first_round()
        # For each round
        for i in range(1, 7):
            self.__calculate_round(i)
        self.__write_results()


    def __calculate_all_matchups(self, start, round_num):
        bucket_size = 2 ** (round_num - 1)
        bucket1_teams, bucket2_teams = self.__collect_teams(start, bucket_size)
        # Calculate probability of each matchup
        for team1 in bucket1_teams:
            for team2 in bucket2_teams:
                matchup_probability = (
                    team1.probabilities[round_num - 1] *
                    team2.probabilities[round_num - 1]
                    )
                win_probabilities = self.__calculate_matchup(team1, team2)
                for team, prob in win_probabilities.items():
                    team.probabilities[round_num] += matchup_probability * prob
        bucket1_sum = 0
        for team in bucket1_teams:
            bucket1_sum += team.probabilities[round_num]
        bucket2_sum = 0
        for team in bucket2_teams:
            bucket2_sum += team.probabilities[round_num]
        assert(round(bucket1_sum + bucket2_sum, 4) == 1.0)

    def __calculate_first_round(self):
        for team_list in self.teams:
            if len(team_list) == 1:
                team_list[0].probabilities[0] = 1
            else:
                team1, team2 = team_list
                win_probabilities = self.__calculate_matchup(team1, team2)
                for key, val in win_probabilities.items():
                    key.probabilities[0] = val

    def __calculate_matchup(self, team1, team2):
        game_std_dev = numpy.mean([team1.std_dev, team2.std_dev])
        z_score = (team1.rating - team2.rating) / game_std_dev
        team1_win = norm.cdf(z_score)
        team2_win = 1 - team1_win
        return {team1: team1_win, team2: team2_win}

    def __calculate_round(self, round_num):
        # For each game slot
        bucket_size = 2 ** (round_num - 1)
        for i in range(0, 64, bucket_size * 2):
            self.__calculate_all_matchups(i, round_num)

    def __collect_teams(self, start, size):
        bucket1_teams = []
        bucket2_teams = []
        for j in range(start, start + size):
            bucket1_teams += self.teams[j]
        for k in range(start + size, start + size * 2):
            bucket2_teams += self.teams[k]
        return [bucket1_teams, bucket2_teams]

    def __create_teams(self):
        for team_name, attributes in self.field.items():
            idx = attributes['pos'] - 1
            new_team = BracketTeam(attributes)
            self.teams[idx].append(new_team)

    def __csv_string(self, team, idx):
        seed = self.POS_TO_SEED[idx % 16]
        region = self.__get_region(idx)
        probability_string = ','.join(map(lambda x: str(x), team.probabilities))
        return "%(seed)s,%(region)s,%(name)s,%(probs)s\n" % {
            'seed': seed,
            'region': region,
            'name': team.name,
            'probs': probability_string
        }

    def __get_region(self, idx):
        if idx < 16:
            return 'South'
        elif idx < 32:
            return 'West'
        elif idx < 48:
            return 'East'
        else:
            return 'Midwest'

    def __read_bracket(self):
        with open(self.bracket_source, 'r') as f:
            for line in f:
                pos, play_in, name = line.strip().split(',')
                pos = int(pos)
                play_in = int(play_in)
                self.field[name] = {'name': name, 'pos': pos}

    def __read_csv(self, source, attribute_name, idx):
        with open(source, 'r') as f:
            for line in f:
                values = line.strip().split(',')
                team_name = values[1]
                if team_name in self.field:
                    team_dict = self.field[team_name]
                    team_dict[attribute_name] = float(values[idx])

    def __read_ratings(self):
        self.__read_csv(self.pure_points_source, 'std_dev', -1)
        self.__read_csv(self.composite_source, 'rating', 2)

    def __write_results(self):
        with open(self.output_file, 'w+') as f:
            for idx, team_list in enumerate(self.teams):
                for team in team_list:
                    csv_string = self.__csv_string(team, idx)
                    f.write(csv_string)
