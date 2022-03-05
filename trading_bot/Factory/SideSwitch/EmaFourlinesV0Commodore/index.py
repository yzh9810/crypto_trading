from .Strategy.BTC import *
from .Strategy.ETH import *
from .Strategy.LTC import *
from .Strategy.XRP import *
from Abstract.Commodore import *
from FunctionParams.CommodoreOrderCommand import *
from FunctionParams.OkexTradingParam import *
from ..SideSwitchStrategyEnum import *

class EmaFourlinesV0Commodore(Commodore):
    def __init__(self,
                 tradingParam: OkexTradingParam,
                 priceManager: PriceQueueManager,
                 fundamentalFetcher: DayFundamentalFetcher):
        Commodore.__init__(self, tradingParam.leader_spot_instId, SideSwitchStrategyEnum.EmaFourLinesV0.value)
        self.instId = tradingParam.leader_spot_instId
        self.priceManager = priceManager
        self.candle_dependent_instIdList = tradingParam.candle_dependent_instIdList
        self.handlerMapping = {
            "BTC-USDT": BTCStrategy,
            "ETH-USDT": ETHStrategy,
            "LTC-USDT": LTCStrategy,
            "XRP-USDT": XRPStrategy
        }
        self.priceLength = max(TradingConfig.EMA_FOUR_LINES_PERIOD_LIST) + 10
        self.lastUpdatedJournal = ""
        # initialize state machine
        self.fundamentalFetcher = fundamentalFetcher

    async def createOrderCommand(self):
        # return an int enum
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

        strategyResp = self.handlerMapping[self.instId](priceDf)
        self.updateJournal(dataVerifyJournal + strategyResp["journal"])

        oldDecisionPayloadString = self.lastUpdatedDecisionPayloadString
        decisionPayloadChanged = self.updateDecisionPayloadString(strategyResp["decision_payload"])

        return CommodoreOrderCommand(decisionPayloadChanged, strategyResp["decision_payload"], oldDecisionPayloadString)