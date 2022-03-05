import pandas as pd
import pandas_ta as ta
from Configs import TradingConfig

def BTCStrategy(priceDf):
    journal = ""

    periodList = TradingConfig.EMA_FOUR_LINES_PERIOD_LIST
    df = priceDf
    btc_ema_2 = list(ta.ema(df["BTC-USDT"], length=periodList[0]))[-1]
    btc_ema_5 = list(ta.ema(df["BTC-USDT"], length=periodList[1]))[-1]

    diff_2_5 = btc_ema_2 - btc_ema_5

    btc_ema_14 = list(ta.ema(df["BTC-USDT"], length=periodList[2]))[-1]
    btc_ema_28 = list(ta.ema(df["BTC-USDT"], length=periodList[3]))[-1]
    diff_14_28 = btc_ema_14 - btc_ema_28

    decision_payload = 0

    if diff_2_5 >= 0 and diff_14_28 >= 0:
        journal += "diff_2_5 >= 0 and diff_14_28 >= 0\n"
        decision_payload = 1

    if diff_2_5 < 0 and diff_14_28 >= 0:
        journal += "diff_2_5 < 0 and diff_14_28 >= 0\n"
        decision_payload = 0

    if diff_2_5 >= 0 and diff_14_28 < 0:
        journal += "diff_2_5 >= 0 and diff_14_28 < 0\n"
        decision_payload = 0

    if diff_2_5 < 0 and diff_14_28 < 0:
        journal += "diff_2_5 < 0 and diff_14_28 < 0\n"
        decision_payload = -1

    return {
        "decision_payload": decision_payload,
        "journal": str(decision_payload) + ',' + journal
    }