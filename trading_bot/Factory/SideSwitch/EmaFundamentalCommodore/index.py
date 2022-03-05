from .Strategy.BTC import *
from .Strategy.ETH import *
from .Strategy.LTC import *
from .Strategy.Minors import *
from Data.ValidityVerifier import *
from Data.PriceQueueManager import PriceQueueManager
from Data.DayFundamentalFetcher import DayFundamentalFetcher
from FunctionParams.OkexTradingParam import *
from Abstract.Commodore import Commodore
from FunctionParams.CommodoreOrderCommand import CommodoreOrderCommand
from ..SideSwitchStrategyEnum import *
import json

class EmaFundamentalCommodore(Commodore):
    def __init__(self,
                 tradingParam: OkexTradingParam,
                 priceManager: PriceQueueManager,
                 fundamentalFetcher: DayFundamentalFetcher):
        Commodore.__init__(self, tradingParam.leader_spot_instId, SideSwitchStrategyEnum.EmaFundamental.value)
        self.instId = tradingParam.leader_spot_instId
        self.priceManager = priceManager
        self.candle_dependent_instIdList = tradingParam.candle_dependent_instIdList
        self.handlerMapping = {
            "BTC-USDT": BTCStrategy,
            "ETH-USDT": ETHStrategy,
            "LTC-USDT": LTCStrategy
        }
        self.priceLength = TradingConfig.MAINSTREAM_CANDLE_LIST_DEFAULT_LENGTH
        self.lastUpdatedJournal = ""
        # initialize state machine
        self.next_state = {
            "instId": tradingParam.leader_spot_instId,
            "mvrv_state" : "Ignore",
            "mvrv_realized_price" : 0,
            "mvrv_start_time" : 0,
            "lefttime" : 0
        }
        self.fundamentalFetcher = fundamentalFetcher

    async def createOrderCommand(self):
        fundamentalDf = self.fundamentalFetcher.getFundamental()

        priceDf = await self.priceManager.getPriceDataframe(self.instId, self.priceLength)

        for dependencyId in self.candle_dependent_instIdList:
            dependencyDf = await self.priceManager.getPriceDataframe(dependencyId, self.priceLength)
            # priceDf get latest # of MAINSTREAM_CANDLE_LIST_DEFAULT_LENGTH items
            priceDf[dependencyId] = dependencyDf[dependencyId]

        dataVerifyJournal = verifyDataValidity(
            self.instId,
            priceDf,
            fundamentalDf
        )

        # minor strategy by default
        foo = self.handlerMapping.get(self.instId, MinorCurrencyStrategy)
        strategyResp = foo(priceDf, fundamentalDf, self.next_state)
        self.next_state = strategyResp["next_state"]
        self.updateJournal(dataVerifyJournal + strategyResp["journal"])

        oldDecisionPayloadString = self.lastUpdatedDecisionPayloadString
        decisionPayloadChanged = self.updateDecisionPayloadString(strategyResp["decision_payload"])

        return CommodoreOrderCommand(decisionPayloadChanged, strategyResp["decision_payload"], oldDecisionPayloadString)