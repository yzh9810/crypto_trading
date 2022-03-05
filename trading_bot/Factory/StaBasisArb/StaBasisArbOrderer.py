from FunctionParams.StaBasisArbParam import StaBasisArbParam
from Data.PriceQueueManager import PriceQueueManager
from Utils.Logger import Logger
from Utils import TimeHelper, GeneralHelper
from FunctionParams.OkexTradingParam import OkexTradingParam
from FunctionParams.UserAccountParam import UserAccountParam
from Abstract.OkexRestOrderer import OkexRestOrderer
from Utils import OkexRestHelper
from .StaBasisExpectedPositionCalculators.index import *
import json
import asyncio
import traceback

class StaBasisArbOrderer(OkexRestOrderer):
    def __init__(self,
        userAccountParam: UserAccountParam,
        tradingParam: OkexTradingParam,
        priceManager: PriceQueueManager
    ):
        OkexRestOrderer.__init__(self, userAccountParam, tradingParam, priceManager)
        self.tradingParam = tradingParam
        self.initWithCustomizedParam(tradingParam.customizedParam)
        self.next_state = {
            "ignore_position": 0
        }
        # otherwise the orderer should abort
        self.errorLogger = Logger(userAccountParam.accountId + "/ErrOrder-" + tradingParam.leader_spot_instId)

    def initWithCustomizedParam(self, customizedParam: StaBasisArbParam):
        self.tradeSpotIdList = customizedParam.tradeSpotIdList
        self.futureSuffix = customizedParam.futureSuffix
        self.ctValMapping = customizedParam.ctValMapping
        self.tradeSwapFuturesList = []
        for spot_instId in self.tradeSpotIdList:
            self.tradeSwapFuturesList.append(spot_instId + self.futureSuffix)
            self.tradeSwapFuturesList.append(spot_instId + "-SWAP")

    async def checkAccountAndOrder(self, decisionPayload):
        totalSendTimes = 0
        while True:
            try:
                totalSendTimes += 1
                if totalSendTimes > 3:
                    self.errorLogger.logSync("ACCOUNT CHECKED TOO MANY TIMES OF ERROR, QUITTING...")
                    break

                balanceRespObj = OkexRestHelper.sendCoinsBalanceQuery(self.userAccountParam, ["USDT"])
                positionRespObj = OkexRestHelper.sendSwapFuturesPositionsQuery(self.userAccountParam, self.tradeSwapFuturesList)
                if "errMsg" in balanceRespObj \
                    or "errMsg" in positionRespObj \
                    or balanceRespObj["code"] != '0'\
                    or positionRespObj["code"] != '0':
                    self.errorLogger.logSync(
                        f"Account Info Response Invalid:\n{json.dumps(balanceRespObj)}\n{json.dumps(positionRespObj)}"
                    )
                    continue

                usdt = self.parseBalance(balanceRespObj, "USDT")
                order_settings = decisionPayload["order_settings"]
                markPriceMapping = decisionPayload["mark_price_mapping"]

                position_calculator = getCalculator(self.leader_spot_instId)
                calculatedPositionMapping = position_calculator(
                    usdt, markPriceMapping, self.next_state, order_settings, self.futureSuffix
                )
                self.orderLogger.logSyncFile(
                    "calculator-result",
                    f"{str(TimeHelper.getCurrentTimestamp())}: {json.dumps(calculatedPositionMapping)} <= " +
                    f"{str(usdt)}, {json.dumps(markPriceMapping)}, {json.dumps(self.next_state)}, {json.dumps(order_settings)}, {self.futureSuffix}"
                )
                self.next_state = calculatedPositionMapping["next_state"]

                payloadList = []
                for spot_instId in self.tradeSpotIdList:
                    futures_instId = spot_instId + self.futureSuffix
                    swap_instId = spot_instId + "-SWAP"

                    expectedPosition = int(calculatedPositionMapping[spot_instId] / self.ctValMapping[spot_instId])
                    futuresLongCurPosition = self.parseFuturesSwapAbsPos(positionRespObj, "long", futures_instId)
                    futuresShortCurPosition = self.parseFuturesSwapAbsPos(positionRespObj, "short", futures_instId)
                    swapLongCurPosition = self.parseFuturesSwapAbsPos(positionRespObj, "long", swap_instId)
                    swapShortCurPosition = self.parseFuturesSwapAbsPos(positionRespObj, "short", swap_instId)

                    future_decision = decisionPayload[spot_instId]["future_decision"]
                    payloadList += self.getPairArgs(
                        futures_instId,
                        future_decision,
                        expectedPosition,
                        futuresLongCurPosition,
                        futuresShortCurPosition
                    )

                    swap_decision = decisionPayload[spot_instId]["swap_decision"]
                    payloadList += self.getPairArgs(
                        swap_instId,
                        swap_decision,
                        expectedPosition,
                        swapLongCurPosition,
                        swapShortCurPosition
                    )

                await self.beginOrderProcess(payloadList)

                break
            except Exception as e:
                GeneralHelper.printErrorStackOnDevPrinterMode()
                self.errorLogger.logSync(f"{str(e)}:\n{traceback.format_exc()}\n")
                await asyncio.sleep(1)

        self.errorLogger.logSyncClose()

    async def beginOrderProcess(self, payloadList):
        args = []
        for payload in payloadList:
            if not payload is None and float(payload["sz"]) != 0:
                args.append(payload)
        await self.executeBatchOrder(args, self.errorLogger)

    def getPairArgs(self, instId, decisionInt, expectedPosition, longCurPosition, shortCurPosition):
        longPayload = None
        shortPayload = None
        if decisionInt > 0:
            longPayload = self.getOpenLongArg(instId, longCurPosition, expectedPosition)
            shortPayload = self.getCloseShortArg(instId, shortCurPosition)
        elif decisionInt == 0:
            longPayload = self.getCloseLongArg(instId, longCurPosition)
            shortPayload = self.getCloseShortArg(instId, shortCurPosition)
        else:
            longPayload = self.getCloseLongArg(instId, longCurPosition)
            shortPayload = self.getOpenShortArg(instId, shortCurPosition, expectedPosition)

        return [longPayload, shortPayload]

    def getOpenLongArg(self, instId, curPosition: int, expectedPosition: int):
        side = None
        size = None

        if curPosition < expectedPosition:
            side = "buy"
        elif curPosition > expectedPosition:
            side = "sell"
        else:
            return None

        deltaPosition = abs(expectedPosition - curPosition)
        return self.getLongArg(
            side,
            instId,
            deltaPosition
        )

    def getCloseLongArg(self, instId, curPosition: int):
        if curPosition == 0:
            return None
        return self.getLongArg(
            "sell",
            instId,
            curPosition
        )

    def getOpenShortArg(self, instId, curPosition: int, expectedPosition: int):
        # IMPORTANT NOTE!!!: SHORT PAYLOAD PRINCIPLE:
        # PRINCIPLE 1. When you want to increase your position (absolute) of short, you sell them to open short instead of buying them
        # same thing happens when you want to decrease the position (absolute), you buy them to close and cover short
        # PRINCIPLE 2. Minimum unit sz param for long short related orders is ALWAYS "1"
        # this means one unit of the minimum exchanging unit you see on OKEX website
        # for example: BTC-USDT-SWAP sz "1" in sz param means "0.01" opening units on OKEX website whereas TRX-USDT sz "1" means "1000" on OKEX website
        side = None
        size = None

        if curPosition < expectedPosition:
            # sell short
            side = "sell"
        elif curPosition > expectedPosition:
            # cover short
            side = "buy"
        else:
            return None

        deltaPosition = abs(expectedPosition - curPosition)
        return self.getShortArg(
            side,
            instId,
            deltaPosition
        )

    def getCloseShortArg(self, instId, curPosition: int):
        # cover short
        if curPosition == 0:
            return None
        return self.getShortArg(
            "buy",
            instId,
            curPosition
        )