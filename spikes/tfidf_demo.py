import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
from scipy.sparse import csr_matrix

import sparse_dot_topn.sparse_dot_topn as ct

import time


pd.set_option('display.max_colwidth', None)

df = pd.read_csv('july_2019')

print(df.head(5))


def ngrams(string, n=3):
  string = re.sub(r'[,-./]|\sBD', r'', string)
  ngrams = zip(*[string[i:] for i in range(n)])
  return [''.join(ngram) for ngram in ngrams]


print('ngrams in deluxroom:')
print(ngrams('deluxroom'))


room_types = df['RoomTypes']
vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)

tf_idf_matrix = vectorizer.fit_transform(room_types)

print(tf_idf_matrix[0])


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

def get_matches_df(sparse_matrix, name_vector, top=100):
    non_zeros = sparse_matrix.nonzero()
    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]

    if top:
        nr_matches = top
    else:
        nr_matches = sparsecols.size

    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similairity = np.zeros(nr_matches)

    for index in range(0, nr_matches):
        left_side[index] = name_vector[sparserows[index]]
        right_side[index] = name_vector[sparsecols[index]]
        similairity[index] = sparse_matrix.data[index]

    return pd.DataFrame({'left_side': left_side,
                          'right_side': right_side,
                           'similairity': similairity})

matches = awesome_cossim_top(tf_idf_matrix, tf_idf_matrix.transpose(), 10, 0.8)
matches_df = get_matches_df(matches, room_types, top=200)
print(len(matches_df))
# matches_df = matches_df[matches_df['similairity'] < 0.99999]
print(len(matches_df))

# print(matches_df.sample(28))
import pdb; pdb.set_trace()
print(matches_df)
