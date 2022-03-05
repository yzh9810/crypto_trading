from Abstract.OkexRestOrderer import OkexRestOrderer
from Data.PriceQueueManager import PriceQueueManager
from Utils.Logger import *
from Utils import TimeHelper, GeneralHelper, OkexRestHelper
from FunctionParams.OkexTradingParam import OkexTradingParam
from FunctionParams.UserAccountParam import UserAccountParam
from FunctionParams.SideSwitchParam import SideSwitchParam
from Configs import GeneralConfig, TradingConfig
import json
import asyncio
import traceback

class SideSwitchOrderer(OkexRestOrderer):
    # side swap between spot and swap
    def __init__(self,
                 userAccountParam: UserAccountParam,
                 tradingParam: OkexTradingParam,
                 priceManager: PriceQueueManager):
        OkexRestOrderer.__init__(self, userAccountParam, tradingParam, priceManager)
        self.tradingParam = tradingParam
        self.initWithCustomizedParam(tradingParam.customizedParam)
        # otherwise the orderer should abort
        self.errorLogger = Logger(userAccountParam.accountId + "/ErrOrder-" + tradingParam.leader_spot_instId)
        self.leader_spot_instId = tradingParam.leader_spot_instId

    def initWithCustomizedParam(self, customizedParam: SideSwitchParam):
        self.short_instId = customizedParam.short_instId
        self.short_coefficient = customizedParam.short_coefficient
        self.ctValMinSwapUnit = customizedParam.ctValMinSwapUnit

    async def checkAccountAndOrder(self, decisionPayload):
        decisionInteger = int(decisionPayload)
        spotPrice = await self.priceManager.getLatestPrice(self.leader_spot_instId)

        # decisionInteger remains constant within the scope of function
        totalSendTimes = 0
        while True:
            try:
                totalSendTimes += 1
                if totalSendTimes > 3:
                    self.errorLogger.logSync("ACCOUNT CHECKED TOO MANY TIMES OF ERROR, QUITTING...")
                    break
                # wait for position
                balanceRespObj = OkexRestHelper.sendCoinsBalanceQuery(self.userAccountParam, [self.leader_spot_instId])
                positionRespObj = OkexRestHelper.sendSwapFuturesPositionsQuery(
                    self.userAccountParam,
                    [self.short_instId]
                )
                if "errMsg" in balanceRespObj \
                    or "errMsg" in positionRespObj \
                    or balanceRespObj["code"] != '0' \
                    or positionRespObj["code"] != '0':
                    self.errorLogger.logSync(
                        f"Account Info Response Invalid:\n{json.dumps(balanceRespObj)}\n{json.dumps(positionRespObj)}"
                    )
                    continue

                spotPosition = self.parseBalance(balanceRespObj, self.leader_spot_instId)
                shortAbsolutePosition = self.parseFuturesSwapAbsPos(positionRespObj, "short", self.short_instId)

                # if prediction is price increase (optimistic, greedy):
                # then we buy spot and buy all shorts back
                # if prediction is price decrease (pessimisitic):
                # then we sell all spot and sell shorts

                if decisionInteger == 1:
                    # TODO: revise our coefficient based on current USDT * buy_spot_cash_purchase_ratio
                    # IMPORTANT NOTE:
                    # SPOT POSITION AT ENUM 1 SHOULD HAVE THE SAME POSITION AS SHORT POSITION AT ENUM -1
                    expectedSpotPosition = self.ctValMinSwapUnit * self.short_coefficient
                    spotPayload = self.getOpenSpotArg(spotPrice, spotPosition, expectedSpotPosition)
                    shortPayload = self.getCloseShortArg(shortAbsolutePosition)
                    await self.beginOrderProcess(spotPayload, shortPayload)

                elif decisionInteger == -1:
                    # TODO: revise our coefficient based on current USDT * buy_spot_cash_purchase_ratio
                    spotPayload = self.getCloseSpotArg(
                        spotPosition
                    )
                    shortPayload = self.getOpenShortArg(
                        shortAbsolutePosition,
                        max(1, int(self.short_coefficient))
                    )
                    await self.beginOrderProcess(spotPayload, shortPayload)

                else:
                    # CLOSE & LIQUIDATE EVERYTHING
                    spotPayload = self.getCloseSpotArg(spotPosition)
                    shortPayload = self.getCloseShortArg(shortAbsolutePosition)
                    await self.beginOrderProcess(spotPayload, shortPayload)

                break
            except Exception as e:
                GeneralHelper.printErrorStackOnDevPrinterMode()
                self.errorLogger.logSync(f"{str(e)}:\n{traceback.format_exc()}\n")
                await asyncio.sleep(1)

        self.errorLogger.logSyncClose()

    async def beginOrderProcess(self, spotPayload, shortPayload):
        args = []
        if not spotPayload is None and float(spotPayload["sz"]) != 0:
            args.append(spotPayload)
        if not shortPayload is None and float(shortPayload["sz"]) != 0:
            args.append(shortPayload)

        await self.executeBatchOrder(args, self.errorLogger)

    def getOpenSpotArg(self, curPrice: float, curPosition: float, expectedPosition: float):
        side = None
        size = None

        if curPosition < expectedPosition:
            side = "buy"
            deltaPosition = expectedPosition - curPosition
            size = GeneralHelper.formattedFloatString(round(curPrice * deltaPosition, 1))
        elif curPosition > expectedPosition:
            side = "sell"
            size = curPosition - expectedPosition
        else:
            return None

        return self.getSpotArg(
            side,
            self.leader_spot_instId,
            size
        )

    def getCloseSpotArg(self, curPosition: float):
        return self.getSpotArg(
            "sell",
            self.leader_spot_instId,
            GeneralHelper.formattedFloatString(curPosition)
        )

    def getOpenShortArg(self, curPosition: int, expectedPosition: int):
        # IMPORTANT NOTE!!!: SHORT PAYLOAD PRINCIPLE:
        # PRINCIPLE 1. When you want to increase your position (absolute) of short, you sell them to open short instead of buying them
        # same thing happens when you want to decrease the position (absolute), you buy them to close and cover short
        # PRINCIPLE 2. Minimum unit sz param for long short related orders is ALWAYS "1"
        # this means one unit of the minimum exchanging unit you see on OKEX website
        # for example: BTC-USDT-SWAP sz "1" in sz param means "0.01" opening units on OKEX website whereas TRX-USDT sz "1" means "1000" on OKEX website
        if self.short_instId == "":
            return None
        if not self.leader_spot_instId in TradingConfig.SIDESWITCH_SHORT_ENABLE_LIST:
            return None
        side = None
        size = None

        if curPosition < expectedPosition:
            # sell short
            side = "sell"
            deltaPosition = expectedPosition - curPosition
        elif curPosition > expectedPosition:
            # cover short
            side = "buy"
            deltaPosition = curPosition - expectedPosition
        else:
            return None

        return self.getShortArg(
            side,
            self.short_instId,
            deltaPosition
        )

    def getCloseShortArg(self, curPosition: int):
        if self.short_instId == "":
            return None
        if not self.leader_spot_instId in TradingConfig.SIDESWITCH_SHORT_ENABLE_LIST:
            return None
        # cover short
        if curPosition == 0:
            return None
        return self.getShortArg(
            "buy",
            self.short_instId,
            curPosition
        )