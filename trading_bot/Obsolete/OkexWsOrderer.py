'''
#OBSOLETE

from Abstract.OkexPrivateChannelConnector import *
from Abstract.OkexTradingParam import *
from Data.PriceQueueManager import *
from abc import ABC, abstractmethod
from time import time
from Utils.Logger import *
from Abstract.UserAccountParam import *

class Orderer(ABC, OkexPrivateChannelConnector):
    def __init__(self,
                 userAccountParam: UserAccountParam,
                 tradingParam: OkexTradingParam,
                 priceManager: PriceQueueManager):
        self.orderLogger = Logger(tradingParam.leader_spot_instId + "/Orders-" + tradingParam.strategyId)
        self.leader_spot_instId = tradingParam.leader_spot_instId
        self.priceManager = priceManager

    async def orderWithLock(self, params):
        async with self.orderLock:
            await self.checkAccountAndOrder(params)

    @abstractmethod
    async def checkAccountAndOrder(self, params):
        pass

    async def pingPosition(self):
        payload = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "balance_and_position"
                    }
                ]
            }
        )
        await self.okexWS.send(payload)

    async def executeBatchOrder(self, args, errorLogger):
        batchPayload = json.dumps({
            "id": str(int(time() * 1000)) + self.leader_spot_instId.split('-')[0][:15],
            "op": "batch-orders",
            "args": args
        })
        self.orderLogger.logSyncWithTimestamp(json.dumps(args))

        if len(args) == 0:
            errorLogger.logSyncClose()
            return

        totalSendTimes = 0
        while True:
            try:
                await self.login()
                await self.okexWS.send(batchPayload)
                totalSendTimes += 1
                if totalSendTimes > 3:
                    errorLogger.logSync("TOO MANY TIMES OF ERROR, QUITTING...")
                    break
                response = await asyncio.wait_for(self.okexWS.recv(),
                                                  timeout=GeneralConfig.SOCKET_URGENT_RECV_TIMEOUT_SEC)
                respObj = json.loads(response)
                if not "data" in respObj:
                    errorLogger.logSync("Reordering: No data in response : " + response)
                    # continue to reorder
                    continue
                else:
                    self.orderLogger.logSyncWithTimestamp("Order Response : " + response, True)
                resendArgs = []
                # check error codes
                for i in range(len(respObj["data"])):
                    singleOrderResp = respObj["data"][i]
                    if not "sCode" in singleOrderResp:
                        errorLogger.logSync(
                            "Reordering: No sCode in response : " + json.dumps(singleOrderResp))
                        resendArgs.append(args[i])
                        continue
                    errorCode = singleOrderResp["sCode"]
                    if not (errorCode == '0' or errorCode in TradingConfig.OKEX_ACCEPTABLE_SCODE):
                        errorLogger.logSync(
                            "Reordering: Error code not acceptable : " + json.dumps(singleOrderResp))
                        resendArgs.append(args[i])
                        continue

                # check whether to reorder
                if len(resendArgs) > 0:
                    errorLogger.logSync(
                        "Reordering: Reorder with new args : " + json.dumps(resendArgs))
                    continue

                break

            except Exception as e:
                GeneralHelper.printErrorStackOnDevPrinterMode()
                errorLogger.logSync(str(e))

        errorLogger.logSyncClose()

    def parseFuturesSwapAbsPos(self, dataObj, posSide, instId) -> int:
        absolutePositionStr = "0"
        posData = dataObj["data"][0]['posData']
        for posObj in posData:
            if "posSide" in posObj and posObj["posSide"] == posSide and posObj["instId"] == instId:
                # Note: okex sell short position is negative number string
                absolutePositionStr = str(abs(int(posObj["pos"])))
                break
        return int(absolutePositionStr)

    async def getLatestSpotPrice(self):
        price = await self.priceManager.getLatestPrice(self.leader_spot_instId)
        return price

    def getSpotArg(self, side, instId, sz):
        return {
            "side": side,
            "instId": instId,
            "tdMode": "cash",
            "ordType": "market",
            "sz": str(sz)
        }

    def getShortArg(self, side, instId, sz):
        return {
            "side": side,
            "instId": instId,
            "posSide": "short",
            "tdMode": "cross",
            "ordType": "market",
            "sz": str(sz)
        }

    def getLongArg(self, side, instId, sz):
        return {
            "side": side,
            "instId": instId,
            "posSide": "long",
            "tdMode": "cross",
            "ordType": "market",
            "sz": str(sz)
        }
'''