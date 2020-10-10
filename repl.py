import os
import sys
from persistence import load_database


PICKLE_PATH = sys.argv[1] if len(sys.argv) > 1 else os.environ['PICKLE_PATH']
print('loading: ', PICKLE_PATH)
data = load_database(PICKLE_PATH)


print("'data' holds {} records. have fun repl-in!".format(len(data)))

import pdb; pdb.set_trace()
print("done!")
