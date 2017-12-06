class Game:

    def __init__(self, details):
        self.location = details['location']
        self.opponent = details['opponent']
        self.result = details['result']
        self.own_score = details['own_score']
        self.opp_score = details['opp_score']
        self.overtime = details['overtime']
        self.num_overtimes = details['num_overtimes']

    def __str__(self):
        string_to_print = "%(location)s vs. %(opponent)s, %(result)s %(own_score)s-%(opp_score)s" % {
            'location': self.location,
            'opponent': self.opponent,
            'result': self.result,
            'own_score': self.own_score,
            'opp_score': self.opp_score
        }
        if self.overtime:
            if self.num_overtimes > 1:
                string_to_print = string_to_print + " %sOT\n" % self.num_overtimes
            else:
                string_to_print = string_to_print + " OT\n"
        else:
            string_to_print += "\n"

        return string_to_print

    def difficulty(self, location_adjustment_func):
        return self.opponent.ratings['pure_points'] - location_adjustment_func(self.location)

    def _default_location_adjustment(self, string):
        results = {
            'N': 0,
            'H': 3,
            'A': -3
        }
        return results[string]
