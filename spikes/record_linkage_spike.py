

from collections import defaultdict

import recordlinkage
import pandas as pd

with open('cool_titles.txt') as f:
  wow = f.read()

titles = wow.split('\n')

titleDF = pd.DataFrame(titles, columns=['title'])

titleIndexer = recordlinkage.Index()
titleIndexer.block('title')
matches = titleIndexer.index(titleDF)

d = defaultdict(lambda: [])

for (t1, t2) in matches:
  d[t1].append(t2)
  
dt = defaultdict(lambda: [])

for (k, v) in d.items():
  root = titleDF.iloc[k].title
  dt[root]
  for tid in v:
    dt[root].append(titleDF.iloc[tid].title)

thing = [v for (k, v) in d.items() if titleDF.iloc[k].title == "Bosch"]
cool = []

for t in thing:
  for c in t:
    cool.append(c)


set(cool)
list(set(cool))

sorted(list(set(cool))) == sorted(thing[-1])


bosch_keys = [k for (k, v) in d.items() if titleDF.iloc[k].title == "Bosch"]


print(bosch_keys)

