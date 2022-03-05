import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Data.CandleHistoryFetcher import *
instIdList = [
    "ETH-USDT-220325",
    "ETH-USDT-SWAP",
    "TRX-USDT-220325",
    "TRX-USDT-SWAP",
    "XRP-USDT-220325",
    "XRP-USDT-SWAP",
]
for instId in instIdList:
    fetcher = CandleHistoryFetcher(instId)
    df = fetcher.fetchHistoricalDataframe(30 * 24 * 60)
    fetcher.save(df)