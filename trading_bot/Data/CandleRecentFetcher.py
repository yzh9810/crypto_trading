import os
from Configs import GeneralConfig
from Utils import TimeHelper
import pandas as pd
import requests
from Utils import GeneralHelper
from time import sleep

class CandleRecentFetcher:
    def __init__(self, instId):
        # Goal: initialization for minor coins:
        self.instId = instId

    def verifyReturnValue(self, df):
        # verify length is okay
        GeneralHelper.printOnDevPrinterMode("Ministream crypto candles dataframe precheck, total length: " + str(df.shape[0]))

        # verify lag is acceptable
        curTs = TimeHelper.getCurrentTimestamp() * 1000
        lastTs = int(df["timestamp"].iloc[-1])
        lag = float((curTs - lastTs)) / 60000
        if lag > 60: # max tolerable lag: 60 minutes
            raise Exception("Fatal Error when initializing price array for: " + self.instId + "; Too much lag: Got: "
                            + str(lastTs) + ", Expected: " + str(curTs) + ", Total Lag: " + str(lag) + " Min")

        # verify timestamp is increasing by 60000 per row
        timestampList = list(df["timestamp"])
        errorIndices = []
        for i in range(len(timestampList) - 1):
            if int(timestampList[i + 1]) - int(timestampList[i]) != 60 * 1000:
                # i means error indices
                errorIndices.append(i)
        if len(errorIndices) > 0:
            raise Exception("Fatal Error when initializing price array for: " + self.instId + "; Error Indices:", errorIndices)
        return

    def fetchHistoryCandleRespObj(self, nextFetchPaginationTimestamp):
        respObj = None
        while True:
            queryInstIdString = "?instId=" + str(self.instId)
            queryPaginationString = ""
            if nextFetchPaginationTimestamp:
                queryPaginationString = "&after=" + str(nextFetchPaginationTimestamp)
            queryGranularityString = '&bar=' + "1H"
            resp = requests.get(
                GeneralConfig.OKEX_V5_REST_CANDLE_ENDPOINT
                + queryInstIdString + queryPaginationString + queryGranularityString)
            respObj = resp.json()
            if "data" in respObj:
                break
            # sleep 2 seconds before fetching next batch of data
            sleep(2)
        return respObj

    def fetchAllCandlesMatrix(self):
        allCandlesMatrix = []
        nextFetchPaginationTimestamp = None
        while True:
            respObj = self.fetchHistoryCandleRespObj(nextFetchPaginationTimestamp)
            if len(respObj["data"]) == 0:
                # fetched all
                break
            matrixToConcat = []
            for candle in respObj["data"]:
                for i in range(60):
                    ts = str(int(candle[0]) - i * 60000)
                    matrixToConcat.append([ts, candle[4], candle[5]])
            matrixToConcat = matrixToConcat[::-1]
            nextFetchPaginationTimestamp = matrixToConcat[0][0]

            allCandlesMatrix = matrixToConcat + allCandlesMatrix

        return allCandlesMatrix

    def fetchAllCandlesDataframe(self):
        candlesMatrix = self.fetchAllCandlesMatrix()
        df = pd.DataFrame(candlesMatrix, columns=['timestamp', 'price', 'volume'])
        return df