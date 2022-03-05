from Abstract.Commodore import *
from Abstract.OkexRestOrderer import *
from FunctionParams.OkexTradingParam import *
from typing import List
from Notifiers.Mailers import *
from FunctionParams.CommodoreOrderCommand import *
import asyncio
from time import time

class WarRoom():
    def __init__(self,
                 loop,
                 commodore: Commodore,
                 orderers: List[OkexRestOrderer],
                 okexTradingParam: OkexTradingParam,
                 priceManager: PriceQueueManager):
        self.loop = loop
        self.instId = okexTradingParam.leader_spot_instId
        self.okexTradingParam = okexTradingParam
        self.mailer = Mailer()
        self.orderers = orderers
        self.decisionChangeLogger = Logger(okexTradingParam.leader_spot_instId)
        self.decisionChangeFileName = "decision-change-" + self.instId + "-" + okexTradingParam.strategyId

        self.priceManager = priceManager
        self.commodore = commodore # all hail Commodore Almighty!!!
        loop.create_task(self.initialize(loop))

    async def initialize(self, loop):
        startTime = time()
        initialOrderCommand = await self.newOrderCommand()
        endTime = time()
        initTimeTaken = int(endTime - startTime)
        loop.create_task(self.analyzeRoutine(initTimeTaken, initialOrderCommand))

    async def analyzeRoutine(self, initTimeTaken: int, initialOrderCommand: CommodoreOrderCommand):
        initialDecisionPayload = initialOrderCommand.decisionPayload
        # initial order for adjusting position
        GeneralHelper.printOnDevPrinterMode(
            "[" + self.instId + f"] Initial Decision at {GeneralHelper.TimeHelper.getLocalTimeFormattedString()}: "
            + json.dumps(initialDecisionPayload)
        )
        title = "[Okex Trading Bot] Initial Decision"
        body = self.commodore.getInstId() + ", " + self.commodore.getStrategyId() + '\n' + json.dumps(initialDecisionPayload)
        if initialOrderCommand.isTimeToOrder:
            for orderer in self.orderers:
                self.loop.create_task(orderer.orderWithLock(initialDecisionPayload))
        latestSpotPrice = await self.priceManager.getLatestPrice(self.instId)
        self.loop.create_task(self.mailer.sendMail(title, body))
        self.loop.create_task(self.logDecision(initialDecisionPayload, latestSpotPrice))

        sleepTime = max(60 - initTimeTaken, 0)
        await asyncio.sleep(sleepTime)

        while True:
            startTime = time()
            commandStartTimestamp = str(TimeHelper.getCurrentTimestamp())
            newOrderCommand = await self.newOrderCommand()
            commandEndTimestamp = str(TimeHelper.getCurrentTimestamp())

            if newOrderCommand.isTimeToOrder:
                newDecisionPayload = newOrderCommand.decisionPayload
                oldDecisionPayloadString = newOrderCommand.oldDecisionPayloadString
                newDecisionPayloadString = json.dumps(newDecisionPayload)
                latestSpotPrice = await self.priceManager.getLatestPrice(self.instId)
                GeneralHelper.printOnDevPrinterMode(
                    "[" + self.instId + f"] Current Decision has been changed from {newOrderCommand.oldDecisionPayloadString} at {GeneralHelper.TimeHelper.getLocalTimeFormattedString()} to: "
                    + newDecisionPayloadString
                )
                for orderer in self.orderers:
                    self.loop.create_task(orderer.orderWithLock(newDecisionPayload))

                title = f"[Okex Trading Bot] Incoming Position Adjustment at {commandStartTimestamp}~{commandEndTimestamp}"
                body = self.commodore.getInstId() + ", " + self.commodore.getStrategyId() + "\nFROM:\n" + oldDecisionPayloadString + "\nTO:\n" + newDecisionPayloadString
                GeneralHelper.printOnDevPrinterMode(title + '\n' + body)
                self.loop.create_task(self.mailer.sendMail(title, body))
                self.loop.create_task(self.logDecision(newDecisionPayload, latestSpotPrice))

            endTime = time()
            elaspedTime = int(endTime - startTime)
            sleepTime = max(self.okexTradingParam.warRoomGap - elaspedTime, 5)

            await asyncio.sleep(sleepTime)

    async def newOrderCommand(self) -> CommodoreOrderCommand:
        orderCommand = await self.commodore.createOrderCommand()
        return orderCommand

    async def logDecision(self, decisionPayload, latestPrice):
        self.decisionChangeLogger.logSyncFile(
            self.decisionChangeFileName,
            str(TimeHelper.getCurrentTimestamp()) + ", "
            + str(latestPrice) + ", "
            + json.dumps(decisionPayload)
        )