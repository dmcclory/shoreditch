import pickle
from sparklines import sparklines
from itertools import groupby

from datetime import datetime, timedelta
from collections import defaultdict

import sys

# gotta share/import this
class Entry():
    def __init__(self):
        self.pings = []
        self.titles = []


with open('data.pickle', 'rb') as f:
    thing = pickle.load(f)


def get_week_keys_for_n_months(n):
    today = datetime.now()
    res = []
    for i in range(n):
        t = today - timedelta(7*i)
        res.append((t.year, t.month, t.day // 7))

    res.reverse()
    return res


def get_month_keys_for_n_months(n):
    today = datetime.now()
    res = []
    for i in range(n):
        t = today - timedelta(30*i)
        res.append((t.year, t.month))

    res.reverse()
    return res



def get_linedata(pings, window='weeks', go_back=6):
    if window == 'weeks':
        keys = get_week_keys_for_n_months(go_back)
        counts = groupby(pings, lambda d: (d.year, d.month, d.day // 7))
    if window == 'months':
        keys = get_month_keys_for_n_months(go_back)
        counts = groupby(pings, lambda d: (d.year, d.month))
    cool = defaultdict(lambda: 0)

    for (k, g) in counts:
        cool[k] = len(list(g))
    linedata = [ cool[key] for key in keys]
    return linedata


window = sys.argv[1] or 'weeks'
go_back = int(sys.argv[2])  if len(sys.argv) > 2 else 30

number_to_see = 20
datasets = [get_linedata(thing[i].pings, window=window, go_back=go_back) for i in range(0, number_to_see)]
maximum = max([item for sublist in datasets for item in sublist])

lines = [ sparklines(d, minimum = 0, maximum = maximum + 1)[0] for d in datasets]
titles = [thing[i].titles[0] for i in range(0, number_to_see)]
for (title, line) in zip(titles, lines):
    print(title.ljust(40) + line)
