import os
import re
from datetime import datetime
from collections import defaultdict

from entry import Entry
from persistence import store_database
from fuzzy_search import FuzzySearcher


wow = defaultdict(Entry)
current_date = None

searcher = FuzzySearcher(['data/2020.txt', 'data/2019.txt', 'data/2018.txt'])

for year in ['2018', '2019', '2020']:
    with open('data/{}.txt'.format(year)) as f:
        choices = f.readlines()

    for title in choices:
        cleaned = title.strip()
        if (cleaned == ''):
            continue
        elif (re.match('^\d+\/\d+', cleaned)):
            current_date = cleaned.strip(':')
            current_date = current_date + '/' + year
            current_date = datetime.strptime(current_date, '%m/%d/%Y')
        else:
            canonicalish = searcher.get_best_match(cleaned)
            wow[canonicalish].titles.append(cleaned)
            wow[canonicalish].pings.append(current_date)

print("done!!!!!")

thing = list(wow.values())

thing.sort(key = lambda v: len(v.pings))
thing.reverse()

for entry in thing:
    entry.pings.sort()

store_database('data.pickle', thing)

# for entry in thing:
#     print(entry.titles[0] + ": " + str(len(entry.pings)))
