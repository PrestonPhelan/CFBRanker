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
            string_to_print = string_to_print + " %sOT\n" % self.num_overtimes
        else:
            string_to_print += "\n"

        return string_to_print
