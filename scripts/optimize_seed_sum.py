import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from models.bracket.bracket import Bracket

b = Bracket()
b.calculate()
sums_by_round = [2, 4, 11, 26, 67, 179]

flat_teams = []
for idx, team_list in enumerate(b.teams):
    for team in team_list:
        team.pos = idx
        team.seed = b.POS_TO_SEED[idx % 16]
        flat_teams.append(team)

selected = set()
seed_sum = 0

eligible_champions = []
for team in flat_teams:
    if team.seed >= sums_by_round[0]:
        eligible_champions.append(team)

sorted_teams = sorted(eligible_champions, key=lambda team: team.probabilities[-1], reverse=True)
pick = sorted_teams[0]
print(sorted_teams[0])
seed_sum += pick.seed
selected.add(pick)

eligible = []
needed = sums_by_round[1] - seed_sum
for team in flat_teams:
    if team not in selected:
        if team.seed >= needed:
            eligible.append(team)
sorted_teams = sorted(eligible, key=lambda team: team.probabilities[-2], reverse=True)
pick = sorted_teams[0]
print(sorted_teams[0])
seed_sum += pick.seed
selected.add(pick)


needed = sums_by_round[2] - seed_sum
print(needed)
buckets_left = [0, 1, 2, 3]
for team in selected:
    buckets_left.remove(team.pos // 16)
buckets = {}
for team in flat_teams:
    team_bucket = team.pos // 16
    if team_bucket in buckets_left:
        if team_bucket in buckets:
            buckets[team_bucket].append(team)
        else:
            buckets[team_bucket] = [team]
bucket1 = buckets[buckets_left[0]]
bucket2 = buckets[buckets_left[1]]
best_sum = 0
best_selection = None
for team1 in bucket1:
    for team2 in bucket2:
        if team1.seed + team2.seed >= needed:
            p_sum = team1.probabilities[-3] * team2.probabilities[-3]
            if p_sum > best_sum:
                best_sum = p_sum
                best_selection = [team1, team2]
print(best_selection[0].name, best_selection[0].probabilities[-3])
print(best_selection[1].name, best_selection[1].probabilities[-3])

for team in best_selection:
    seed_sum += team.seed
    selected.add(team)
print(seed_sum)
print(selected)


needed = sums_by_round[3] - seed_sum
print(needed)
buckets_left = list(range(8))
for team in selected:
    buckets_left.remove(team.pos // 8)
buckets = {}
for team in flat_teams:
    team_bucket = team.pos // 8
    if team_bucket in buckets_left:
        if team_bucket in buckets:
            buckets[team_bucket].append(team)
        else:
            buckets[team_bucket] = [team]

bucket1 = buckets[buckets_left[0]]
bucket2 = buckets[buckets_left[1]]
bucket3 = buckets[buckets_left[2]]
bucket4 = buckets[buckets_left[3]]
best_sum = 0
best_selection = None
for team1 in bucket1:
    for team2 in bucket2:
        for team3 in bucket3:
            for team4 in bucket4:
                seeds = list(map(lambda team: team.seed, [team1, team2, team3, team4]))
                if sum(seeds) >= needed:
                    p_win = list(map(lambda team: team.probabilities[-4], [team1, team2, team3, team4]))
                    product = 1
                    for x in p_win:
                        product = x * product
                    if product > best_sum:
                        best_sum = product
                        best_selection = [team1, team2, team3, team4]
print(best_selection[0].name, best_selection[0].probabilities[-4])
print(best_selection[1].name, best_selection[1].probabilities[-4])
print(best_selection[2].name, best_selection[2].probabilities[-4])
print(best_selection[3].name, best_selection[3].probabilities[-4])

for team in best_selection:
    seed_sum += team.seed
    selected.add(team)

needed = sums_by_round[4] - seed_sum
print(needed)
buckets_left = list(range(16))
for team in selected:
    buckets_left.remove(team.pos // 4)
buckets = {}
for team in flat_teams:
    team_bucket = team.pos // 4
    if team_bucket in buckets_left:
        if team_bucket in buckets:
            buckets[team_bucket].append(team)
        else:
            buckets[team_bucket] = [team]

bucket1 = buckets[buckets_left[0]]
bucket2 = buckets[buckets_left[1]]
bucket3 = buckets[buckets_left[2]]
bucket4 = buckets[buckets_left[3]]
bucket5 = buckets[buckets_left[4]]
bucket6 = buckets[buckets_left[5]]
bucket7 = buckets[buckets_left[6]]
bucket8 = buckets[buckets_left[7]]
best_sum = 0
best_selection = None
for team1 in bucket1:
    for team2 in bucket2:
        for team3 in bucket3:
            for team4 in bucket4:
                for team5 in bucket5:
                    for team6 in bucket6:
                        for team7 in bucket7:
                            for team8 in bucket8:
                                teams = [team1, team2, team3, team4, team5, team6, team7, team8]
                                seeds = list(map(lambda team: team.seed, teams))
                                if sum(seeds) >= needed:
                                    p_win = list(map(lambda team: team.probabilities[-5], teams))
                                    product = 1
                                    for x in p_win:
                                        product = x * product
                                    if product > best_sum:
                                        best_sum = product
                                        best_selection = teams
for team in best_selection:
    print(team.name, team.probabilities[-5])
    seed_sum += team.seed
    selected.add(team)

needed = sums_by_round[5] - seed_sum
print(needed)
buckets_left = list(range(32))
for team in selected:
    buckets_left.remove(team.pos // 2)
buckets = {}
for team in flat_teams:
    team_bucket = team.pos // 2
    if team_bucket in buckets_left:
        if team_bucket in buckets:
            buckets[team_bucket].append(team)
        else:
            buckets[team_bucket] = [team]

bucket1 = buckets[buckets_left[0]]
bucket2 = buckets[buckets_left[1]]
bucket3 = buckets[buckets_left[2]]
bucket4 = buckets[buckets_left[3]]
bucket5 = buckets[buckets_left[4]]
bucket6 = buckets[buckets_left[5]]
bucket7 = buckets[buckets_left[6]]
bucket8 = buckets[buckets_left[7]]
bucket9 = buckets[buckets_left[8]]
bucket10 = buckets[buckets_left[9]]
bucket11 = buckets[buckets_left[10]]
bucket12 = buckets[buckets_left[11]]
bucket13 = buckets[buckets_left[12]]
bucket14 = buckets[buckets_left[13]]
bucket15 = buckets[buckets_left[14]]
bucket16 = buckets[buckets_left[15]]
best_sum = 0
best_selection = None
for team1 in bucket1:
    for team2 in bucket2:
        for team3 in bucket3:
            for team4 in bucket4:
                for team5 in bucket5:
                    for team6 in bucket6:
                        for team7 in bucket7:
                            for team8 in bucket8:
                                for team9 in bucket9:
                                    for team10 in bucket10:
                                        for team11 in bucket11:
                                            for team12 in bucket12:
                                                for team13 in bucket13:
                                                    for team14 in bucket14:
                                                        for team15 in bucket15:
                                                            for team16 in bucket16:
                                                                teams = [team1, team2, team3, team4, team5, team6, team7, team8, team9, team10, team11, team12, team13, team14, team15, team16]
                                                                seeds = list(map(lambda team: team.seed, teams))
                                                                if sum(seeds) >= needed:
                                                                    p_win = list(map(lambda team: team.probabilities[-6], teams))
                                                                    product = 1
                                                                    for x in p_win:
                                                                        product = x * product
                                                                    if product > best_sum:
                                                                        best_sum = product
                                                                        best_selection = teams
for team in best_selection:
    print(team.name, team.probabilities[-6])
    seed_sum += team.seed
    selected.add(team)
