# import asyncio
# from Utils import TimeHelper
# from Configs import GeneralConfig
# import json
# import hmac
# import hashlib
# import base64
# import websockets
# 
# class OkexPrivateChannelConnector:
#     def __init__(self, connectionSemaphore):
#         self.okexWS = None
#         self.connectionSemaphore = connectionSemaphore
#
#     async def connect(self):
#         try:
#             async with self.connectionSemaphore:
#                 self.okexWS = await websockets.connect(GeneralConfig.OKEX_V5_WSS_ENDPOINT_PRIVATE)
#                 await asyncio.sleep(GeneralConfig.SOCKET_CONNECTION_BUFFER_SEC)
#         except:
#             await asyncio.sleep(GeneralConfig.SOCKET_CONNECTION_BUFFER_SEC)
#             await self.connect()
#
#     def disconnect(self):
#         self.okexWS = None
#
#     async def login(self):
#         self.okexWS = None # disconnect
#         await self.connect()
#         API_SECRET = GeneralConfig.OKEX_API_SECRET
#         timestamp = str(TimeHelper.getCurrentTimestamp())
#         message = timestamp + GeneralConfig.OKEX_VERIFY_ROUTE
#         encrypted = hmac.new(bytes(API_SECRET, 'latin-1'), msg=bytes(message, 'latin-1'), digestmod=hashlib.sha256)
#         signature = base64.b64encode(encrypted.digest()).decode()
#         payload = json.dumps(
#             {
#                 "op": "login",
#                 "args":
#                     [
#                         {
#                             "apiKey": GeneralConfig.OKEX_API_KEY,
#                             "passphrase": GeneralConfig.OKEX_PASS_PHRASE,
#                             "timestamp": timestamp,
#                             "sign": signature
#                         }
#                     ]
#             }
#         )
#         await self.okexWS.send(payload)
#         await asyncio.wait_for(self.okexWS.recv(), timeout=2)