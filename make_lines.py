import pickle
from sparklines import sparklines
from itertools import groupby

from datetime import datetime
from collections import defaultdict


# gotta share/import this
class Entry():
    def __init__(self):
        self.pings = []
        self.titles = []


with open('data.pickle', 'rb') as f:
    thing = pickle.load(f)


def get_linedata(pings):
    window = defaultdict(lambda: 0)
    # want to make this generalizable
    # for the multiple year case
    # or how do we do the past N months, say??
    # the lambda should probably always include the year.....
    counts_per_month_week = groupby(pings, lambda d: (d.month, d.day // 7))
    for (k, g) in counts_per_month_week:
        window[k] = len(list(g))
    linedata = [ window[(j, i)] for j in range(0, 6) for i in range(0, 6) ]
    return linedata


number_to_see = 20
datasets = [get_linedata(thing[i].pings) for i in range(0, number_to_see)]
maximum = max([item for sublist in datasets for item in sublist])

lines = [ sparklines(d, minimum = 0, maximum = maximum + 1)[0] for d in datasets]
titles = [thing[i].titles[0] for i in range(0, number_to_see)]
for (title, line) in zip(titles, lines):
    print(title.ljust(40) + line)
