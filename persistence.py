import os
import pickle

from shoreditch.entry import Entry

def load_object(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)

    return data


def store_object(path, store):
    with open(path, 'wb') as f:
        pickle.dump(store, f)



def load_database(path):
    return load_object(path)


def store_database(path, store):
    store_object(path, store)
