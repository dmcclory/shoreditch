from shoreditch.tfidf_search import TfidfSearcher, process_watch_log, add_watches_to_entries, add_uncategorized_to_entries
from shoreditch.persistence import store_database

searcher = TfidfSearcher(['data/mega.txt'])


as_watches, uncategorized = process_watch_log(searcher.matches_df, ['data/mega_watch.txt'])
entries = add_watches_to_entries(as_watches, searcher.entries)

path = 'augmented_data.pickle'
store_database(path, entries)

print(as_watches)
print(len(as_watches.keys()))
print('---------------')
print(uncategorized)
