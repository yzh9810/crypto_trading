import requests

def sendStackedSignal(instId, decisionInt: int):
    symbol = f"{instId.split('-')[0]}/USD"
    action = None
    side = None
    if decisionInt > 0:
        action = "open"
        side = "buy"
    elif decisionInt == 0:
        action = "close"
        side = "all"
    else:
        action = "open"
        side = "sell"
    fullUrl = "https://alerts.stackedinvest.com/api/v1/alert"
    postBody = {
        "symbol" : symbol,
        "authCode" : "bq4m6R0gSPHX5wW",
        "action": action,
        "side": side,
        "equity": 1,
    }
    resp = requests.post(fullUrl, headers={'Content-Type': 'application/json'}, json=postBody)
    respJson = None
    try:
        respJson = resp.json()
    except:
        return {
            "status": resp.status_code,
            "errMsg": resp.text
        }
    return respJson
