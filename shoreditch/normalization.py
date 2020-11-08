import pandas as pd
import re

# TODO: if I switch to a parser the code in these 2 functions is 
# going to be redundant - i forgot I was doing this at all honestly
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
    return df


def key_for(title):
    df = pd.DataFrame.from_dict({'title': [title]})
    res = normalize(df)
    return res['normalized'][0]
