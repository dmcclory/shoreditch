import pickle
from sparklines import sparklines
from itertools import groupby
import argparse

from datetime import datetime, timedelta
from collections import defaultdict

import sys

from termcolor import colored

parser = argparse.ArgumentParser(description='Browse the Cool Stuff', allow_abbrev=True)

parser.add_argument('-b', '--bucket_size',
                    dest='window',
                    default='weeks',
                    help='group by week or by month (default: week)',
                   )
parser.add_argument('-w', '--window',
                    dest='go_back',
                    default=20,
                    type=int,
                    help='number of buckets to see (default: 20)',
                   )
parser.add_argument('-c', '--count',
                    dest='number_to_see',
                    default=20,
                    type=int,
                    help='number of buckets to see (default: 20)',
                   )
parser.add_argument('-s', '--status',
                    dest='status',
                    default='all',
                    help='filter by status (default: all)',
                   )
parser.add_argument('-t', '--type',
                    dest='type',
                    default='all',
                    help='filter by media type (default: all)',
                   )

args = parser.parse_args()

WINDOW = args.window
GO_BACK = args.go_back
NUMBER_TO_SEE = args.number_to_see

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


# gotta share/import this
class Entry():
    def __init__(self):
        self.pings = []
        self.titles = []

    def get_dataset(self):
        return get_linedata(self.pings, window=WINDOW, go_back=GO_BACK)


with open('data.pickle', 'rb') as f:
    thing = pickle.load(f)


# it would be cool to be able to specify a range of dates
# would be cool to be able to type in a title & see it's history

# it would be nice to be able to do something cool for the 'first time added'
# and the 'completed' date - like a different color

# and of course ... filtering on "seen"
# and being able to see reports of things I *have* seen

datasets = [thing[i].get_dataset() for i in range(0, NUMBER_TO_SEE)]
maximum = max([item for sublist in datasets for item in sublist])

finished = ["Burning", "Jojo Rabbit", "Game of Thrones (s2)", "Uncut Gems", "Babylon Berlin (s3)", "Jaws", "Knives Out", "Barry (s2)", "Germania", "Force Majeure", "The Taking of Pelham 123", "Riverdale", "Parasite", "Chernobyl", "Art of Self defense", "Waiting for Guffman", "Ip Man", "Sopranos (s1)", "Succession (s2)"]
started = ["Bosch", "Satoshi Kon Filmography", "Death Stranding", "Wolf Hall",  "True Detective (s1)", "Killing Eve (s3)", "Sopranos", "True Detective"]


def build_sparkline(piece):
    dataset = piece.get_dataset()
    return sparklines(dataset, minimum = 0, maximum = maximum + 1)[0]


def title_format(piece):
    title = piece.titles[0]
    return title + " (" + str(len(piece.pings)) + ")"


def color_for_row(piece):
    title = piece.titles[0]
    if title in finished:
        color = "green"
    elif title in started:
        color = "cyan"
    else:
        color = "white"
    return color


started_pieces = [t for t in thing if t.titles[0] in started]
finished_pieces = [t for t in thing if t.titles[0] in finished]
combined = finished_pieces + started_pieces
unstarted = [t for t in thing if t not in combined]

# cool_array = combined
# cool_array = unstarted
cool_array = thing

subset_count = min(len(cool_array), NUMBER_TO_SEE)
selected_rows = [cool_array[i] for i in range(subset_count)]

lines = [ build_sparkline(p) for p in selected_rows]
titles = [title_format(p) for p in selected_rows]
colors_from_statuses = [color_for_row(p) for p in selected_rows]

for (title, line, color) in zip(titles, lines, colors_from_statuses):
    print(colored( title.ljust(40) + line, color))
