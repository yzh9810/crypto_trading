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
from time import sleep

class MarkPriceListener(OkexPublicChannelConnector):
    def __init__(self, loop, instId: str, connectionSemaphore, connectionLogger):
        OkexPublicChannelConnector.__init__(self, connectionSemaphore)
        self.loop = loop
        self.instId = instId
        self.connectionLogger = connectionLogger
        self.latestPrice = None
        self.initialize(loop)

    def initialize(self, loop):
        while True:
            resp = requests.get(
                GeneralConfig.OKEX_V5_REST_CANDLE_ENDPOINT + "?instId=" + self.instId + "&limit=1"
            )
            respObj = resp.json()
            if "data" in respObj:
                self.latestPrice = float(respObj["data"][0][4])
                break
            sleep(2)
        loop.create_task(self.priceListenRoutine())

    def getLatestMarkPrice(self):
        # Public API
        return self.latestPrice

    async def priceListenRoutine(self):
        payload = json.dumps(
            {
                "op": "subscribe",
                "args": [{
                    "channel": "mark-price",
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
                self.loop.create_task(self.logRecconectionSucceed())

            if "data" not in dataObj:
                continue

            self.latestPrice = float(dataObj["data"][0]["markPx"])

    async def logReconnection(self, errorString):
        await self.connectionLogger.logFile(
            "connection-" + TimeHelper.getCurrentYearMonthDayString(),
            "[" + self.instId + "," + str(TimeHelper.getCurrentTimestamp())
            + "] Hibernation for next reconnection begins" + "\nSource of Exception:" + errorString + "\n"
        )

    async def logRecconectionSucceed(self):
        await self.connectionLogger.logFile(
            "connection-" + TimeHelper.getCurrentYearMonthDayString(),
            "[" + self.instId + "," + str(TimeHelper.getCurrentTimestamp())
            + "] Reconnection Succeeds\n"
        )