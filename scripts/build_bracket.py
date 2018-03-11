import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from string_constants import RATINGS_P_BEST, RATINGS_P_BEST_WORSE
from settings import CALCULATE_P_OF_R

def build_bracket(teams):
    sorted_teams = sorted(list(teams), key=lambda team: team.composite_rating(), reverse=True)
    selected_teams = select_autobids(sorted_teams)

    search_idx = 0
    while len(selected_teams) < 68:
        team = sorted_teams[search_idx]
        if team not in selected_teams:
            selected_teams.append(team)
        search_idx += 1

    sorted_selected_teams = sorted(list(selected_teams), key=lambda team: team.composite_rating(), reverse=True)
    output_file = ROOT_PATH + "/output/basketball/bracketology.md"
    with open(output_file, 'w+') as f:
        for idx, team in enumerate(sorted_selected_teams):
            s_rank = idx + 1
            seed = idx // 4 + 1
            if s_rank > 48:
                seed = (idx - 2) // 4 + 1
            if s_rank >66:
                seed = 16
            f.write("%s %s %s -- %s\n" % (seed, s_rank, team.name, team.conference))

    conference_bids = {}
    for team in sorted_selected_teams:
        if team.conference in conference_bids:
            conference_bids[team.conference] += 1
        else:
            conference_bids[team.conference] = 1

    for key, value in conference_bids.items():
        print("%s -- %s" % (key, value))

    # SELECT BY P(Best)
    if CALCULATE_P_OF_R:
        selected_teams = select_autobids(sorted_teams)
        sorted_teams = sorted(list(sorted_teams), key=lambda team: team.ratings[RATINGS_P_BEST] + team.ratings[RATINGS_P_BEST_WORSE], reverse=True)
        search_idx = 0
        while len(selected_teams) < 68:
            team = sorted_teams[search_idx]
            if team not in selected_teams:
                selected_teams.append(team)
            search_idx += 1

        sorted_selected_teams = sorted(list(selected_teams), key=lambda team: team.composite_rating(), reverse=True)
        output_file = ROOT_PATH + "/output/basketball/bracketology-p-best.md"
        with open(output_file, 'w+') as f:
            for idx, team in enumerate(sorted_selected_teams):
                s_rank = idx + 1
                seed = idx // 4 + 1
                if s_rank > 48:
                    seed = (idx - 2) // 4 + 1
                if s_rank >66:
                    seed = 16
                f.write("%s %s %s -- %s\n" % (seed, s_rank, team.name, team.conference))

        conference_bids = {}
        for team in sorted_selected_teams:
            if team.conference in conference_bids:
                conference_bids[team.conference] += 1
            else:
                conference_bids[team.conference] = 1

        for key, value in conference_bids.items():
            print("%s -- %s" % (key, value))

def select_autobids(sorted_teams):
    autobids = []
    conferences_seen = set()
    for team in sorted_teams:
        if team.conference not in conferences_seen:
            autobids.append(team)
            conferences_seen.add(team.conference)
    return autobids
