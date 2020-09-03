import os
import sys
import argparse

from sparklines import sparklines
from termcolor import colored
from entry import Entry, get_dataset
from persistence import load_database

parser = argparse.ArgumentParser(description='Browse the Cool Stuff', allow_abbrev=True)

parser.add_argument('-b', '--bucket_size',
                    dest='window',
                    default='weeks',
                    help='group by week or by month (default: week)',
                   )
parser.add_argument('-w', '--window',
                    dest='go_back',
                    default=30,
                    type=int,
                    help='number of buckets to see (default: 20)',
                   )
parser.add_argument('-c', '--count',
                    dest='number_to_see',
                    default=40,
                    type=int,
                    help='number of buckets to see (default: 20)',
                   )
parser.add_argument('-s', '--status',
                    dest='status',
                    default='all',
                    help='filter by status (default: any)',
                   )
parser.add_argument('-t', '--type',
                    dest='type',
                    default='all',
                    help='filter by media type (default: any)',
                   )
parser.add_argument('--all',
                    action='store_true',
                    help='ignore count & show all of a certain status')

args = parser.parse_args()

WINDOW = args.window
GO_BACK = args.go_back
NUMBER_TO_SEE = args.number_to_see
STATUS = args.status
SHOW_ALL=args.all

PICKLE_PATH = os.environ['PICKLE_PATH']

thing = load_database(PICKLE_PATH)

# it would be cool to be able to specify a range of dates
# would be cool to be able to type in a title & see it's history

# it would be nice to be able to do something cool for the 'first time added'
# and the 'completed' date - like a different color

# and of course ... filtering on "seen"
# and being able to see reports of things I *have* seen

datasets = [get_dataset(thing[i], window=WINDOW, go_back=GO_BACK) for i in range(0, NUMBER_TO_SEE)]
maximum = max([item for sublist in datasets for item in sublist])


def build_sparkline(piece):
    dataset = get_dataset(piece, window=WINDOW, go_back=GO_BACK)
    return sparklines(dataset, minimum = 0, maximum = maximum + 1)[0]


def title_format(piece):
    title = piece.titles[0]
    return title + " (" + str(len(piece.pings)) + ")"


def color_for_row(piece):
    title = piece.titles[0]
    if piece.finished():
        color = "green"
    elif piece.started():
        color = "cyan"
    else:
        color = "white"
    return color

started_pieces = [t for t in thing if (t.started() and not t.finished())]
finished_pieces = [t for t in thing if t.finished()]
combined = finished_pieces + started_pieces
unstarted = [t for t in thing if t not in combined]

if STATUS == 'started':
    cool_array = started_pieces
elif STATUS == 'finished':
    cool_array = finished_pieces
elif STATUS == 'unstarted':
    cool_array = unstarted
else:
    cool_array = thing

if SHOW_ALL:
    subset_count = len(cool_array)
else:
    subset_count = min(len(cool_array), NUMBER_TO_SEE)

selected_rows = [cool_array[i] for i in range(subset_count)]

lines = [ build_sparkline(p) for p in selected_rows]
titles = [title_format(p) for p in selected_rows]
colors_from_statuses = [color_for_row(p) for p in selected_rows]

for (title, line, color) in zip(titles, lines, colors_from_statuses):
    print(colored( title.ljust(40) + line, color))
