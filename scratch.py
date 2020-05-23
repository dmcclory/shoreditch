import pickle
from sparklines import sparklines
from itertools import groupby

from datetime import datetime

thing = pickle.read('data.pickle')

# munge .... 

# subset = thing[0:30]


# gotta make the dates "02/22/2020" formatted in loader, at least
# DONE: probably just save them as dates (sorted) 

# datetime.strptime('02/17/2020', '%m/%d/%Y')

# DONE: then I gotta group by, and group within those groups
# d.month 
# d.day % 7
# at least having parsed dates with 
# ahhh tuple makes it a little nicer

# then I gotta write a function get turns them in

# then I gotta print the sparklines

# then I gotta do some cleanup

first = thing[0]

dates = first.pings

list(groupby(n.pings, lambda x: x.split('/')[0]))

groups = []
groupings = groupby(n.pings, lambda x: x.split('/')[0])
for (k, g) in groupings:
    groups.append(list(g))



groupings = groupby(dates, lambda d: (d.month, d.day % 7))
for (k, g) in groupings:
    groups.append(list(g))

groups = []
groupings = groupby(dates, lambda d: (d.month, d.day % 7))
for (k, g) in groupings:
    groups.append(list(g))

counts = []
groupings = groupby(dates, lambda d: (d.month, d.day % 7))
for (k, g) in groupings:
    counts.append(len(list(g)))


# but this is correct:
# mod  was ... not what i want

groupby(dates, lambda d: (d.month, d.day // 7))


close = defaultdict(lambda: 0)
huh = groupby(p2[1].pings, lambda d: (d.month, d.day // 7))
for (k, g) in huh:
    close[k] = len(list(g))
[ close[(j, i)] for j in range(0, 6) for i in range(0, 6) ]
[ (j, i) for j in range(1, 5) for i in range(0, 5) ]

# close = defaultdict(lambda: 0)
# huh = groupby(thing[1].pings, lambda d: (d.month, d.day // 7))
# for (k, g) in huh:
    # close[k] = len(list(g))
# spark_input = [ close[(j, i)] for j in range(0, 6) for i in range(0, 6) ]
# [ print(str((i,j)) + ": " + str(close[(j, i)])) for j in range(0, 6) for i in range(0, 6) ]
# [ (j, i) for j in range(1, 5) for i in range(0, 5) ]
