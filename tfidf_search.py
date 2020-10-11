import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.sparse import csr_matrix
import sparse_dot_topn.sparse_dot_topn as ct

from entry import Entry
from datetime import datetime

from line_predicates import (blank, dateline)

from persistence import store_database, store_object

from collections import defaultdict

from tfidf_helpers import get_best_key
from normalization import normalize, key_for

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
    result = []
    titles = []
    dates = []
    for path in paths:
        year = path[5:9]
        with open(path) as f:
            for line in f.readlines():
                cleaned = line.strip()

                if blank(cleaned):
                    continue

                elif dateline(cleaned):
                    current_date = cleaned.strip(':')
                    current_date = current_date + '/' + year
                    current_date = datetime.strptime(current_date, '%m/%d/%Y')
                else:
                    result.append([cleaned, current_date])
                    titles.append(cleaned)
                    dates.append(current_date)

    df = pd.DataFrame.from_dict({'title': titles, 'date': dates}, dtype="string")
    return df


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

        for row in self.title_date_df.iterrows():
            key = get_best_key(self.matches_df, row[1]['normalized']) or row[1]['normalized']
            e = wow[key]
            if e.key == '':
                e.key = key
            e.titles.append(row[1]['title'])
            e.pings.append(datetime.fromisoformat(row[1]['date']))
        for e in wow.values():
            self.entries.append(e)

        self.entries.sort(key = lambda v: len(v.pings))
        self.entries.reverse()

    def save(self):
        store_object('tf_matches.pickle', self.matches_df)
        store_database('tf_data.pickle', self.entries)
