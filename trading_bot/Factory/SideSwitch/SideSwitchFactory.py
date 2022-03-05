from Factory.WarRoom import *
from .SideSwitchOrderer import *
from .EmaFundamentalCommodore.index import *
from .EmaFourlinesV0Commodore.index import *
from Data.DayFundamentalFetcher import *
from .SideSwitchStrategyEnum import *

class SideSwitchFactory:
    def __init__(self,
                 priceManager: PriceQueueManager,
                 fundamentalFetcher: DayFundamentalFetcher):
        self.priceManager = priceManager
        self.fundamentalFetcher = fundamentalFetcher

    def createCommodore(self, tradingParam: OkexTradingParam) -> Commodore:
        instId = tradingParam.leader_spot_instId
        strategyId = tradingParam.strategyId
        commodore = None
        if strategyId == SideSwitchStrategyEnum.EmaFourLinesV0.value:
            commodore = EmaFourlinesV0Commodore(
                tradingParam,
                self.priceManager,
                self.fundamentalFetcher
            )
        elif strategyId == SideSwitchStrategyEnum.EmaFundamental.value:
            commodore = EmaFundamentalCommodore(
                tradingParam,
                self.priceManager,
                self.fundamentalFetcher
            )
        else:
            raise Exception("Fatal Error when initializing SideSwitch Commodore for: "
                            + instId + "; Unknown tradingParam Strategy ID " + str(strategyId))
        return commodore

    def createAccountOrderers(self, tradingParam: OkexTradingParam, accounts) -> List[SideSwitchOrderer]:
        orderers = []
        for acc in accounts:
            orderers.append(SideSwitchOrderer(acc, tradingParam, self.priceManager))
        return orderers