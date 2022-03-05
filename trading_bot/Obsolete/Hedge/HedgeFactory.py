from Factory.WarRoom import *
from .HedgeV0Commodore.index import *
from .HedgeOrderer import *
from .HedgeStrategyEnum import *
from Data.DayFundamentalFetcher import *

class HedgeFactory:
    def __init__(self,
                 connectionSemaphore,
                 priceManager: PriceQueueManager,
                 fundamentalFetcher: DayFundamentalFetcher):
        self.connectionSemaphore = connectionSemaphore
        self.priceManager = priceManager
        self.fundamentalFetcher = fundamentalFetcher

    def createOperatingUnits(self, tradingParam: OkexTradingParam, simulation):
        instId = tradingParam.spot_instId
        strategyId = tradingParam.strategyId
        orderer = None
        if not simulation:
            orderer = HedgeOrderer(self.connectionSemaphore, tradingParam, self.priceManager)
        commodore = None
        if strategyId == HedgeStrategyEnum.HedgeV0.value:
            commodore = HedgeV0Commodore(
                self.priceManager,
                self.fundamentalFetcher,
                instId)
        else:
            raise Exception("Fatal Error when initializing Hedge Commodore for: "
                            + instId + "; Unknown tradingParam Strategy ID " + str(strategyId))
        return (commodore, orderer)