import json
from time import strptime
import locale

cal_data = None
with open('eventcal.json', 'r+') as json_file:
    cal_data = json.load(json_file)

    locale.setlocale(locale.LC_ALL, ('de_DE', 'UTF-8'))

    cal_data.sort(key=lambda x: (strptime(x['month'], '%b').tm_mon, x['day_of_month']))
    json_file.seek(0)
    json.dump(cal_data, json_file)
    json_file.truncate()
