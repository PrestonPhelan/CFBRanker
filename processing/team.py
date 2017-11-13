class Team:

    def __init__(self, name):
        self.name = name
        self.power_mean = None
        self.strength_of_record = None
        self.game_control = None
        self.combined_rating = None

    def set_power_mean(self, rating):
        self.power_mean = ratings
        if self.strength_of_record and self.game_control:
            self.set_combined_rating

    def set_performance_metrics(self, strength_of_record, game_control):
        self.strength_of_record = strength_of_record
        self.game_control = game_control
        if self.power_mean is not None:
            self.set_combined_rating

    def get_combined_rating(self):
        if self.combined_rating is None:
            self.set_combined_rating()
        return self.combined_rating

    def set_combined_rating(self):
        self.combined_rating = self.calculate_combined_rating()

    def calculate_combined_rating(self):
        return 0.5 * (self.calculate_power_rating() + self.calculate_performance_rating())

    def calculate_power_rating(self):
        return self.power_mean

    def calculate_performance_rating(self):
        return (self.strength_of_record * 2 + self.combined_rating) / 3.0
