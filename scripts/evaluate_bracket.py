import os
import sys

LOCAL_PATH = os.path.dirname(__file__)
ROOT_PATH = '/'.join(LOCAL_PATH.split('/')[:-1])
sys.path.append(ROOT_PATH)

from numpy import random

from models.bracket.bracket import Bracket

SCORING_SYSTEM = [1, 2, 4, 8, 16, 32]
NUM_OPPONENTS = 10
NUM_SIMS = 25000
AUTO_RUN = True
CONF_INT = 0.005
PLAY_INS = {
    'North Carolina Central': 'NCC/TS',
    'Texas Southern': 'NCC/TS',
    'LIU Brooklyn': 'LIU/RAD',
    'Radford': 'LIU/RAD',
    'St. Bonaventure': 'BON/LA',
    'UCLA': 'BON/LA',
    'Arizona State': 'ASU/SY',
    'Syracuse': 'ASU/SY'
}


def build_selections(bracket, freqs):
    selections = []
    # For each game
    for i in range(32):
        team1_list = bracket.teams[2 * i]
        team1_key = fetch_key(team1_list)
        team1_raw_freq = freqs[team1_key][0]

        team2_list = bracket.teams[2 * i + 1]
        team2_key = fetch_key(team2_list)
        team2_raw_freq = freqs[team2_key][0]

        # See matchup
        team1_freq = team1_raw_freq / (team1_raw_freq + team2_raw_freq)

        # Select between the two options
        rand_x = random.random()
        if rand_x <= team1_freq:
            selections.append(team1_key)
        else:
            selections.append(team2_key)

    for i in range(31):
        if i < 16:
            round_idx = 1
        if i < 24:
            round_idx = 2
        if i < 28:
            round_idx = 3
        if i < 30:
            round_idx = 4
        else:
            round_idx = 5
        team1_key = selections[2 * i]
        team1_raw_freq = freqs[team1_key][round_idx]
        team2_key = selections[2 * i + 1]
        team2_raw_freq = freqs[team2_key][round_idx]

        team1_freq = team1_raw_freq / (team1_raw_freq + team2_raw_freq)

        rand_x = random.random()
        if rand_x <= team1_freq:
            selections.append(team1_key)
        else:
            selections.append(team2_key)

    return selections


def fetch_key(team):
    if len(team) == 1:
        return team[0].name
    else:
        return PLAY_INS[team[0].name]

def round_by_index(i):
    if i < 32:
        return 0
    elif i < 48:
        return 1
    elif i < 56:
        return 2
    elif i < 60:
        return 3
    elif i < 62:
        return 4
    else:
        return 5

def score(pick_list, results):
    score = 0
    for idx, pick in enumerate(pick_list):
        winning_team = results[idx]
        if winning_team in PLAY_INS:
            actual_winner = PLAY_INS[winning_team]
        else:
            actual_winner = winning_team.name
        if pick == actual_winner:
            score += SCORING_SYSTEM[round_by_index(idx)]
    return score

def str_freq_to_float(x):
    num_chars = x[:-1]
    num = float(num_chars)
    return num

