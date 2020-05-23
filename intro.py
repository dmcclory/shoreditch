import os
import re
import pickle
from datetime import datetime
from collections import defaultdict

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

with open('bigger_file.txt') as f:
    choices = f.readlines()


def number_of_ok_matches(extract):
    return len(list(filter(lambda a: a[1] >= 90, extract)))

def get_matches(title):
    return process.extract(title, choices, limit=10)

class Entry():
    def __init__(self):
        self.pings = []
        self.titles = []

wow = defaultdict(Entry)

current_date = None

for title in choices:
    cleaned = title.strip()
    if (cleaned == ''):
        continue
    elif (re.match('^\d+\/\d+', cleaned)):
        current_date = cleaned.strip(':')
        current_date = current_date + '/2020'
        current_date = datetime.strptime(current_date, '%m/%d/%Y')
    else:
        res = get_matches(cleaned)
        canonicalish = res[0][0]
        wow[canonicalish].titles.append(cleaned)
        wow[canonicalish].pings.append(current_date)

print("done!!!!!")

thing = list(wow.values())

thing.sort(key = lambda v: len(v.pings))
thing.reverse()

for entry in thing:
    entry.pings.sort()

with open('data.pickle', 'wb') as f:
    pickle.dump(thing, f)

for entry in thing:
    print(entry.titles[0] + ": " + str(len(entry.pings)))
