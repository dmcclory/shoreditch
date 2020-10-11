import os
import re
from datetime import datetime
from collections import defaultdict


from shoreditch.entry import Entry, Watch
from shoreditch.normalization import normalize, key_for
from shoreditch.persistence import load_database, store_database, load_object
from shoreditch.tfidf_helpers import get_best_key

from shoreditch.tfidf_search import process_watch_log



PICKLE_PATH = os.environ['MATCH_LINES_INPUT']
thing = load_database(PICKLE_PATH)
matches_df = load_object('tf_matches.pickle')



as_watches, uncategorized = process_watch_log(matches_df, ['2020', '2019'])

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
