from Utils import GeneralHelper
from Configs import GeneralConfig
from Utils.Logger import *
import requests
import pandas as pd

class DayFundamentalFetcher():
    def __init__(self, loop):
        self.loop = loop
        self.fundamentalDf = None
        # initialization
        self.fetchFundamental()
        # loop.create_task(self.fundamentalFetchRoutine())

    def getFundamental(self):
        return self.fundamentalDf

    def fetchFundamental(self):
        respf = requests.get('https://api.alternative.me/fng/?limit=450')
        respfearList = respf.json()['data'][::-1]
        fearList = []
        for item in respfearList:
            fearList.append([int(item["timestamp"]), int(item["value"])])
        fundamentalDf = pd.DataFrame(fearList, columns=["timestamp", "fear"])

        resz = requests.get(GeneralConfig.GLASSNODE_MVRV_ZSCORE_ENDPOINT,
                            params={'a': 'BTC', 'api_key': GeneralConfig.GLASSNODE_API_KEY,
                                    's': str(TimeHelper.getCurrentTimestamp() - 451 * 24 * 60 * 60)})
        respMvrvList = resz.json()
        tsMvrvMapping = {}
        for item in respMvrvList:
            tsMvrvMapping[int(item['t'])] = float(item['v'])

        mvrvList = []
        for i in range(fundamentalDf.shape[0]):
            timestamp = int(fundamentalDf["timestamp"].iloc[i])
            nextMvrv = tsMvrvMapping.get(timestamp, self.lastMvrvAvailable(mvrvList))
            mvrvList.append(nextMvrv)
        fundamentalDf["mvrv"] = mvrvList

        self.fundamentalDf = fundamentalDf
        GeneralHelper.printOnDevPrinterMode("Fundamental Fetched for " + TimeHelper.getCurrentYearMonthDayString())

    def lastMvrvAvailable(self, mvrvList):
        if len(mvrvList) == 0:
            return 2.0
        return mvrvList[-1]

    async def fundamentalFetchRoutine(self):
        while True:
            # sleep for 2 hours per check
            await asyncio.sleep(2 * 60 * 60)
            self.fetchFundamental()