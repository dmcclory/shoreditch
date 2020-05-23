
import pickle

class Entry():
    def __init__(self):
        self.pings = []
        self.titles = []

with open('data.pickle', 'rb') as f:
    thing = pickle.load(f)

for entry in thing:
    print(entry.titles[0] + ": " + str(len(entry.pings)))
