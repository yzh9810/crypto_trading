from Factory.WarRoom import *
from .StaBasisArbV0Commodore.index import *
from .StaBasisArbOrderer import *
from .StaBasisArbStrategyEnum import *
from Data.DayFundamentalFetcher import *

class StaBasisArbFactory():
    def __init__(self,
                 priceManager: PriceQueueManager,
                 fundamentalFetcher: DayFundamentalFetcher):
        self.priceManager = priceManager
        self.fundamentalFetcher = fundamentalFetcher

    def createCommodore(self, tradingParam: OkexTradingParam) -> Commodore:
        instId = tradingParam.leader_spot_instId
        strategyId = tradingParam.strategyId
        commodore = None
        if strategyId == StaBasisArbStrategyEnum.StaBasisArbV0.value:
            commodore = StaBasisArbV0Commodore(
                tradingParam,
                self.priceManager,
                self.fundamentalFetcher
            )
        else:
            raise Exception("Fatal Error when initializing Arbitrage Commodore for: "
                            + instId + "; Unknown tradingParam Strategy ID " + str(strategyId))
        return commodore

    def createAccountOrderers(self, tradingParam: OkexTradingParam, accounts) -> List[StaBasisArbOrderer]:
        orderers = []
        for acc in accounts:
            orderers.append(StaBasisArbOrderer(acc, tradingParam, self.priceManager))
        return orderers

