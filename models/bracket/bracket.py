import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-2])
sys.path.append(ROOT_PATH)

import numpy
from scipy.stats import norm

from bracket_team import BracketTeam

class Bracket:

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

        # Read teams with bracket locations
        self.__read_bracket()
        # Read team ratings
        self.__read_ratings()

        # Build teams with location data
        self.__create_teams()

    def calculate(self):
        self.__calculate_first_round()
        # For each round
            # Calculate probability of each matchup
            # Calculate win probailities of each matchup
            # Sum each team's advance rate
        pass

    def __calculate_first_round(self):
        for team_list in self.teams:
            if len(team_list) == 1:
                team_list[0].probabilities[0] = 1
            else:
                team1, team2 = team_list
                win_probabilities = self.__calculate_matchup(team1, team2)
                for key, val in win_probabilities.items():
                    key.probabilities[0] = val
                    probability = round(val * 100, 2)
                    p_string = ": %s" % probability
                    print(key.name +  p_string)

    def __calculate_matchup(self, team1, team2):
        game_std_dev = numpy.mean([team1.std_dev, team2.std_dev])
        z_score = (team1.rating - team2.rating) / game_std_dev
        team1_win = norm.cdf(z_score)
        team2_win = 1 - team1_win
        return {team1: team1_win, team2: team2_win}

    def __create_teams(self):
        for team_name, attributes in self.field.items():
            idx = attributes['pos'] - 1
            new_team = BracketTeam(attributes)
            self.teams[idx].append(new_team)

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
