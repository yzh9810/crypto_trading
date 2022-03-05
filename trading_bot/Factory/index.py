from Factory.WarRoom import *
from Factory.StaBasisArb.StaBasisArbFactory import StaBasisArbFactory
from Factory.SideSwitch.SideSwitchFactory import SideSwitchFactory
from Factory.TradingTypeEnum import *
from Data.DayFundamentalFetcher import *
from Data.PriceQueueManager import *
from Exporters.HourCommodoreJournalExporter import *
from Exporters.MinuteCommodoreJournalExporter import *
import asyncio

class WarRoomFactory:
    def __init__(self,
                 loop,
                 priceManager: PriceQueueManager,
                 fundamentalFetcher: DayFundamentalFetcher):
        self.loop = loop
        self.priceManager = priceManager

        self.strategyRegistrarMapping = {
            TradingTypeEnum.StaBasisArb.value.StaBasisArbV0: TradingTypeEnum.StaBasisArb,
            TradingTypeEnum.SideSwitch.value.EmaFourLinesV0: TradingTypeEnum.SideSwitch,
            TradingTypeEnum.SideSwitch.value.EmaFundamental: TradingTypeEnum.SideSwitch
        }
        self.staBasisArbFactory = StaBasisArbFactory(self.priceManager, fundamentalFetcher)
        self.sideSwitchFactory = SideSwitchFactory(self.priceManager, fundamentalFetcher)

    def initWarRoom(self, okexTradingParam, accounts):
        factory = None
        tradingType = self.strategyRegistrarMapping[okexTradingParam.strategyEnum]
        if tradingType == TradingTypeEnum.StaBasisArb:
            factory = self.staBasisArbFactory
        elif tradingType == TradingTypeEnum.SideSwitch:
            factory = self.sideSwitchFactory
        else:
            raise Exception("Fatal Error when initializing War Room Factory; Unknown tradingParam Trading Type " + str(str(tradingType)))
        commodore = factory.createCommodore(okexTradingParam)
        orderers = factory.createAccountOrderers(okexTradingParam, accounts)
        MinuteCommodoreJournalExporter(self.loop, commodore)
        WarRoom(self.loop, commodore, orderers, okexTradingParam, self.priceManager)