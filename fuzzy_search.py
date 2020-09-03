from fuzzywuzzy import process

class FuzzySearcher():
    def __init__(self, paths):
        self.huge_choice_set = []

        for path in paths:
            with open(path) as f:
                self.huge_choice_set += f.readlines()

    def get_best_match(self, title):
        res = process.extract(title, self.huge_choice_set, limit=10)
        return res[0][0]
