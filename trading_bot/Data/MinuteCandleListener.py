from Abstract.OkexPublicChannelConnector import *
from Configs import GeneralConfig, TradingConfig
from Utils import GeneralHelper, TimeHelper
from Data.CandleHistoryFetcher import *
from Data.CandleRecentFetcher import *
from collections import deque
import json
import pandas as pd
import asyncio
import traceback
# import aiorwlock

class MinuteCandleListener(OkexPublicChannelConnector):
    def __init__(self, loop, instId: str, length:int , connectionSemaphore, connectionLogger):
        OkexPublicChannelConnector.__init__(self, connectionSemaphore)
        self.loop = loop
        self.instId = instId
        self.connectionLogger = connectionLogger
        self.priceQ = None
        self.timestampQ = None
        self.initialize(loop, length)
        # self.rwlock = aiorwlock.RWLock()

    def initialize(self, loop, length: int):
        df = None
        if self.instId in TradingConfig.OKEX_MAINSTREAM_CANDLES_INSTID:
            # IMPORTANT: ONLY MAINSTREAM CRYPTO CURRENCY HAS HISTORY CANDLES ON OKEX !!!
            fetcher = CandleHistoryFetcher(self.instId)
            df = fetcher.fetchFileDataComplement(length)
        else:
            fetcher = CandleRecentFetcher(self.instId)
            df = fetcher.fetchAllCandlesDataframe()
            df = df.tail(length)

        timestampList = [int(int(x) / 1000) for x in list(df["timestamp"])]
        priceList = [float(x) for x in list(df["price"])]
        volumeList = [float(x) for x in list(df["volume"])]

        if len(timestampList) != len(priceList):
            print(self.instId + " Data Listener has mismatched list length!")
            exit(1)

        # timestamp, price, volume
        self.queue = deque([[timestampList[i], priceList[i], volumeList[i]] for i in range(len(timestampList))])

        loop.create_task(self.priceListenRoutine())

    async def priceListenRoutine(self):
        payload = json.dumps(
            {
                "op": "subscribe",
                "args": [{
                    "channel": "candle1m",
                    "instId": self.instId
                }]
            }
        )

        initSocket = True
        while True:
            ReconnectionPerformed = False
            # outter loop: receiving responses for producer dq
            response = None
            while True:
                exceptionRaised = False
                # inner loop: retrying connection & payload sending when error happens
                try:
                    if initSocket:
                        initSocket = False
                        await self.connect()
                        await self.okexWS.send(payload)
                    response = await asyncio.wait_for(self.okexWS.recv(), timeout=GeneralConfig.SOCKET_URGENT_RECV_TIMEOUT_SEC)
                except Exception as e:
                    self.disconnect()
                    exceptionRaised = True
                    # first sleep for one minute then reconnect again using semaphore
                    GeneralHelper.printOnDevPrinterMode("Failed grab data from inst id: " + self.instId)
                    self.loop.create_task(self.logReconnection(""))
                    # self.loop.create_task(self.logReconnection(traceback.format_exc()))
                    await asyncio.sleep(GeneralConfig.SOCKET_URGENT_RECONNECT_HIBERNATE_SEC)
                    await self.connect()
                    await self.okexWS.send(payload)
                    ReconnectionPerformed = True

                if exceptionRaised == False:
                    # break outta loop
                    break

            if response is None:
                continue
            dataObj = json.loads(response)

            if ReconnectionPerformed:
                GeneralHelper.printOnDevPrinterMode("Reconnection Succeeds: " + self.instId)
                self.loop.create_task(self.logRecconectionSucceed())

            if "data" not in dataObj:
                continue

            await self.brokeData(dataObj["data"][0][0], dataObj["data"][0][4], dataObj["data"][0][5])

    async def logReconnection(self, errorString):
        await self.connectionLogger.logFile(
            "connection-" + TimeHelper.getCurrentYearMonthDayString(),
            "[" + self.instId + "," + str(TimeHelper.getCurrentTimestamp())
            + "] Hibernation for next reconnection begins;" + errorString
        )

    async def logRecconectionSucceed(self):
        await self.connectionLogger.logFile(
            "connection-" + TimeHelper.getCurrentYearMonthDayString(),
            "[" + self.instId + "," + str(TimeHelper.getCurrentTimestamp())
            + "] Reconnection Succeeds\n"
        )

    async def brokeData(self, currentTimestampStr, closePriceStr, volString):
        # async with self.rwlock.writer_lock:
            currentTimestamp = int(int(currentTimestampStr) / 1000)
            latestTimestamp = self.queue[-1][0]
            timeDiff = currentTimestamp - latestTimestamp
            minuteDiff = int(timeDiff / 60)

            if minuteDiff == 0:
                # only overwrites last data if the minute is the same
                # print(self.instId, closePriceStr, "overwrites", self.priceQ[-3], self.priceQ[-2], self.priceQ[-1])
                self.queue[-1][1] = float(closePriceStr)
                self.queue[-1][2] = float(volString)
            elif minuteDiff > 0:
                # print(self.instId, "before push", self.priceQ[-3], self.priceQ[-2], self.priceQ[-1])
                for i in range(1, minuteDiff + 1):
                    nextTimestamp = latestTimestamp + 60 * i
                    self.queue.popleft()
                    self.queue.append([nextTimestamp, float(closePriceStr), float(volString)])
                # print(self.instId, "after pushed", self.priceQ[-3], self.priceQ[-2], self.priceQ[-1])

    async def getDataFrame(self, latestLength):
        # Exposed Public API with cleaned column names
        # async with self.rwlock.reader_lock:
            dataList = list(self.queue)
            dataChopped = dataList[-latestLength:]
            priceDf = pd.DataFrame(dataChopped, columns=["timestamp", self.instId, self.instId + "-volume"])
            return priceDf

    async def getLatestPrice(self):
        # Exposed Public API with latest candle closed price
        # async with self.rwlock.reader_lock:
            p = self.queue[-1][1]
            return p