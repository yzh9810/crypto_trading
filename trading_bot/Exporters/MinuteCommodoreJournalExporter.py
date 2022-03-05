from Abstract.Commodore import Commodore
from Utils.Logger import *
from Utils import GeneralHelper

class MinuteCommodoreJournalExporter():
    def __init__(self, loop, commodore: Commodore):
        self.loop = loop
        self.commodore = commodore
        currentDateString = TimeHelper.getCurrentYearMonthDayString()
        self.exporter = Logger(f"{commodore.getInstId()}/{currentDateString}")
        self.lastCreatedFolderDateString = currentDateString
        loop.create_task(self.decisionExportRoutine())

    async def decisionExportRoutine(self):
        # sleep for two minutes during init
        await asyncio.sleep(60)

        while True:
            currentDateString = TimeHelper.getCurrentYearMonthDayString()

            if self.lastCreatedFolderDateString != currentDateString:
                self.exporter = Logger(f"{self.commodore.getInstId()}/{currentDateString}")
                self.lastCreatedFolderDateString = currentDateString

            self.exporter.logSyncFile(
                TimeHelper.getCurrentYearMonthDayHourString(),
                self.commodore.getLastJournal()
            )
            GeneralHelper.printOnDevPrinterMode("Commodore Journal Updated")
            await asyncio.sleep(60)