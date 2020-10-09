
from collections import defaultdict

import recordlinkage
import pandas as pd

from line_predicates import (blank, dateline)

from persistence import store_database
from entry import Entry
from datetime import datetime

def title_date_df():
    current_date = None
    result = []
    for year in ['2018', '2019', '2020']:
        with open('data/{}.txt'.format(year)) as f:
            for line in f.readlines():
                cleaned = line.strip()
                if blank(cleaned):
                    continue
                elif dateline(cleaned):
                    current_date = cleaned.strip(':')
                    current_date = current_date + '/' + year
                    current_date = datetime.strptime(current_date, '%m/%d/%Y')
                else:
                    result.append([cleaned, current_date])
    df = pd.DataFrame.from_records(result, columns=['title', 'date'])
    return df


class LinkageSearcher():
    def __init__(self, paths):
        self.title_date_df = title_date_df()
        titleIndexer = recordlinkage.Index()
        titleIndexer.block('title')
        self.matches = titleIndexer.index(self.title_date_df)
        self.group_into_sets()

    def group_into_sets(self):
        sets = []
        current_set = {self.matches[0][1]}
        for (a, b) in self.matches:
            if not b in current_set:
                sets.append(current_set)
                current_set = {a,b}
            else:
                current_set.add(a)
        result = []
        for group in sets:
            titles = []
            for index in group:
                row = self.title_date_df.iloc[index]
                titles.append( {'date': row.date, 'title': row.title} )

            result.append(titles)

        all_indices = set([num for elem in self.matches.to_list() for num in elem])
        for (i, row) in self.title_date_df.iterrows():
            if not i in all_indices:
                titles = [ {'date': row.date, 'title': row.title} ]
                result.append(titles)

        self.grouped_titles = result

        self.entries = []

        for group in self.grouped_titles:
            e = Entry()
            for ping in group:
                e.titles.append(ping['title'])
                e.pings.append(ping['date'].to_pydatetime())
            e.pings.sort()
            self.entries.append(e)

        self.entries.sort(key = lambda v: len(v.pings))
        self.entries.reverse()

    def save(self):
        store_database('rl_data.pickle', self.entries)
