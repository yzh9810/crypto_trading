import asyncio
from Configs import GeneralConfig
import json
import websockets

class OkexPublicChannelConnector:
    def __init__(self, connectionSemaphore):
        self.okexWS = None
        self.connectionSemaphore = connectionSemaphore

    async def connect(self):
        async with self.connectionSemaphore:
            self.okexWS = await websockets.connect(GeneralConfig.OKEX_V5_WSS_ENDPOINT_PUBLIC)
            await asyncio.sleep(GeneralConfig.SOCKET_CONNECTION_BUFFER_SEC)

    async def ping(self, payloadObject):
        await self.connect()
        await self.okexWS.send(json.dumps(payloadObject))

    def disconnect(self):
        self.okexWS = None