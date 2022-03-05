from Data.ValidityVerifier import *
from Data.PriceQueueManager import *
from Data.DayFundamentalFetcher import *
from Configs import GeneralConfig
import json
from Utils import TimeHelper
from Utils.Logger import *
import pandas as pd
from abc import ABC, abstractmethod

class Commodore(ABC):
    def __init__(self, instId, strategyId: str):
        self.instId = instId
        self.strategyId = strategyId
        self.lastUpdatedJournal = ""
        self.lastUpdatedDecisionPayloadString = ""

    @abstractmethod
    async def createOrderCommand(self):
        pass

    def updateDecisionPayloadString(self, decisionPayload):
        payloadString = json.dumps(decisionPayload)
        if self.lastUpdatedDecisionPayloadString != payloadString:
            self.lastUpdatedDecisionPayloadString = payloadString
            return True
        return False

    def getInstId(self):
        return self.instId

    def getStrategyId(self):
        return self.strategyId

    def getLastJournal(self):
        return self.lastUpdatedJournal

    def updateJournal(self, string: str):
        h1 = TimeHelper.getCurrentYearMonthDayHourString()
        h2 = str(TimeHelper.getCurrentTimestamp())
        self.lastUpdatedJournal = h1 + "," + h2 + "\n" + string