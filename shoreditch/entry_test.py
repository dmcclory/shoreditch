import pytest

from .entry import Entry
from datetime import datetime

def ping_factory(pd = None):
    return pd or datetime.datetime.today().date()

def test_ping_count_returns_number_of_pings():
    e = Entry()
    e.titles = ['wow', 'wow', 'wow']
    e.pings = [
       ping_factory(datetime.fromisoformat('2020-11-20')),
       ping_factory(datetime.fromisoformat('2020-11-30')),
       ping_factory(datetime.fromisoformat('2020-12-10')),
    ]
    assert e.ping_count() == 3

def test_pings_within_returns_list_of_pings_within_date_range():
    e = Entry()
    e.titles = ['wow', 'wow', 'wow']
    e.pings = [
       ping_factory(datetime.fromisoformat('2020-11-20')),
       ping_factory(datetime.fromisoformat('2020-11-30')),
       ping_factory(datetime.fromisoformat('2020-12-10')),
    ]
    assert len(e.pings_within(
        datetime.fromisoformat('2020-11-01'),
        datetime.fromisoformat('2020-11-30')
    )) == 2
