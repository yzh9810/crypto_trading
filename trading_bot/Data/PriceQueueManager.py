from Abstract.OkexPublicChannelConnector import *
from Configs import GeneralConfig, TradingConfig
from Utils import GeneralHelper, TimeHelper
from Data.MinuteCandleListener import *
from Data.MarkPriceListener import *
import asyncio

class PriceQueueManager():
    def __init__(self, loop, candleIdList, markIdList, connectionSecandleMaphore, connectionLogger):
        """
        :param idList: List of instId, length to monitor and maintain price queue
        """
        # max(TradingConfig.EMA_FOUR_LINES_PERIOD_LIST) + 60  # extra 60 for safety concerns
        self.candleMap = {}
        for instId in candleIdList:
            mainstream_candles_list_length = TradingConfig.MAINSTREAM_CANDLE_LIST_LENGTH_MAPPING.get(
                instId,
                TradingConfig.MAINSTREAM_CANDLE_LIST_DEFAULT_LENGTH + 157
            )
            self.candleMap[instId] = MinuteCandleListener(
                loop, instId, mainstream_candles_list_length, connectionSecandleMaphore, connectionLogger
            )

        self.markMap = {}
        for instId in markIdList:
            self.markMap[instId] = MarkPriceListener(
                loop, instId, connectionSecandleMaphore, connectionLogger
            )

    async def getPriceDataframe(self, instId, latestLength):
        if not instId in self.candleMap:
            return None
        dataframe = await self.candleMap[instId].getDataFrame(latestLength)
        return dataframe

    async def getLatestPrice(self, instId):
        if not instId in self.candleMap:
            return None
        latestPrice = await self.candleMap[instId].getLatestPrice()
        return latestPrice

    def getLatestMarkPrice(self, instId):
        return self.markMap[instId].getLatestMarkPrice()