def bucket_winner_from_idx(x):
    if x < 32:
        return 32 + (x // 2)
    elif x < 48:
        return 48 + ((x - 32) // 2)
    elif x < 56:
        return 56 + ((x - 48) // 2)
    elif x < 60:
        return 60 + ((x - 56) // 2)
    elif x < 62:
        return 62
    else:
        return None

def prev_bucket_start_from_idx(x):
    if x < 32:
        return (x * 2)
    elif x < 48:
        return (x - 32) * 2
    elif x < 56:
        return 32 + (x - 48) * 2
    elif x < 60:
        return 48 + (x - 56) * 2
    elif x < 62:
        return 56 + (x - 60) * 2
    else:
        return 60

def pickable(new_pick, old_pick, idx, favorites, probs, freq, skip_list):
    if favorites[idx] == new_pick:
        return True
    if new_pick in skip_list and i in skip_list[new_pick]:
        print("Skipping %s due to past performance" % new_pick)
        return False
    round_num = round_by_index(idx)
    new_pick_p = probs[new_pick][round_num]
    # if new_pick_p < 1 / (NUM_OPPONENTS + 1):
    #     return False
    old_pick_p = probs[old_pick][round_num]
    new_pick_freq = freq[new_pick][round_num]
    old_pick_freq = freq[old_pick][round_num]
    if (new_pick_p / new_pick_freq) > (old_pick_p / old_pick_freq):
        return True
    else:
        return False

def get_next_base(results_list, runs_completed, top_winrate):
    for result in results_list:
        if tuple(result['selections']) in runs_completed:
            continue
        elif result['winrate'] > top_winrate - CONF_INT:
            return result['selections']
        else:
            return None

# Read my picks
favorites_location = "./constants/favorites.txt"
favorites = []
with open(favorites_location, 'r') as f:
    for line in f:
        favorites.append(line.strip())

selection_location = "./constants/my_picks.txt"
selections = []
with open(selection_location, 'r') as f:
    for line in f:
        selections.append(line.strip())

# Read pick frequency
mothership_freq_location = "./output/basketball/pick_frequency/mothership.csv"
selection_freq = {}
with open(mothership_freq_location, 'r') as f:
    for line in f:
        attributes = line.strip().split(',')
        name = attributes[0]
        str_freqs = attributes[1:]
        float_freqs = list(map(str_freq_to_float, str_freqs))
        selection_freq[name] = float_freqs

b = Bracket()
b.calculate()
probs_by_name = {}
original_pos = []
for team_list in b.teams:
    name_key = fetch_key(team_list)
    original_pos.append(name_key)
    p_sums = [0] * 6
    for team in team_list:
        for idx, p in enumerate(team.probabilities):
            if idx == 0:
                continue
            p_sums[idx - 1] += p
    probs_by_name[name_key] = p_sums

performance = []

# assert(pickable('Virginia', 'Duke', 62, favorites, probs_by_name, selection_freq) is True)
# assert(pickable('Villanova', 'Duke', 62, favorites, probs_by_name, selection_freq) is True)
# assert(pickable('Virginia', 'Purdue', 62, favorites, probs_by_name, selection_freq) is True)
# assert(pickable('Villanova', 'Virginia', 62, favorites, probs_by_name, selection_freq) is False)
# assert(pickable('Purdue', 'Virginia', 62, favorites, probs_by_name, selection_freq) is False)
# assert(pickable('Duke', 'Virginia', 62, favorites, probs_by_name, selection_freq) is False)
# print("Assertions passed")

runs_done = 0
runs_completed = set()
sims_completed = {}
top_winrate = 0
reached_local_max = False
do_next_run = True
skip_list = {}

while not reached_local_max and do_next_run:
    if not AUTO_RUN:
        do_next_run = False
    print("Starting run")
    print("Working off of %s" % selections)
    local_top_winrate = top_winrate
    for i in reversed(range(64)):
        if i == 63:
            sim_selections = selections
            key = selections[i - 1]
        else:
            team = selections[i]
            bucket_winner = bucket_winner_from_idx(i)
            if bucket_winner and selections[bucket_winner] == team:
                continue
            else:
                prev_bucket = prev_bucket_start_from_idx(i)
                if i < 32:
                    if original_pos[prev_bucket] == team:
                        prev_beat = original_pos[prev_bucket + 1]
                    else:
                        prev_beat = original_pos[prev_bucket]
                else:
                    if selections[prev_bucket] == team:
                        prev_beat = selections[prev_bucket + 1]
                    else:
                        prev_beat = selections[prev_bucket]
                if pickable(prev_beat, team, i, favorites, probs_by_name, selection_freq, skip_list):
                    sim_selections = selections[:]
                    sim_selections[i] = prev_beat
                    key = prev_beat
                else:
                    print("Skipped %s at %s" % (prev_beat, str(i)))
                    continue
        if tuple(sim_selections) in sims_completed:
            print("Already sim'd %s" % key)
            continue
        wins = 0
        # For each simulation
        print("Starting %s" % key)
        for sim in range(NUM_SIMS):
            # Build opponent picks
            opp_picks = []
            for i in range(NUM_OPPONENTS):
                opp_x = build_selections(b, selection_freq)
                opp_picks.append(opp_x)
            # Simulate actual results
            results = b.simulate()
            # Score picks
            my_score = score(sim_selections, results)
            tied = 0
            lost = False
            for opp in opp_picks:
                opp_score = score(opp, results)
                if opp_score > my_score:
                    lost = True
                    break;
                elif opp_score == my_score:
                    tied += 1
            # Win/Lose Update
            if not lost:
                wins += (1 / (tied + 1))
                winrate = wins / (sim + 1)
            if (sim + 1) % 1000 == 0:
                print("%s sims complete, current winrate: %s" % (sim + 1, winrate))
                if sim < 1000 and winrate < local_top_winrate - 0.025:
                    print("Giving up on %s" % key)
                    print("Local top winrate is %s" % local_top_winrate)
                    print("Margin is %s" % str(0.025))
                    print("threshold is %s" % (local_top_winrate - 0.025))
                    if winrate < top_winrate - 0.025:
                        if key in skip_list:
                            skip_list[key].append(i)
                        else:
                            skip_list[key] = [i]
                    break
                elif sim >= 1000 and sim < 2000 and winrate < local_top_winrate - 0.02:
                    print("Giving up on %s" % key)
                    print("Local top winrate is %s" % local_top_winrate)
                    print("Margin is %s" % str(0.02))
                    print("threshold is %s" % (local_top_winrate - 0.02))
                    if winrate < top_winrate - 0.02:
                        if key in skip_list:
                            skip_list[key].append(i)
                        else:
                            skip_list[key] = [i]
                    break
                elif sim >= 2000 and sim < 6000 and winrate < local_top_winrate - 0.015:
                    print("Giving up on %s" % key)
                    print("Local top winrate is %s" % local_top_winrate)
                    print("Margin is %s" % str(0.015))
                    print("threshold is %s" % (local_top_winrate - 0.015))
                    if winrate < top_winrate - 0.015:
                        if key in skip_list:
                            skip_list[key].append(i)
                        else:
                            skip_list[key] = [i]
                    break
                elif sim >= 6000 and winrate < local_top_winrate - 0.01:
                    print("Giving up on %s" % key)
                    print("threshold is %s" % (local_top_winrate - 0.01))
                    if winrate < top_winrate - 0.01:
                        if key in skip_list:
                            skip_list[key].append(i)
                        else:
                            skip_list[key] = [i]
                    break

        print("DONE with %s" % key)
        winrate = wins / NUM_SIMS
        sims_completed[tuple(sim_selections)] = {'wins': wins, 'winrate': winrate, 'run_num': runs_done}
        performance.append({
            'key': key, 'selections': sim_selections, 'run_num': runs_done,
            'winrate': winrate, 'wins': wins})
        if winrate > local_top_winrate:
            local_top_winrate = winrate
        # if top_winrate > 0 and winrate > top_winrate + CONF_INT:
        #     print("Found a better bracket, using %s, with winrate of %s" % (key, winrate))
        #     print("Previous best was %s" % top_winrate)
        #     break

    output_filename = './output/basketball/sim_runs/%s.csv' % runs_done
    runs_done += 1
    runs_completed.add(tuple(selections))
    sorted_results = sorted(performance, key=lambda x: x['winrate'], reverse=True)
    with open(output_filename, 'w+') as f:
        for result in sorted_results:
            line = ",".join([str(result['run_num']), result['key'], str(result['wins']), str(result['winrate'])] + result['selections'])
            f.write(line + '\n')

    if sorted_results[0]['winrate'] > top_winrate:
        top_winrate = sorted_results[0]['winrate']
    next_base = get_next_base(sorted_results, runs_completed, top_winrate)
    eligible_choices = [x for x in sorted_results if x['winrate'] > top_winrate - CONF_INT]
    if not AUTO_RUN:
        for x in eligible_choices:
            print("%s: %s\n" % (x['key'], x['winrate']))
    if next_base:
        selections = next_base
        continue
    else:
        reached_local_max = True
        print("At local max, found %s possibilities so far" % len(eligible_choices))
        for x in eligible_choices:
            if tuple(x['selections']) not in runs_completed:
                next_base = x['selections']
                reached_local_max = False
                continue
