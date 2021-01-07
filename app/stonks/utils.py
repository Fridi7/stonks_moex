import json


def decoder_from_js(data, element):
    data_json = json.loads(data.text)
    ready_data = data_json[element]['data']
    return ready_data


def calc_percentage_change(numbers):
    pct_change = (numbers[1] - numbers[0]) / numbers[0]
    format_pct_change = float('{:.5f}'.format(pct_change))
    return format_pct_change
