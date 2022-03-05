from Configs import GeneralConfig
from Utils import GeneralHelper
from Utils.Logger import *

class HourPositionExporter(OkexPrivateChannelConnector):
    def __init__(self, loop, connectionSemaphore):
        OkexPrivateChannelConnector.__init__(self, connectionSemaphore)
        self.loop = loop
        self.exporter = Logger("Position")
        if GeneralConfig.MODE != "dev":
            loop.create_task(self.positionExportRoutine())

    async def positionExportRoutine(self):
        # sleep for two minutes during init
        await asyncio.sleep(2 * 60)

        while True:
            # sleep for 60 * 60 seconds
            await self.login()
            payload = json.dumps(
                {
                    "op": "subscribe",
                    "args": [
                        {
                            "channel": "balance_and_position"
                        }
                    ]
                }
            )
            await self.okexWS.send(payload)

            writeString = "NONE"
            totalSendTimes = 0
            while True:
                try:
                    response = await asyncio.wait_for(self.okexWS.recv(),
                                                      timeout=GeneralConfig.SOCKET_RECV_TIMEOUT_SEC)
                    dataObj = json.loads(response)
                    if not "data" in dataObj:
                        continue
                    totalSendTimes += 1
                    if totalSendTimes > 3:
                        writeString = "TOO MANY TIMES OF ERROR, QUITTING..."
                        break
                    writeString = response
                    GeneralHelper.printOnDevPrinterMode("Position Fetched!")

                    break
                except Exception as e:
                    GeneralHelper.printOnDevPrinterMode("Position Fetch Error!")
                    await self.login()
                    await self.okexWS.send(payload)

            self.disconnect()

            self.exporter.logSyncFile(
                "position-" + TimeHelper.getCurrentYearMonthDayString(),
                TimeHelper.getCurrentYearMonthDayHourString() + ","
                + str(TimeHelper.getCurrentTimestamp()) + "\n"
                + writeString + "\n"
            )
            # sleep for an hour
            await asyncio.sleep(60 * 60)