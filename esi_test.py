import pandas as pd
import requests
from pprint import pprint
from datetime import date, datetime, timedelta
import pickle

requestHeaders = {"User-Agent":"Asteroid appraiser by vjackrussel@gmail.com"}
the_forge_region_id = 10000002
type_id_input = 28432
result = requests.get(f"https://esi.evetech.net/latest/markets/{the_forge_region_id}/history/?datasource=tranquility&type_id={type_id_input}", headers=requestHeaders).json()[-2]

pprint(result)
print(type(result))
print(result['date'], type(result['date']))
test_date = datetime.strptime(result['date'], "%Y-%m-%d").date()
print(test_date)
datetime_delta = date.today() - test_date
print(datetime_delta.days, type(datetime_delta.days))
