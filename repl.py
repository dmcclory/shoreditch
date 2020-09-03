import os
from persistence import load_database

PICKLE_PATH = os.environ['PICKLE_PATH']
data = load_database(PICKLE_PATH)


print("'data' holds {} records. have fun repl-in!".format(len(data)))

import pdb; pdb.set_trace()
print("done!")
