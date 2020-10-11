import os
import re
from datetime import datetime
from collections import defaultdict


from shoreditch.entry import Entry, Watch
from shoreditch.normalization import normalize, key_for
from shoreditch.persistence import load_database, store_database, load_object
from shoreditch.tfidf_helpers import get_best_key

from shoreditch.tfidf_search import process_watch_log, add_watches_to_entries


matches_df = load_object('tf_matches.pickle')
PICKLE_PATH = os.environ['MATCH_LINES_INPUT']




as_watches, uncategorized = process_watch_log(matches_df, ['2020', '2019'])

entries = load_database(PICKLE_PATH)
entries = add_watches_to_entries(as_watches, entries)

path = 'augmented_data.pickle'
store_database(path, entries)


print(as_watches)
print(len(as_watches.keys()))
print('---------------')
print(uncategorized)
