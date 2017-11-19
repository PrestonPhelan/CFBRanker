def build_conference_flairs(data):
    result = {}
    for line in data:
        abrev, flair = line.strip().split(',')
        result[abrev] = flair
    return result

def build_result_string(team):
    performance = round(team.calculate_performance_rating(), 2)
    combined = round(team.get_combined_rating(), 2)
    reddit = team.get_reddit_rating()

    return ",".join(map(lambda el: str(el), [
        team.power_mean,
        performance,
        combined,
        reddit,
        team.name]))
