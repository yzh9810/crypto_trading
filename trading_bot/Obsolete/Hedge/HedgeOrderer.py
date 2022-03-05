# from Abstract.OkexTradingParam import *
# from Data.PriceQueueManager import PriceQueueManager
# from Utils.Logger import *
# from Utils import TimeHelper, GeneralHelper
# from Configs import GeneralConfig, TradingConfig
# from Abstract.OkexTradingParam import *
# import json
# from time import time
# from Abstract.Orderer import Orderer
# import asyncio
#
# class HedgeOrderer(Orderer):
#     def __init__(self,
#                  connectionSemaphore,
#                  tradingParam: OkexTradingParam,
#                  priceManager: PriceQueueManager):
#         Orderer.__init__(self, connectionSemaphore, tradingParam, priceManager)
#         self.tradingParam = tradingParam
#         # otherwise the orderer should abort
#         self.errorLogger = Logger(tradingParam.spot_instId + "/ErrOrder-" + tradingParam.strategyId)
#
#         self.spot_instId = tradingParam.spot_instId
#         self.futures_instId = tradingParam.futures_instId
#         self.futures_coefficient = tradingParam.futures_coefficient
#         self.swap_instId = tradingParam.swap_instId
#         self.swap_coefficient = tradingParam.swap_coefficient
#
#         self.okexWS = None
#
#     async def order(self, decisionPayload):
#         future_position = int(decisionPayload["future_position"])
#         future_decision = int(decisionPayload["future_decision"]) * future_position
#
#         swap_position = int(decisionPayload["swap_position"])
#         swap_decision = int(decisionPayload["swap_decision"]) * swap_position
#
#         spotPrice = await self.getLatestSpotPrice()
#         if GeneralConfig.MODE == "dev":
#             # abondon order on dev mode
#             return
#
#         # decisionInteger remains constant within the scope of function
#         await self.login()
#         totalSendTimes = 0
#         while True:
#             try:
#                 await self.pingPosition()
#                 response = await asyncio.wait_for(self.okexWS.recv(), timeout=GeneralConfig.SOCKET_URGENT_RECV_TIMEOUT_SEC)
#                 dataObj = json.loads(response)
#                 if not "data" in dataObj:
#                     continue
#
#                 totalSendTimes += 1
#                 if totalSendTimes > 3:
#                     self.errorLogger.logSync("TOO MANY TIMES OF ERROR, QUITTING...")
#                     break
#
#                 futuresLongCurPosition = self.retrieveFutureSwapAbsPos(dataObj, "long", self.futures_instId)
#                 futuresShortCurPosition = self.retrieveFutureSwapAbsPos(dataObj, "short", self.futures_instId)
#                 swapLongCurPosition = self.retrieveFutureSwapAbsPos(dataObj, "long", self.swap_instId)
#                 swapShortCurPosition = self.retrieveFutureSwapAbsPos(dataObj, "short", self.swap_instId)
#
#                 futuresExpectedPosition = abs(int(self.futures_coefficient * future_position))
#                 futuresPayloads = self.getPairArgs(
#                     self.futures_instId,
#                     future_decision,
#                     futuresExpectedPosition,
#                     futuresLongCurPosition,
#                     futuresShortCurPosition
#                 )
#                 swapExpectedPosition = abs(int(self.swap_coefficient * swap_position))
#                 swapPayloads = self.getPairArgs(
#                     self.swap_instId,
#                     swap_decision,
#                     swapExpectedPosition,
#                     swapLongCurPosition,
#                     swapShortCurPosition
#                 )
#                 await self.beginOrderProcess(future_decision, swap_decision, futuresPayloads + swapPayloads)
#
#                 break
#             except Exception as e:
#                 GeneralHelper.printErrorStackOnDevPrinterMode()
#                 self.errorLogger.logSync(str(e))
#                 await self.login()
#
#         self.disconnect()
#         self.errorLogger.logSyncClose()
#
#     async def beginOrderProcess(self, futureDecisionInt, swapDecisionInt, payloadList):
#         args = []
#         for payload in payloadList:
#             if not payload is None and float(payload["sz"]) != 0:
#                 args.append(payload)
#         await self.executeBatchOrder(args, self.errorLogger)
#         await self.trackFuturesProfit(futureDecisionInt)
#         await self.trackSwapProfit(swapDecisionInt)
#
#     def getPairArgs(self, instId, decisionInt, expectedPosition, longCurPosition, shortCurPosition):
#         longPayload = None
#         shortPayload = None
#         if decisionInt > 0:
#             longPayload = self.getOpenLongArg(instId, longCurPosition, expectedPosition)
#             shortPayload = self.getCloseShortArg(instId, shortCurPosition)
#         elif decisionInt == 0:
#             longPayload = self.getCloseLongArg(instId, longCurPosition)
#             shortPayload = self.getCloseShortArg(instId, shortCurPosition)
#         else:
#             longPayload = self.getCloseLongArg(instId, longCurPosition)
#             shortPayload = self.getOpenShortArg(instId, shortCurPosition, expectedPosition)
#
#         return [longPayload, shortPayload]
#
#     def getOpenLongArg(self, instId, curPosition: int, expectedPosition: int):
#         side = None
#         size = None
#
#         if curPosition < expectedPosition:
#             side = "buy"
#         elif curPosition > expectedPosition:
#             side = "sell"
#         else:
#             return None
#
#         deltaPosition = abs(expectedPosition - curPosition)
#         return self.getLongArg(
#             side,
#             instId,
#             deltaPosition
#         )
#
#     def getCloseLongArg(self, instId, curPosition: int):
#         if curPosition == 0:
#             return None
#         return self.getLongArg(
#             "sell",
#             instId,
#             curPosition
#         )
#
#     def getOpenShortArg(self, instId, curPosition: int, expectedPosition: int):
#         # IMPORTANT NOTE!!!: SHORT PAYLOAD PRINCIPLE:
#         # PRINCIPLE 1. When you want to increase your position (absolute) of short, you sell them to open short instead of buying them
#         # same thing happens when you want to decrease the position (absolute), you buy them to close and cover short
#         # PRINCIPLE 2. Minimum unit sz param for long short related orders is ALWAYS "1"
#         # this means one unit of the minimum exchanging unit you see on OKEX website
#         # for example: BTC-USDT-SWAP sz "1" in sz param means "0.01" opening units on OKEX website whereas TRX-USDT sz "1" means "1000" on OKEX website
#         side = None
#         size = None
#
#         if curPosition < expectedPosition:
#             # sell short
#             side = "sell"
#         elif curPosition > expectedPosition:
#             # cover short
#             side = "buy"
#         else:
#             return None
#
#         deltaPosition = abs(expectedPosition - curPosition)
#         return self.getShortArg(
#             side,
#             instId,
#             deltaPosition
#         )
#
#     def getCloseShortArg(self, instId, curPosition: int):
#         # cover short
#         if curPosition == 0:
#             return None
#         return self.getShortArg(
#             "buy",
#             instId,
#             curPosition
#         )
#
#     async def trackFuturesProfit(self, decisionInteger):
#         sideStr = ",close,"
#         if decisionInteger > 0:
#             sideStr = ",long,"
#         elif decisionInteger < 0:
#             sideStr = ",short,"
#         spotPrice = await self.fetchLatestOkexPrice(self.futures_instId)
#         trackLogger = Logger(self.spot_instId)
#         trackLogger.logSyncFile(self.futures_instId + "-investment-tracker",
#                                 str(TimeHelper.getCurrentTimestamp()) + sideStr + str(spotPrice))
#
#     async def trackSwapProfit(self, decisionInteger):
#         sideStr = ",close,"
#         if decisionInteger > 0:
#             sideStr = ",long,"
#         elif decisionInteger < 0:
#             sideStr = ",short,"
#         shortPrice = await self.fetchLatestOkexPrice(self.swap_instId)
#         trackLogger = Logger(self.spot_instId)
#         trackLogger.logSyncFile(self.swap_instId + "-investment-tracker",
#                                 str(TimeHelper.getCurrentTimestamp()) + sideStr + str(shortPrice))
