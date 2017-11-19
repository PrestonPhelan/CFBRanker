def build_conference_flairs(data):
    result = {}
    for line in data:
        abrev, flair = line.strip().split(',')
        result[abrev] = flair
    return result

def build_result_string(team, idx):
    rank = idx + 1
    performance = round(team.calculate_performance_rating(), 2)
    combined = round(team.get_combined_rating(), 2)
    reddit = team.get_reddit_rating()

    return ",".join(map(lambda el: str(el), [
        rank,
        team.power_mean,
        performance,
        combined,
        reddit,
        team.name]))

REDDIT_COLUMNS = ["Rnk", "LW", "Team", "W-L", "Conf", "Rating"]

def build_reddit_header():
    return " | ".join(REDDIT_COLUMNS) + "\n"

def build_reddit_barrier():
    return "|".join(map(lambda _: "---", REDDIT_COLUMNS)) + "\n"
