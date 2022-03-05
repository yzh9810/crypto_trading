from Abstract.Commodore import Commodore
from Utils.Logger import *
from Utils import GeneralHelper

class HourCommodoreJournalExporter():
    def __init__(self, loop, commodore: Commodore):
        self.loop = loop
        self.commodore = commodore
        self.exporter = Logger(commodore.getInstId() + "/CommodoreJournal-" + commodore.getStrategyId())
        loop.create_task(self.decisionExportRoutine())

    async def decisionExportRoutine(self):
        # sleep for two minutes during init
        await asyncio.sleep(2 * 60)

        while True:
            # sleep for an hour: 60 * 60 seconds
            self.loop.create_task(self.exporter.logFile(
                "commodoreJournal-" + TimeHelper.getCurrentYearMonthDayString(),
                self.commodore.getLastJournal()
            ))
            GeneralHelper.printOnDevPrinterMode("Commodore Journal Updated")
            await asyncio.sleep(60 * 60)