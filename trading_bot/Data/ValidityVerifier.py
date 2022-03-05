from Utils import TimeHelper
from Utils.Logger import *

def verifyDataValidity(instId, priceDf, fundamentalDf=None):
    # verify timestamp is increasing by 60000 per row
    journal = ""
    priceTimestampList = list(priceDf["timestamp"])
    errorIndices = []
    for i in range(len(priceTimestampList) - 1):
        if int(priceTimestampList[i + 1]) - int(priceTimestampList[i]) != 60:
            # i means error indices
            errorIndices.append(i)
    if len(errorIndices) > 0:
        errorLogger = Logger(instId + "/ErrCommodore")
        errorIndicesString = [str(err) for err in errorIndices]
        errorLogger.logSync("Error Price Timestamp List Indices: " + ",".join(errorIndicesString))
        print(instId + " Error Price Timestamp List Indices in Commodore!")
        exit(1)
    curTs = TimeHelper.getCurrentTimestamp()
    lastPriceTs = int(priceTimestampList[-1])
    lag = float((curTs - lastPriceTs)) / 60
    if lag > 5:  # max tolerable lag: 3 minutes
        newString = "Lag of price detected! Got: " \
                    + str(lastPriceTs) + ", Expected: " + str(curTs) + ", Total Lag: " + str(lag) + " Min\n"
        journal += newString

    journal += f"Price List Checked, Latest: {lastPriceTs}\n"

    if fundamentalDf is None:
        return journal

    fundamentalTimestampList = list(fundamentalDf["timestamp"])
    for i in range(len(fundamentalTimestampList) - 1):
        if int(fundamentalTimestampList[i + 1]) - int(fundamentalTimestampList[i]) != 24 * 60 * 60:
            # i means error indices
            errorIndices.append(i)
    if len(errorIndices) > 0:
        errorLogger = Logger(instId + "/ErrCommodore")
        errorIndicesString = [str(err) for err in errorIndices]
        errorLogger.logSync("Error Fundamental Timestamp List Indices: " + ",".join(errorIndicesString))
        print(instId + " Error Fundamental Timestamp List Indices in Commodore!")
        exit(1)

    lastFundamentalTs = int(fundamentalTimestampList[-1])
    lag = float((curTs - lastFundamentalTs)) / (60 * 60)
    if lag > 30:  # max tolerable lag: 30 hours
        newString = "Lag of fundamental detected! Got: " \
                    + str(lastFundamentalTs) + ", Expected: " + str(curTs) + ", Total Lag: " + str(lag) + " Hours\n"
        journal += newString

    lastThreeFundamentalRows = str(fundamentalTimestampList[-1]) \
                               + ", mvrv:" + str(list(fundamentalDf["mvrv"])[-1]) \
                               + ", fear:" + str(list(fundamentalDf["fear"])[-1]) + '\n'
    journal += lastThreeFundamentalRows

    return journal