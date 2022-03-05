import pandas as pd
import pandas_ta as ta
from Configs import TradingConfig

def ETHStrategy(priceDf):
    journal = ""

    periodList = TradingConfig.EMA_FOUR_LINES_PERIOD_LIST
    df = priceDf
    btc_ema_2 = list(ta.ema(df["BTC-USDT"], length=periodList[0]))[-1]
    btc_ema_5 = list(ta.ema(df["BTC-USDT"], length=periodList[1]))[-1]

    btc_diff_2_5 = btc_ema_2 - btc_ema_5

    btc_ema_14 = list(ta.ema(df["BTC-USDT"], length=periodList[2]))[-1]
    btc_ema_28 = list(ta.ema(df["BTC-USDT"], length=periodList[3]))[-1]

    btc_diff_14_28 = btc_ema_14 - btc_ema_28

    eth_ema_2 = list(ta.ema(df["ETH-USDT"], length=periodList[0]))[-1]
    eth_ema_5 = list(ta.ema(df["ETH-USDT"], length=periodList[1]))[-1]

    eth_diff_2_5 = eth_ema_2 - eth_ema_5

    eth_ema_14 = list(ta.ema(df["ETH-USDT"], length=periodList[2]))[-1]
    eth_ema_28 = list(ta.ema(df["ETH-USDT"], length=periodList[3]))[-1]
    eth_diff_14_28 = eth_ema_14 - eth_ema_28

    btc_decision = 0
    eth_decision = 0
    if (btc_diff_2_5 > 0 and btc_diff_14_28 > 0):
        btc_decision = 1

    if (btc_diff_2_5 < 0 and btc_diff_14_28 < 0):
        btc_decision = -1

    if (eth_diff_2_5 > 0 and eth_diff_14_28 > 0):
        eth_decision = 1

    if (eth_diff_2_5 < 0 and eth_diff_14_28 < 0):
        eth_decision = -1

    decision_payload = 0

    if btc_decision == 1 and eth_decision == -1:
        journal += "btc_decision == 1 and eth_decision == -1\n"
        decision_payload = 0
    elif btc_decision == -1 and eth_decision == 1:
        journal += "btc_decision == -1 and eth_decision == 1\n"
        decision_payload = 0
    elif btc_decision == 1:
        journal += "btc_decision == 1\n"
        decision_payload = 1
    elif eth_decision == 1:
        journal += "eth_decision == 1\n"
        decision_payload = 1
    elif btc_decision == -1:
        journal += " btc_decision == -1\n"
        decision_payload = -1
    elif eth_decision == -1:
        journal += " eth_decision == -1\n"
        decision_payload = -1

    return {
        "decision_payload": decision_payload,
        "journal": str(decision_payload) + ',' + journal
    }