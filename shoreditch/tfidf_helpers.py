import pandas as pd
import re

def get_best_key(matches_df, key):
    right_side = matches_df[matches_df['left_side'] == key].sort_values('similarity', ascending=False).head(1)['right_side']
    try:
        return right_side.values[0]
    except:
        return None
