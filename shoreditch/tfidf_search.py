import pandas as pd
import numpy as np
import re
from collections import defaultdict
from datetime import datetime
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
import sparse_dot_topn.sparse_dot_topn as ct



from shoreditch.entry import Entry, Watch
from shoreditch.line_predicates import blank, dateline, yearline, extract_year, parse_title_line
from shoreditch.normalization import normalize, key_for
from shoreditch.persistence import store_database, store_object
from shoreditch.tfidf_helpers import get_best_key

def ngrams(string, n=3):
    if len(string) < n:
        return [string.ljust(3, '*')]
    string = re.sub(r'[,-./]|\sBD', r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]

def awesome_cossim_top(A, B, ntop, lower_bound=0):
  # force A and B as a CSR matrix.
  # If they have already been CSR, there is no overhead
  A = A.tocsr()
  B = B.tocsr()
  M, _ = A.shape
  _, N = B.shape

  idx_dtype = np.int32

  nnz_max = M*ntop

  indptr = np.zeros(M+1, dtype=idx_dtype)
  indices = np.zeros(nnz_max, dtype=idx_dtype)
  data = np.zeros(nnz_max, dtype=A.dtype)
  ct.sparse_dot_topn(
    M, N, np.asarray(A.indptr, dtype=idx_dtype),
    np.asarray(A.indices, dtype=idx_dtype),
    A.data,
    np.asarray(B.indptr, dtype=idx_dtype),
    np.asarray(B.indices, dtype=idx_dtype),
    B.data,
    ntop,
    lower_bound,
    indptr, indices, data
  )

  return csr_matrix((data,indices,indptr),shape=(M,N))

def get_matches_df(sparse_matrix, name_vector, top=None):
    non_zeros = sparse_matrix.nonzero()
    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]

    if top:
        nr_matches = top
    else:
        nr_matches = sparsecols.size

    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similarity = np.zeros(nr_matches)

    for index in range(0, nr_matches):
        left_side[index] = name_vector[sparserows[index]]
        right_side[index] = name_vector[sparsecols[index]]
        similarity[index] = sparse_matrix.data[index]

    return pd.DataFrame({'left_side': left_side,
                          'right_side': right_side,
                           'similarity': similarity})

def title_date_df(paths):
    current_date = None
    titles = []
    dates = []
    annotations = []
    for path in paths:
        with open(path) as f:
            for line in f.readlines():
                cleaned = line.strip()

                if blank(cleaned):
                    continue

                elif yearline(cleaned):
                    year = extract_year(cleaned)

                elif dateline(cleaned):
                    current_date = cleaned.strip(':')
                    current_date = current_date + '/' + year
                    current_date = datetime.strptime(current_date, '%m/%d/%Y')
                else:
                    title, annotate = parse_title_line(cleaned)
                    titles.append(cleaned)
                    dates.append(current_date)
                    annotations.append(annotate)

    df = pd.DataFrame.from_dict({'title': titles, 'date': dates}, dtype="string")
    df['annotations'] = annotations
    return df


def add_watch_data(watches_dict, data, key):
    verb, current_date, title = data
    if verb == 'Watched':
        w = Watch()
        w.started = current_date
        w.finished = current_date
        watches_dict[key].append(w)
    if verb == 'Started':
        w = Watch()
        w.started = current_date
        watches_dict[key].append(w)
    if verb == 'Finished':
        try:
            w = watches_dict[key][-1]
            w.finished = current_date
        except:
            import pdb; pdb.set_trace()


def process_watch_log(matches_df, paths):
    watch_events = defaultdict(lambda: [])
    uncategorized = []
    for path in paths:
        with open(path) as f:
            watches = f.readlines()

        for entry in watches:
            cleaned = entry.strip()
            if (cleaned == ''):
                continue
            elif yearline(cleaned):
                year = extract_year(cleaned)
            elif dateline(cleaned):
                current_date = cleaned.strip(':')
                current_date = current_date + '/' + year
                current_date = datetime.strptime(current_date, '%m/%d/%Y')
            else:
                print('title: ', cleaned)
                verb, *rest = cleaned.split(' ')
                title = ' '.join(rest)
                title_key = key_for(title)
                key = get_best_key(matches_df, title_key)
                if key:
                    watch_events[key].insert(0, (verb, current_date, title))
                else:
                    uncategorized.append((verb, current_date, title))

    as_watches = { }

    for (k,v) in watch_events.items():
        as_watches[k] = []
        for l in v:
            add_watch_data(as_watches, l, k)

    return (as_watches, uncategorized)


def add_watches_to_entries(as_watches, entries):
    entries_dict = { t.key: t for t in entries}

    for (k, v) in as_watches.items():
        entry = entries_dict[k]
        entry.watches = v

    entries_with_extra_data = list(entries_dict.values())
    entries_with_extra_data.sort(key = lambda v: len(v.pings))
    entries_with_extra_data.reverse()

    return entries_with_extra_data



# started this back in October 2020 and
# i don't remember why I wanted to add this
def add_uncategorized_to_entries(uncategorized, entries):
    for entry_data in uncategorized:
        verb, current_date, title = entry_data
        e = Entry()
        e.titles.append(title)
        e.pings.append(current_date)





class TfidfSearcher():
    def __init__(self, paths):
        self.paths = paths
        self.title_date_df = title_date_df(paths)
        self.entries = []
        self.title_date_df = normalize(self.title_date_df)
        titles = self.title_date_df['normalized']
        vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
        tf_idf_matrix = vectorizer.fit_transform(titles)
        matches = awesome_cossim_top(tf_idf_matrix, tf_idf_matrix.transpose(), 10, 0.8)
        self.matches_df = get_matches_df(matches, titles)
        self.group_into_sets()

    def group_into_sets(self):
        sets  = []
        wow = defaultdict(Entry)

        # self.title_date_df[self.title_date_df['normalized'] == key]
        # this could be a simpler way to select things
        for row in self.title_date_df.iterrows():
            key = get_best_key(self.matches_df, row[1]['normalized']) or row[1]['normalized']
            e = wow[key]
            if e.key == '':
                e.key = key
            e.titles.append(row[1]['title'])
            e.pings.append(datetime.fromisoformat(row[1]['date']))
            if row[1]['annotations']:
                e.add_annotations(row[1]['annotations'])
        for e in wow.values():
            self.entries.append(e)

        self.entries.sort(key = lambda v: len(v.pings))
        self.entries.reverse()

    def save(self):
        store_object('tf_matches.pickle', self.matches_df)
        store_database('tf_data.pickle', self.entries)
