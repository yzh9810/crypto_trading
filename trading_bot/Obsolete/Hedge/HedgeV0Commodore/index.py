from .Strategy.BTC import *
from .Strategy.ETH import *
from .Strategy.LTC import *
from Data.ValidityVerifier import *
from Data.PriceQueueManager import *
from Data.DayFundamentalFetcher import *
from Utils import TimeHelper
from Abstract.Commodore import *
from ..HedgeStrategyEnum import *

class HedgeV0Commodore(Commodore):
    def __init__(self,
                 priceManager: PriceQueueManager,
                 fundamentalFetcher: DayFundamentalFetcher,
                 instId="BTC-USDT"):
        Commodore.__init__(self, instId, HedgeStrategyEnum.HedgeV0.value)
        self.instId = instId
        self.priceManager = priceManager
        self.handlerMapping = {
            "BTC-USDT": BTCStrategy,
            "ETH-USDT": None,
            "LTC-USDT": None
        }
        self.priceLength = TradingConfig.MAINSTREAM_CANDLE_LIST_LENGTH + 10
        self.lastUpdatedJournal = ""
        # initialize state machine
        self.fundamentalFetcher = fundamentalFetcher

    async def makeInvestmentDecision(self, analysis_instId_dependency: list):
        # return an int enum
        fundamentalDf = self.fundamentalFetcher.getFundamental()

        priceDf = await self.priceManager.getPriceDataframe(self.instId, self.priceLength)

        for dependencyId in analysis_instId_dependency:
            dependencyDf = await self.priceManager.getPriceDataframe(dependencyId, self.priceLength)
            # priceDf get latest # of MAINSTREAM_CANDLE_LIST_LENGTH items
            priceDf[dependencyId] = dependencyDf[dependencyId]
            priceDf[dependencyId + "-volume"] = dependencyDf[dependencyId + "-volume"]

        dataVerifyJournal = verifyDataValidity(
            self.instId,
            priceDf,
            fundamentalDf
        )

        resp = self.handlerMapping[self.instId](priceDf, fundamentalDf)
        self.updateJournal(dataVerifyJournal)

        self.logDecisionChange(resp, priceDf[self.instId].iloc[-1])
        return resp