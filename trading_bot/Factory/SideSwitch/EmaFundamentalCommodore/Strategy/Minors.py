import pandas as pd
import pandas_ta as ta
from Configs import TradingConfig

def MinorCurrencyStrategy(priceDf, fundamentalDf, next_state: dict):
    instId = next_state["instId"]
    ema_5 = ta.ema(priceDf[instId], length=5 * 24 * 60).to_numpy()
    ema_10 = ta.ema(priceDf[instId], length=10 * 24 * 60).to_numpy()
    ema_14 = ta.ema(priceDf[instId], length=14 * 24 * 60).to_numpy()
    ema_28 = ta.ema(priceDf[instId], length=28 * 24 * 60).to_numpy()

    fear_ema_decision = 0
    journal = instId + f" latest => ema_5,10,14,28: {ema_5[-1]}, {ema_10[-1]}, {ema_14[-1]}, {ema_28[-1]}\n"

    if fundamentalDf["fear"].iloc[-1] > 70:
        fear_ema_decision = 1
        journal += "fear > 70\n"
    if fundamentalDf["fear"].iloc[-1] <= 30:
        fear_ema_decision = 0
        journal += "fear <= 30\n"
    if (fundamentalDf["fear"].iloc[-1] <= 70) and (fundamentalDf["fear"].iloc[-1] > 30) and (
        ema_5[-1] > ema_10[-1]) and (ema_14[-1] > ema_28[-1]):
        fear_ema_decision = 1
        journal += "30 < fear <= 70\n"

    return {
        "decision_payload": fear_ema_decision,
        "next_state": {
            "instId": instId
        },
        "journal": journal
    }