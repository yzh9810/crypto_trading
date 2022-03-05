import pandas as pd
import pandas_ta as ta
from Configs import TradingConfig

def XRPStrategy(priceDf):
    journal = ""

    periodList = TradingConfig.EMA_FOUR_LINES_PERIOD_LIST
    df = priceDf
    btc_ema_2 = list(ta.ema(df["BTC-USDT"], length=periodList[0]))[-1]
    btc_ema_5 = list(ta.ema(df["BTC-USDT"], length=periodList[1]))[-1]

    btc_diff_2_5 = btc_ema_2 - btc_ema_5

    btc_ema_14 = list(ta.ema(df["BTC-USDT"], length=periodList[2]))[-1]
    btc_ema_28 = list(ta.ema(df["BTC-USDT"], length=periodList[3]))[-1]

    btc_diff_14_28 = btc_ema_14 - btc_ema_28

    xrp_ema_2 = list(ta.ema(df["XRP-USDT"], length=periodList[0]))[-1]
    xrp_ema_5 = list(ta.ema(df["XRP-USDT"], length=periodList[1]))[-1]

    xrp_diff_2_5 = xrp_ema_2 - xrp_ema_5

    xrp_ema_14 = list(ta.ema(df["XRP-USDT"], length=periodList[2]))[-1]
    xrp_ema_28 = list(ta.ema(df["XRP-USDT"], length=periodList[3]))[-1]
    xrp_diff_14_28 = xrp_ema_14 - xrp_ema_28
    journal += f"btc latest ema2,5,14,28: {btc_ema_2}, {btc_ema_5}, {btc_ema_14}, {btc_ema_28}\n"
    journal += f"xrp latest ema2,5,14,28: {xrp_ema_2}, {xrp_ema_5}, {xrp_ema_14}, {xrp_ema_28}\n"

    btc_decision = 0
    xrp_decision = 0
    if (btc_diff_2_5 > 0 and btc_diff_14_28 > 0):
        btc_decision = 1

    if (btc_diff_2_5 < 0 and btc_diff_14_28 < 0):
        btc_decision = -1

    if (xrp_diff_2_5 > 0 and xrp_diff_14_28 > 0):
        xrp_decision = 1

    if (xrp_diff_2_5 < 0 and xrp_diff_14_28 < 0):
        xrp_decision = -1

    decision_payload = 0
    if btc_decision == 1 and xrp_decision == -1:
        journal += "btc_decision == 1 and xrp_decision == -1\n"
        decision_payload = 0
    elif btc_decision == -1 and xrp_decision == 1:
        journal += "btc_decision == -1 and xrp_decision == 1\n"
        decision_payload = 0
    elif btc_decision == 1:
        journal += "btc_decision == 1\n"
        decision_payload = 1
    elif xrp_decision == 1:
        journal += "xrp_decision == 1\n"
        decision_payload = 1
    elif btc_decision == -1:
        journal += "btc_decision == -1\n"
        decision_payload = -1
    elif xrp_decision == -1:
        journal += "xrp_decision == -1\n"
        decision_payload = -1

    return {
        "decision_payload": decision_payload,
        "journal": str(decision_payload) + '<=>' + journal
    }