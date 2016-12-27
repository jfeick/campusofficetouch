import json
from time import strptime
from datetime import datetime
import locale

cal_data = None
with open('piazza.json', 'r+') as json_file:
    piazza_data = json.load(json_file)

    #cal_data.sort(key=lambda x: (strptime(x['month'], '%b').tm_mon, x['day_of_month']))
    locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))
    piazza_data.sort(key=lambda x: datetime.strptime(x['date'], '%a, %d %b %Y %H:%M:%S %Z'))
    piazza_data.reverse()
    for item in piazza_data:
        locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))
        dt = datetime.strptime(item['date'],'%a, %d %b %Y %H:%M:%S %Z')
        locale.setlocale(locale.LC_ALL, ('de_DE', 'UTF-8'))
        item['german_date'] = dt.strftime('%-d. %B %Y')
        item['time'] = dt.strftime('%H:%M')
    json_file.seek(0)
    json.dump(piazza_data, json_file)
    json_file.truncate()
