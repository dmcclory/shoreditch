import os
import pickle

from entry import Entry

PICKLE_PATH = os.environ['PICKLE_PATH']

with open(PICKLE_PATH, 'rb') as f:
    data = pickle.load(f)

print("'data' holds {} records. have fun repl-in!".format(len(data)))

import pdb; pdb.set_trace()
print("done!")
