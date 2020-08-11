import json

import pandas as pd


def load_from_files():
    with open('TICK_exmpl.txt') as TICKs:
        TICKs = [line.rstrip() for line in TICKs]


def decoder_from_js(data, element):
    data_json = json.loads(data.text)
    ready_data = data_json[element]['data']
    return ready_data


def calc_percentage_change(numbers):
    change_series = pd.Series(numbers)
    pct_change = change_series.pct_change()
    return pct_change
