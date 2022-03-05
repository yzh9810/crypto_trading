import asyncio
from Utils import TimeHelper
import os

class Logger:
    def __init__(self, folderName):
        try:
            path = "../Logs/" + folderName
            os.mkdir(os.path.join(os.path.dirname(__file__), path))
        except:
            pass
        self.folderName = folderName
        self.writeLock = asyncio.Lock()
        self.logNamePrefix = None
        # self.periodicLogOpened = None
        self.lastSyncFile = None

    def getFileName(self, namePrefix):
        path = "../Logs/" + self.folderName + "/" + namePrefix + ".txt"
        return os.path.join(os.path.dirname(__file__), path)

    def logSyncFile(self, filename, message):
        file = open(self.getFileName(filename), "a")
        file.write(message + '\n')
        file.close()

    async def logFile(self, filename, message):
        async with self.writeLock:
            file = open(self.getFileName(filename), "a")
            file.write(message + '\n')
            file.close()

    def logSync(self, message, close=False):
        f = None
        if self.lastSyncFile is None:
            currentLogPrefix = str(TimeHelper.getCurrentTimestamp())
            f = open(self.getFileName(currentLogPrefix), "a")
        else:
            f = self.lastSyncFile
        f.write(message + '\n')
        if close:
            f.close()
            self.lastSyncFile = None
        else:
            self.lastSyncFile = f

    def logSyncClose(self):
        if not self.lastSyncFile is None:
            self.logSync("--LOGGING END--", True)

    def logSyncWithTimestamp(self, message, close=False):
        self.logSync("[" + str(TimeHelper.getCurrentTimestamp()) + "] " + message, close)

    # async def log(self, message, duration="day"):
    #     currentLogPrefix = None
    #     if duration == "hour":
    #         currentLogPrefix = TimeHelper.getCurrentYearMonthDayHourString()
    #     else:
    #         currentLogPrefix = TimeHelper.getCurrentYearMonthDayString()
    #     async with self.writeLock:
    #         if self.periodicLogOpened is None or self.logNamePrefix is None:
    #             # lazy initialization
    #             self.logNamePrefix = currentLogPrefix
    #             self.periodicLogOpened = open(self.getFileName(currentLogPrefix), "a")
    #         if currentLogPrefix != self.logNamePrefix:
    #             # new day's coming up
    #             self.periodicLogOpened.close()
    #             self.logNamePrefix = currentLogPrefix
    #             self.periodicLogOpened = open(self.getFileName(currentLogPrefix), "a")
    #         self.periodicLogOpened.write(message + '\n')
    #
    # async def logWithTimestamp(self, message):
    #     await self.log("[" + str(TimeHelper.getCurrentTimestamp()) + "] " + message)