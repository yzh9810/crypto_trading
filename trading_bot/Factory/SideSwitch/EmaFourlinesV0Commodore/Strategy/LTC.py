import pandas as pd
import pandas_ta as ta
from Configs import TradingConfig

def LTCStrategy(priceDf):
    journal = ""

    periodList = TradingConfig.EMA_FOUR_LINES_PERIOD_LIST
    df = priceDf
    btc_ema_2 = list(ta.ema(df["BTC-USDT"], length=periodList[0]))[-1]
    btc_ema_5 = list(ta.ema(df["BTC-USDT"], length=periodList[1]))[-1]

    btc_diff_2_5 = btc_ema_2 - btc_ema_5

    btc_ema_14 = list(ta.ema(df["BTC-USDT"], length=periodList[2]))[-1]
    btc_ema_28 = list(ta.ema(df["BTC-USDT"], length=periodList[3]))[-1]

    btc_diff_14_28 = btc_ema_14 - btc_ema_28

    ltc_ema_2 = list(ta.ema(df["LTC-USDT"], length=periodList[0]))[-1]
    ltc_ema_5 = list(ta.ema(df["LTC-USDT"], length=periodList[1]))[-1]

    ltc_diff_2_5 = ltc_ema_2 - ltc_ema_5

    ltc_ema_14 = list(ta.ema(df["LTC-USDT"], length=periodList[2]))[-1]
    ltc_ema_28 = list(ta.ema(df["LTC-USDT"], length=periodList[3]))[-1]
    ltc_diff_14_28 = ltc_ema_14 - ltc_ema_28
    journal += f"btc latest ema2,5,14,28: {btc_ema_2}, {btc_ema_5}, {btc_ema_14}, {btc_ema_28}\n"
    journal += f"ltc latest ema2,5,14,28: {ltc_ema_2}, {ltc_ema_5}, {ltc_ema_14}, {ltc_ema_28}\n"

    btc_decision = 0
    ltc_decision = 0
    if (btc_diff_2_5 > 0 and btc_diff_14_28 > 0):
        btc_decision = 1

    if (btc_diff_2_5 < 0 and btc_diff_14_28 < 0):
        btc_decision = -1

    if (ltc_diff_2_5 > 0 and ltc_diff_14_28 > 0):
        ltc_decision = 1

    if (ltc_diff_2_5 < 0 and ltc_diff_14_28 < 0):
        ltc_decision = -1

    decision_payload = 0
    if btc_decision == 1 and ltc_decision == -1:
        journal += "btc_decision == 1 and ltc_decision == -1\n"
        decision_payload = 0
    elif btc_decision == -1 and ltc_decision == 1:
        journal += "btc_decision == -1 and ltc_decision == 1\n"
        decision_payload = 0
    elif btc_decision == 1:
        journal += "btc_decision == 1\n"
        decision_payload = 1
    elif ltc_decision == 1:
        journal += "ltc_decision == 1\n"
        decision_payload = 1
    elif btc_decision == -1:
        journal += "btc_decision == -1\n"
        decision_payload = -1
    elif ltc_decision == -1:
        journal += "ltc_decision == -1\n"
        decision_payload = -1

    return {
        "decision_payload": decision_payload,
        "journal": str(decision_payload) + ',' + journal
    }