import os
import re
import pickle

from collections import defaultdict
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from entry import Entry, Watch

from dataclasses import dataclass

from datetime import datetime
from persistence import load_database, store_database, load_object

from tfidf_helpers import get_best_key
from normalization import normalize, key_for

PICKLE_PATH = os.environ['MATCH_LINES_INPUT']
thing = load_database(PICKLE_PATH)

matches_df = load_object('tf_matches.pickle')


titles = [t.titles[0] for t in thing]


def get_matches(title):
    return process.extract(title, titles, limit=10)


cool = defaultdict(lambda: [])
uncategorized = defaultdict(lambda: [])
uncategorized = []

for year in ['2020', '2019']:
    with open('data/{}_watch.txt'.format(year)) as f:
        watches = f.readlines()

    for entry in watches:
        cleaned = entry.strip()
        if (cleaned == ''):
            continue
        elif (re.match('^\d+\/\d+', cleaned)):
            current_date = cleaned.strip(':')
            current_date = current_date + '/' + year
            current_date = datetime.strptime(current_date, '%m/%d/%Y')
        else:
            print('title: ', cleaned)
            verb, *rest = cleaned.split(' ')
            title = ' '.join(rest)
            title_key = key_for(title)
            key = get_best_key(matches_df, title_key)
            if key:
                cool[key].insert(0, (verb, current_date, title))
            else:
                uncategorized.append((verb, current_date, title))

as_watches = { }

for (k,v) in cool.items():
    as_watches[k] = []
    for (verb, current_date, title) in v:
        if verb == 'Watched':
            w = Watch()
            w.started = current_date
            w.finished = current_date
            as_watches[k].append(w)
        if verb == 'Started':
            w = Watch()
            w.started = current_date
            as_watches[k].append(w)
        if verb == 'Finished':
            try:
                w = as_watches[k][-1]
                w.finished = current_date
            except:
                import pdb; pdb.set_trace()

thing_dict = { t.key: t for t in thing}


for (k, v) in as_watches.items():
    entry = thing_dict[k]
    entry.watches = v

thing_with_extra_data = list(thing_dict.values())
thing_with_extra_data.sort(key = lambda v: len(v.pings))
thing_with_extra_data.reverse()

path = 'augmented_data.pickle'
store_database(path, thing_with_extra_data)


print(as_watches)
print(len(as_watches.keys()))
print('---------------')
print(uncategorized)
