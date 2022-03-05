import os
from Configs import GeneralConfig
from Utils import TimeHelper
import pandas as pd
import requests
from time import sleep

class CandleHistoryFetcher:
    # Goal: fast initialization for three stages of mainstream coins:
    # 1. offline file chunk fetched by script
    # 2. api data fetch later than file end
    # 3. api data fetch earlier than file start
    def __init__(self, instId):
        self.instId = instId

    def save(self, df):
        folderPath = os.path.join(os.path.dirname(__file__), "../Data/MinuteHistoricalData")
        try:
            os.mkdir(folderPath)
        except:
            pass
        df.to_csv(path_or_buf=folderPath + "/" + self.instId + ".csv", index=False)

    def savePath(self, df, path):
        filePath = os.path.join(os.path.dirname(__file__), path)
        df.to_csv(path_or_buf=filePath, index=False)

    def verifyReturnValue(self, df, expectedLength):
        # verify length is okay
        if df.shape[0] != expectedLength:
            raise Exception("Fatal Error when initializing price array for: " + self.instId + "; Length mismatch: Got: "
                            + str(df.shape[0]) + ", Expected: " + str(expectedLength))

        # verify lag is acceptable
        curTs = TimeHelper.getCurrentTimestamp() * 1000
        lastTs = int(df["timestamp"].iloc[-1])
        lag = float((curTs - lastTs)) / 60000
        if lag > 3: # max tolerable lag: 3 minutes
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
            print(timestampList[errorIndices[0]])
            raise Exception("Fatal Error when initializing price array for: " + self.instId + "; Error Indices:", errorIndices)
        return

    def fetchHistoryCandleRespObj(self, nextFetchPaginationTimestamp, limit):
        respObj = None
        while True:
            queryInstIdString = "?instId=" + str(self.instId)
            queryPaginationString = "&after=" + str(nextFetchPaginationTimestamp)
            queryLimitString = '&limit=' + str(limit)
            queryGranularityString = '&bar=' + "1m"
            resp = requests.get(
                GeneralConfig.OKEX_V5_REST_CANDLE_HISTORY_ENDPOINT
                + queryInstIdString + queryPaginationString + queryLimitString + queryGranularityString)
            respObj = resp.json()
            if "data" in respObj:
                break
            # sleep 2 seconds before fetching next batch of data
            sleep(2)
        return respObj

    def fetchCandlesMatrix(self, initialFetchPaginationTimestamp, totalFetchLimit):
        candlesMatrix = []
        totalNumFetch = 0

        nextFetchPaginationTimestamp = initialFetchPaginationTimestamp
        while totalNumFetch < totalFetchLimit:
            limit = totalFetchLimit - totalNumFetch
            respObj = self.fetchHistoryCandleRespObj(nextFetchPaginationTimestamp, limit)
            data = respObj["data"][::-1]

            nextFetchPaginationTimestamp = data[0][0]
            matrixToConcat = list(map(lambda x: [x[0], x[4], x[5]], data))
            candlesMatrix = matrixToConcat + candlesMatrix

            totalNumFetch += len(matrixToConcat)

        return candlesMatrix

    def fetchHistoricalDataframe(self, length: int):
        candlesMatrix = self.fetchCandlesMatrix(TimeHelper.getCurrentTimestamp() * 1000, length)
        df = pd.DataFrame(candlesMatrix, columns=['timestamp', 'price', 'volume'])
        return df

    def fetchFileDataComplement(self, totalLength: int):
        filePath = os.path.join(os.path.dirname(__file__), "../Data/MinuteHistoricalData/" + self.instId + ".csv")
        # first fetch data from file
        fileDf = pd.read_csv(filePath)
        fileLength = fileDf.shape[0]
        latestFileTimestamp = fileDf["timestamp"].iloc[-1]

        nextFetchPaginationTimestamp = TimeHelper.getCurrentTimestamp() * 1000
        # fetch one item of latest data as a timestamp jump start
        respObj = self.fetchHistoryCandleRespObj(nextFetchPaginationTimestamp, 1)
        data = respObj["data"][::-1]
        jumpStartCandlesMatrix = list(map(lambda x: [x[0], x[4], x[5]], data))

        nextFetchPaginationTimestamp = data[0][0]
        latestAvailableOkexTimestamp = data[-1][0] # latest timestamp in okex history candle api
        timeDiffBetweenOkexAndFile = int(latestAvailableOkexTimestamp) - int(latestFileTimestamp)
        # numFetchBetweenOkexAndFile is the number of fetches between latest okex timestamp and latest file timestamp
        numFetchBetweenOkexAndFile = int(timeDiffBetweenOkexAndFile / 60000)  # 60 * 1000 = 60000

        # fileLaterTotalFetchLimit: number of fetches needed later than latestFileTimestamp
        # And we have one initial fetch and need to fetch one fewer item now
        fileLaterTotalFetchLimit = min(totalLength, numFetchBetweenOkexAndFile) - 1
        fileLaterCandlesMatrix = self.fetchCandlesMatrix(nextFetchPaginationTimestamp, fileLaterTotalFetchLimit)
        # concat the jump start matrix to the very back
        fileLaterCandlesMatrix =  fileLaterCandlesMatrix + jumpStartCandlesMatrix
        fileLaterDf = pd.DataFrame(fileLaterCandlesMatrix, columns=['timestamp', 'price', 'volume'])

        if totalLength <= numFetchBetweenOkexAndFile:
            self.verifyReturnValue(fileLaterDf, totalLength)
            return fileLaterDf
        elif totalLength > numFetchBetweenOkexAndFile and totalLength <= numFetchBetweenOkexAndFile + fileLength:
            fileAndFileLaterConcatDF = pd.concat([fileDf.tail(totalLength - numFetchBetweenOkexAndFile), fileLaterDf])
            self.verifyReturnValue(fileAndFileLaterConcatDF, totalLength)
            return fileAndFileLaterConcatDF

        # fetch with file earliest timestamp
        nextFetchPaginationTimestamp = fileDf["timestamp"].iloc[0]
        # last stage fetching:
        fileEarlierTotalFetchLimit = totalLength - (numFetchBetweenOkexAndFile + fileLength)
        fileEarlierCandlesMatrix = self.fetchCandlesMatrix(nextFetchPaginationTimestamp, fileEarlierTotalFetchLimit)
        fileEarlierDf = pd.DataFrame(fileEarlierCandlesMatrix, columns=['timestamp', 'price', 'volume'])
        fileThreeStagesConcatMatrix = pd.concat([fileEarlierDf, fileDf, fileLaterDf])
        self.verifyReturnValue(fileThreeStagesConcatMatrix, totalLength)
        return fileThreeStagesConcatMatrix