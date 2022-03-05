import requests
import hmac
import hashlib
import base64
import json
from Configs import GeneralConfig
from FunctionParams.UserAccountParam import *
from datetime import datetime

def sendSignedRequest(userAccountParam: UserAccountParam, method, path, postBody=None):
    timestamp = datetime.utcnow().isoformat()[:-3] + 'Z'
    bodyString = ""
    if method == "POST" and postBody:
        bodyString = json.dumps(postBody)

    message = str(timestamp) + str.upper(method) + path + bodyString
    digest = hmac.new(
        bytes(userAccountParam.apiSecret, encoding='utf-8'),
        msg=bytes(message, 'utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(digest)

    headers = {
        "OK-ACCESS-KEY": userAccountParam.apiKey,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": userAccountParam.passphrase
    }

    fullUrl = GeneralConfig.OKEX_ENDPOINT + path
    resp = None
    if method == "POST":
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        resp = requests.post(fullUrl, headers=headers, json=postBody)
    else:
        resp = requests.get(fullUrl, headers=headers)
    respJson = None
    try:
        respJson = resp.json()
    except:
        return {
            "status": resp.status_code,
            "errMsg": resp.text
        }
    return respJson

def sendCoinsBalanceQuery(userAccountParam: UserAccountParam, coinList):
    ccyList = [instId.split('-')[0] for instId in coinList]
    queryString = "?ccy=" + ','.join(ccyList)
    fullPath = GeneralConfig.OKEX_V5_BALANCE_PATH + queryString
    respJson = sendSignedRequest(userAccountParam, "GET", fullPath)
    return respJson

def sendSwapFuturesPositionsQuery(userAccountParam: UserAccountParam, idList):
    queryString = "?instId=" + ','.join(idList)
    fullPath = GeneralConfig.OKEX_V5_POSITION_PATH + queryString
    respJson = sendSignedRequest(userAccountParam, "GET", fullPath)
    return respJson