from FunctionParams.OkexTradingParam import *
from FunctionParams.UserAccountParam import *
from Data.PriceQueueManager import *
from abc import ABC, abstractmethod
from Utils.Logger import *
from Utils import OkexRestHelper
import traceback

class OkexRestOrderer(ABC):
    def __init__(self,
                 userAccountParam: UserAccountParam,
                 tradingParam: OkexTradingParam,
                 priceManager: PriceQueueManager):
        self.leader_spot_instId = tradingParam.leader_spot_instId
        self.userAccountParam = userAccountParam
        self.orderLogger = Logger(f"{userAccountParam.accountId}/{tradingParam.leader_spot_instId}")
        self.orderLock = userAccountParam.orderLock
        self.priceManager = priceManager

    async def orderWithLock(self, decisionPayload):
        async with self.orderLock:
            await self.checkAccountAndOrder(decisionPayload)

    @abstractmethod
    async def checkAccountAndOrder(self, params):
        pass

    def parseBalance(self, dataObj, instId) -> float:
        spotPosition = 0
        balData = dataObj["data"][0]["details"]
        for ccyObj in balData:
            if "ccy" in ccyObj and ccyObj["ccy"] == instId.split("-")[0]:
                spotPosition = float(ccyObj["cashBal"])
                break
        return spotPosition

    def parseFuturesSwapAbsPos(self, dataObj, posSide, instId) -> int:
        absolutePosition = 0
        posData = dataObj["data"]
        for posObj in posData:
            if "posSide" in posObj and posObj["posSide"] == posSide and posObj["instId"] == instId:
                # Note: okex sell short position is negative number string
                absolutePosition = abs(int(posObj["pos"]))
                break
        return absolutePosition

    async def executeBatchOrder(self, args, errorLogger):
        orderFilename = str(TimeHelper.getCurrentTimestamp())
        self.orderLogger.logSyncFile(orderFilename, f"[Payload] : {json.dumps(args)}")
        GeneralHelper.printOnDevPrinterMode(
            "Dev Mode: Order Placement Blocked at "
            + TimeHelper.getLocalTimeFormattedString()
            + "; Context Decision shows as the following\n"
            + f"{self.leader_spot_instId}: {json.dumps(args)}"
        )
        if GeneralConfig.MODE == "dev":
            # abondon order on dev mode
            return

        responses = []
        if len(args) == 0:
            return

        totalSendTimes = 0
        while True:
            try:
                totalSendTimes += 1
                if totalSendTimes > 3:
                    errorLogger.logSync("TOO MANY TIMES OF ERROR, QUITTING...")
                    break
                respObj = OkexRestHelper.sendSignedRequest(self.userAccountParam, "POST", "/api/v5/trade/batch-orders", args)
                response = json.dumps(respObj)
                GeneralHelper.printOnDevPrinterMode(
                    f"{self.leader_spot_instId} order request sent to okex server\nResponse: f{response}"
                )
                if "errMsg" in respObj or not "data" in respObj:
                    errorLogger.logSync("Reordering: No data in response : " + response)
                    continue
                else:
                    responses.append(response)

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
                errorLogger.logSync(f"{str(e)}:\n{traceback.format_exc()}\n")
                await asyncio.sleep(1)

        for response in responses:
            self.orderLogger.logSyncFile(orderFilename, f"[Responses] : {response}")
        self.orderLogger.logSyncClose()

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