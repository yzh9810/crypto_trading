from .Strategy.ETHXRP import *
from FunctionParams.OkexTradingParam import *
from FunctionParams.StaBasisArbParam import StaBasisArbParam
from Abstract.Commodore import *
from FunctionParams.CommodoreOrderCommand import *
from ..StaBasisArbStrategyEnum import *

class StaBasisArbV0Commodore(Commodore):
    def __init__(self,
                 tradingParam: OkexTradingParam,
                 priceManager: PriceQueueManager,
                 fundamentalFetcher: DayFundamentalFetcher):
        Commodore.__init__(self, tradingParam.leader_spot_instId, StaBasisArbStrategyEnum.StaBasisArbV0.value)
        self.initWithCustomizedParam(tradingParam.customizedParam)
        self.candle_dependent_instIdList = tradingParam.candle_dependent_instIdList
        self.markprice_dependent_instIdList = tradingParam.markprice_dependent_instIdList
        self.priceManager = priceManager
        self.handlerMapping = {
            "ETH-USDT": ETHXRPStrategy
        }
        self.next_state = {
            "previous_status" : "ignore",
            "previous_leverage" : 0,
            "previous_coins_pair": ""
        }
        # initialize state machine
        self.fundamentalFetcher = fundamentalFetcher

    def initWithCustomizedParam(self, customizedParam: StaBasisArbParam):
        self.futureSuffix = customizedParam.futureSuffix

    async def createOrderCommand(self):
        candlePriceDf = await self.priceManager.getPriceDataframe(self.candle_dependent_instIdList[0], 28 * 24 * 60)
        for i in range(1, len(self.candle_dependent_instIdList)):
            dependencyId = self.candle_dependent_instIdList[i]
            dependencyDf = await self.priceManager.getPriceDataframe(dependencyId, 28 * 24 * 60)
            # candlePriceDf get latest # of MAINSTREAM_CANDLE_LIST_DEFAULT_LENGTH items
            candlePriceDf[dependencyId] = dependencyDf[dependencyId]
            candlePriceDf[dependencyId + "-volume"] = dependencyDf[dependencyId + "-volume"]

        dataVerifyJournal = verifyDataValidity(
            self.instId,
            candlePriceDf,
            None
        )

        markPriceMapping = {}
        for dependencyId in self.candle_dependent_instIdList:
            markPriceMapping[dependencyId] = float(candlePriceDf[dependencyId].iloc[-1])

        strategyResp = self.handlerMapping[self.instId](candlePriceDf, markPriceMapping, self.next_state, self.futureSuffix)
        self.updateJournal(dataVerifyJournal + strategyResp["journal"])

        self.next_state = strategyResp["next_state"]

        decisionPayload = strategyResp["decision_payload"]
        decisionPayload["mark_price_mapping"] = markPriceMapping

        oldDecisionPayloadString = self.lastUpdatedDecisionPayloadString
        self.updateDecisionPayloadString(decisionPayload)

        return CommodoreOrderCommand(
            strategyResp["time_to_order"],
            decisionPayload,
            oldDecisionPayloadString
        )