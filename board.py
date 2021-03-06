import os
import sys
import argparse
from datetime import datetime, timedelta
from random import shuffle
from sparklines import sparklines
from termcolor import colored

from shoreditch.entry import Entry, get_dataset, count_durations_ago
from shoreditch.persistence import load_database

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
parser.add_argument('-m', '--max_pings',
                    dest='max_pings',
                    default=9000000,
                    type=int,
                    help='max number of pings to allow (default: 9000000)',
                   )
parser.add_argument('-n', '--min_pings',
                    dest='min_pings',
                    default=1,
                    type=int,
                    help='min number of pings to allow (default: 1)',
                   )
parser.add_argument('-t', '--type',
                    dest='type',
                    default='all',
                    help='filter by media type (default: any)',
                   )
parser.add_argument('--all',
                    action='store_true',
                    help='ignore count & show all of a certain status')
parser.add_argument('--shuffle',
                    action='store_true',
                    help='randomly sort the results before reducing the number of options')
parser.add_argument('--slice_start',
                    dest='slice_start',
                    default=None,
                    type=str,
                    help='start date for time slice')
parser.add_argument('--slice_end',
                    dest='slice_end',
                    default=None,
                    type=str,
                    help='end date for time slice')

args = parser.parse_args()

WINDOW = args.window
GO_BACK = args.go_back
NUMBER_TO_SEE = args.number_to_see
STATUS = args.status
SHOW_ALL=args.all
TYPE= args.type
MIN_PINGS = args.min_pings
MAX_PINGS = args.max_pings
SHUFFLE = args.shuffle
SLICE_START = args.slice_start
SLICE_END = args.slice_end


PICKLE_PATH = os.environ['PICKLE_PATH']

db = load_database(PICKLE_PATH)

if SHUFFLE:
    shuffle(db)

if TYPE == 'all':
    thing = db
else:
    thing = [e for e in db if e.type() == TYPE]

if SLICE_START and SLICE_END:
    thing = [row for row in thing if row.pings_within(SLICE_START, SLICE_END)]

# filter based on the pings
thing = [row for row in thing if row.ping_count() >= MIN_PINGS and row.ping_count() <= MAX_PINGS]

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
    title = piece.title()
    return title + " (" + str(piece.ping_count()) + ")"


def color_for_row(piece):
    title = piece.title()
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

width = len(lines[0])

def format_header_date(date):
    return "{}/{}".format(str(date.month).rjust(2, '0'), date.year)

if width > 50:
    today = datetime.now()
    beginning = count_durations_ago(GO_BACK, WINDOW)
    midpoint = count_durations_ago(GO_BACK/2, WINDOW)
    beginning_string = format_header_date(beginning)
    ending_string = format_header_date(today)
    midpoint_string = format_header_date(midpoint)

    margin = width % 2

    dateline = beginning_string + midpoint_string.rjust(int((width/2))-3, ' ') + ending_string.rjust(int(width/2)-(4-margin), ' ')
    print(' ' * 40 + dateline)


for (title, line, color) in zip(titles, lines, colors_from_statuses):
    print(colored( title.ljust(40) + line, color))
