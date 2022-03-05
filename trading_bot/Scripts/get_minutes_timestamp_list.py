import os
import sys
import inspect
from datetime import datetime
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils import TimeHelper
import pandas as pd

priceDf = pd.DataFrame()
currentTimestamp = TimeHelper.getCurrentMinuteTimestamp()
priceTimestampList = [currentTimestamp - i * 60 for i in range(120 * 24 * 60 - 1, -1, -1)]
priceDf["timestamp"] = priceTimestampList
dateList = list(map(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d'), list(priceDf["timestamp"])))
priceDf["readableDates"] = dateList
print(priceDf)

from Data.CandleHistoryFetcher import *
# instIdList = ["BTC-USDT", "ETH-USDT", "LTC-USDT"]
fetcher = CandleHistoryFetcher("BTC-USDT")
tempDf = fetcher.fetchFileDataComplement(120 * 24 * 60)
print(len(tempDf["price"]))
priceDf["BTC-USDT"] = list(tempDf["price"])

import requests
import pandas as pd

# insert your API key here
API_KEY = '1soahyHxlIOjgHCEzZtluSD5AMi'
# make API request
resz = requests.get('https://api.glassnode.com/v1/metrics/market/mvrv_z_score',
    params={'a': 'BTC', 'api_key': API_KEY, 's': str(TimeHelper.getCurrentTimestamp() - 400 * 24 * 60 * 60)})
# convert to pandas dataframe
z_score = pd.read_json(resz.text)
z_score = z_score.rename(columns={"t": "timestamp", "v": "mvrv"})
dateList = list(map(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d'), list(z_score["timestamp"])))
z_score["readableDates"] = dateList
print(z_score)