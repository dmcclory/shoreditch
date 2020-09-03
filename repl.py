import pickle

from entry import Entry


with open('data.pickle', 'rb') as f:
    thing = pickle.load(f)

import pdb; pdb.set_trace()
print("done!")
