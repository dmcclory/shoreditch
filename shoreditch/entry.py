from datetime import datetime, timedelta
from collections import defaultdict
from itertools import groupby
from dataclasses import dataclass
from typing import Dict
from datetimerange import DateTimeRange

def count_durations_ago(count, duration_string):
    today = datetime.now()
    if duration_string == 'weeks':
        duration = 7
    else:
        duration = 30
    return today - timedelta(duration*count)

def get_week_keys_for_n_months(n):
    res = []
    for i in range(n):
        t = count_durations_ago(i, 'weeks')
        res.append((t.year, t.month, t.day // 7))

    res.reverse()
    return res


def get_month_keys_for_n_months(n):
    today = datetime.now()
    res = []
    for i in range(n):
        t = count_durations_ago(i, 'months')
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


def get_dataset(entry, window=None, go_back=None):
    return get_linedata(entry.pings, window, go_back)


@dataclass
class Watch():
    started: datetime = None
    finished: datetime = None



def add_to_list_in_dict(d, k, v):
    if k not in v:
        d[k] = []
    d[k] = v


class Entry():
    def __init__(self, key=''):
        self.pings = []
        self.titles = []
        self.watches = []
        self.annotations = {}
        self.key = key

    def finished(self):
        if not 'watches' in self.__dict__.keys():
            return False
        finished_watches = [w for w in self.watches if w.finished]
        return len(finished_watches) > 0

    def started(self):
        if not 'watches' in self.__dict__.keys():
            return False
        started_watches = [w for w in self.watches if w.started]
        return len(started_watches) > 0

    def add_annotations(self, new_annotations: Dict[str, str]):
        for (k, v) in new_annotations.items():
            add_to_list_in_dict(self.annotations, k, v)

    def title(self):
        title = self.titles[0]
        return title

    def ping_count(self):
        return len(self.pings)

    def pings_within(self, start_date, end_date):
        daterange = DateTimeRange(start_date, end_date)
        return [p for p in self.pings if p in daterange]



    def type(self):
        return self.annotations.get('type', None)
