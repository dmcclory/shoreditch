import os
import pickle

from entry import Entry

def load_database(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)

    return data