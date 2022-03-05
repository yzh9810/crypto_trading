import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Configs import GeneralConfig
from FunctionParams.UserAccountParam import *
from Utils import OkexRestHelper
import json

account1Param = UserAccountParam(
    "Testing",
    "6295a5f5-fb9b-4dfb-98f8-b34801ce7bc1",
    "4BD9C0EA5563A6626159DCA0721CB8BD",
    GeneralConfig.OKEX_PASS_PHRASE
)

account2Param = UserAccountParam(
    "Testing",
    "2541ecd0-88e2-4171-a5c0-dbfdd3579168",
    "22881A9F1C6BD6630F183A4DEAAAC25E",
    GeneralConfig.OKEX_PASS_PHRASE
)
#
#
def parseBalance(dataObj, instId) -> float:
    spotPositionStr = "0"
    balData = dataObj["data"][0]["details"]
    for ccyObj in balData:
        if "ccy" in ccyObj and ccyObj["ccy"] == instId.split("-")[0]:
            spotPositionStr = ccyObj["cashBal"]
            break
    return float(spotPositionStr)

print("original account")
print(OkexRestHelper.sendSwapFuturesPositionsQuery(account1Param, ["TRX-USDT-SWAP"]))
print("new account")
print(OkexRestHelper.sendSwapFuturesPositionsQuery(account2Param, ["TRX-USDT-SWAP"]))

# respObj = OkexRestHelper.sendSignedRequest(
#     userAccountParam,
#     "POST",
#     "/api/v5/trade/batch-orders",
#     [
#         {
#             "side": "buy",
#             "instId": "BTC-USDT",
#             "tdMode": "cash",
#             "ordType": "market",
#             "sz": "1"
#         },
#         {
#             "side": "sell",
#             "instId": "LTC-USDT",
#             "posSide": "short",
#             "tdMode": "cross",
#             "ordType": "market",
#             "sz": "1"
#         }
#     ]
# )
#
# print(respObj)

# for i in range(10):
#     respObj = OkexRestHelper.sendSignedRequest(
#         userAccountParam,
#         "POST",
#         "/api/v5/trade/batch-orders",
#         [
#             {
#                 "side": "buy",
#                 "instId": "BTC-USDT",
#                 "tdMode": "cash",
#                 "ordType": "market",
#                 "sz": "0.5"
#             }
#         ]
#     )
#     print(i)
#     print(respObj)