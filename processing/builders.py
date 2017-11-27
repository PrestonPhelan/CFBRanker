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

def build_reddit_string(idx, team, conference_flairs, flair_dict):
    rank = idx + 1
    flair_string = team.get_flair_string(flair_dict)
    conf_flair = conference_flairs[team.conference]
    rating = team.get_reddit_rating()

    result = "%(rnk)s | %(lw)s | %(name)s | %(record)s | %(conference)s | %(rating)s |\n" % {
        'rnk': rank,
        'lw': team.last_week,
        'name': flair_string,
        'record': team.record,
        'conference': conf_flair,
        'rating': rating
    }
    return result

def build_filename_format(team_name):
    filename_format_name = ''
    for character in team_name:
        if character.isalpha():
            filename_format_name += character.lower()
    return filename_format_name
