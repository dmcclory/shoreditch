import pandas as pd
import re

def extract_annotations(series):
    return series.str.extract(r'.*\((.*)\)\w*$')[0].fillna('')

def chop_annotations(series):
    return series.str.replace(r'\((.*)\)\w*$', '')

STOP_WORDS = ['in', 'on', 'the', 'of']

def remove_stop_words(series):
    return series.str.split(' ').apply(lambda l: ' '.join(w for w in l if w not in STOP_WORDS))

def add_season_suffix(keys, suffixes):
    x = pd.DataFrame.from_dict({'protokey': keys, 'annotation': suffixes}, dtype='string')
    return x.apply(
        lambda r: r['protokey'] + ' ' + r['annotation'] if re.match(r'^s\d+$', r['annotation']) else r['protokey'], axis=1
    )

def normalize(df):
    column_label = 'title'
    annotations = extract_annotations(df[column_label])
    chopped = chop_annotations(df[column_label])
    stripped = chopped.str.strip()
    lower = stripped.str.lower()
    destopped = remove_stop_words(lower)
    seasoned = add_season_suffix(destopped, annotations)
    df['normalized'] =  seasoned
    df['annotations'] = annotations
    return df


def key_for(title):
    df = pd.DataFrame.from_dict({'title': [title]})
    res = normalize(df)
    return res['normalized'][0]


def get_best_key(matches_df, key):
    right_side = matches_df[matches_df['left_side'] == key].sort_values('similarity', ascending=False).head(1)['right_side']
    try:
        return right_side.values[0]
    except:
        return None
