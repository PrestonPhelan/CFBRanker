class Team:

    @classmethod
    def build_teams_from_file(cls, sourcefile):
        teams = {}
        name_list = None
        with open(sourcefile) as f:
            name_list = list(f)
        for line in name_list:
            name, conference = line.strip().split(',')
            teams[name] = Team(name, conference)
        return teams

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

    def __init__(self, name, conference):
        self.name = name
        self.power_mean = None
        self.strength_of_record = None
        self.game_control = None
        self.combined_rating = None
        self.reddit_rating = None
        self.last_week = "NR"
        self.conference = conference
        self.record = None

    def __str__(self):
        return ", ".join([self.name, str(self.get_combined_rating())[:5]])

    def set_power_mean(self, rating):
        self.power_mean = rating
        if self.strength_of_record and self.game_control:
            self.set_combined_rating()

    def set_performance_metrics(self, strength_of_record, game_control):
        self.strength_of_record = strength_of_record
        self.game_control = game_control
        if self.power_mean is not None:
            self.set_combined_rating()

    def get_combined_rating(self):
        if self.combined_rating is None:
            self.set_combined_rating()
        return self.combined_rating

    def set_combined_rating(self):
        self.combined_rating = self.calculate_combined_rating()

    def calculate_combined_rating(self):
        rating = 0.5 * (self.calculate_power_rating() + self.calculate_performance_rating())
        return rating

    def calculate_power_rating(self):
        return self.power_mean

    def calculate_performance_rating(self):
        return (self.strength_of_record * 2 + self.game_control) / 3.0

    def get_reddit_rating(self):
        if self.reddit_rating is None:
            self.calculate_reddit_rating()
        return self.reddit_rating

    def calculate_reddit_rating(self):
        self.reddit_rating = round(100*(130-self.get_combined_rating())/129, 1)
