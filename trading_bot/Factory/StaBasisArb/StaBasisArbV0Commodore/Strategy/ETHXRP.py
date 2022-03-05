import pandas_ta as ta
from Configs import TradingConfig
from Utils.StrategyHelper import *
from Utils.Logger import *
import pandas as pd
import numpy as np


def Checking_Arbitrage_Opportunity(eth_basis, xrp_basis, ema, previous_status, previous_leverage):
    eth_future_decision = None
    eth_swap_decision = None
    xrp_future_decision = None
    xrp_swap_decision = None

    current_status = None
    current_leverage = None

    change_position = False
    if previous_status == "ignore":
        if eth_basis - xrp_basis - ema >= 0.005:
            if eth_basis - xrp_basis - ema >= 0.12:
                current_leverage = 20
            elif eth_basis - xrp_basis - ema >= 0.06:
                current_leverage = 16
            elif eth_basis - xrp_basis - ema >= 0.04:
                current_leverage = 14
            elif eth_basis - xrp_basis - ema >= 0.03:
                current_leverage = 13
            elif eth_basis - xrp_basis - ema >= 0.02:
                current_leverage = 12
            elif eth_basis - xrp_basis - ema >= 0.015:
                current_leverage = 10
            elif eth_basis - xrp_basis - ema >= 0.01:
                current_leverage = 7
            elif eth_basis - xrp_basis - ema >= 0.005:
                current_leverage = 3

            change_position = True

            current_status = "short"
            eth_future_decision = -1
            eth_swap_decision = 1
            xrp_future_decision = 1
            xrp_swap_decision = -1

        elif eth_basis - xrp_basis - ema <= -0.005:
            if eth_basis - xrp_basis - ema <= -0.12:
                current_leverage = 20
            elif eth_basis - xrp_basis - ema <= -0.06:
                current_leverage = 16
            elif eth_basis - xrp_basis - ema <= -0.04:
                current_leverage = 14
            elif eth_basis - xrp_basis - ema <= -0.03:
                current_leverage = 13
            elif eth_basis - xrp_basis - ema <= -0.02:
                current_leverage = 12
            elif eth_basis - xrp_basis - ema <= -0.015:
                current_leverage = 10
            elif eth_basis - xrp_basis - ema <= -0.01:
                current_leverage = 7
            elif eth_basis - xrp_basis - ema <= -0.005:
                current_leverage = 3

            change_position = True
            current_status = "long"
            eth_future_decision = 1
            eth_swap_decision = -1
            xrp_future_decision = -1
            xrp_swap_decision = 1
        else:
            current_status = "ignore"
            eth_future_decision = 0
            eth_swap_decision = 0
            xrp_future_decision = 0
            xrp_swap_decision = 0
            current_leverage = 0

    elif previous_status == "short":
        if eth_basis - xrp_basis - ema >= 0.12:
            current_leverage = 20
        elif eth_basis - xrp_basis - ema >= 0.06:
            current_leverage = 16
        elif eth_basis - xrp_basis - ema >= 0.04:
            current_leverage = 14
        elif eth_basis - xrp_basis - ema >= 0.03:
            current_leverage = 13
        elif eth_basis - xrp_basis - ema >= 0.02:
            current_leverage = 12
        elif eth_basis - xrp_basis - ema >= 0.015:
            current_leverage = 10
        elif eth_basis - xrp_basis - ema >= 0.01:
            current_leverage = 7
        elif eth_basis - xrp_basis - ema >= 0.005:
            current_leverage = 3
        else:
            current_leverage = 0

        if current_leverage > previous_leverage:
            current_leverage = current_leverage
            change_position = True
        elif current_leverage < previous_leverage:
            if (previous_leverage >= 1) and (eth_basis - xrp_basis - ema <= 0.0005):
                current_status = "ignore"
                change_position = True
                current_leverage = 0
            elif (previous_leverage >= 10) and (eth_basis - xrp_basis - ema <= 0.01):
                current_leverage = 7
                change_position = True
            elif (previous_leverage >= 13) and (eth_basis - xrp_basis - ema <= 0.02):
                current_leverage = 12
                change_position = True
            else:
                current_leverage = previous_leverage

        if eth_basis - xrp_basis - ema <= 0.0005:
            current_status = "ignore"
            eth_future_decision = 0
            eth_swap_decision = 0
            xrp_future_decision = 0
            xrp_swap_decision = 0
        else:
            current_status = "short"
            eth_future_decision = -1
            eth_swap_decision = 1
            xrp_future_decision = 1
            xrp_swap_decision = -1

    elif previous_status == "long":
        if eth_basis - xrp_basis - ema <= -0.12:
            current_leverage = 20
        elif eth_basis - xrp_basis - ema <= -0.06:
            current_leverage = 16
        elif eth_basis - xrp_basis - ema <= -0.04:
            current_leverage = 14
        elif eth_basis - xrp_basis - ema <= -0.03:
            current_leverage = 13
        elif eth_basis - xrp_basis - ema <= -0.02:
            current_leverage = 12
        elif eth_basis - xrp_basis - ema <= -0.015:
            current_leverage = 10
        elif eth_basis - xrp_basis - ema <= -0.01:
            current_leverage = 7
        elif eth_basis - xrp_basis - ema <= -0.005:
            current_leverage = 3
        else:
            current_leverage = 0

        if current_leverage > previous_leverage:
            current_leverage = current_leverage
            change_position = True
        elif current_leverage < previous_leverage:
            if (previous_leverage >= 1) and (eth_basis - xrp_basis - ema >= -0.0005):
                current_leverage = 0
                change_position = True
                current_status = "ignore"
            elif (previous_leverage >= 10) and (eth_basis - xrp_basis - ema >= -0.01):
                current_leverage = 7
                change_position = True
            elif (previous_leverage >= 13) and (eth_basis - xrp_basis - ema >= -0.02):
                current_leverage = 12
                change_position = True
            else:
                current_leverage = previous_leverage

        if eth_basis - xrp_basis - ema >= -0.0005:
            current_status = "ignore"
            eth_future_decision = 0
            eth_swap_decision = 0
            xrp_future_decision = 0
            xrp_swap_decision = 0
        else:
            current_status = "long"
            eth_future_decision = 1
            eth_swap_decision = -1
            xrp_future_decision = -1
            xrp_swap_decision = 1
    #     print("eth_basis = ",eth_basis , "xrp_basis = ", xrp_basis, current_status, change_position)
    #     print("current_leverage")
    return eth_future_decision, eth_swap_decision, xrp_future_decision, xrp_swap_decision, current_status, current_leverage, change_position


def ETHXRPStrategy(candlePriceDf, markPriceMapping, next_state: dict, futureSuffix):
    journal = ""
    eth_future_decision = None
    eth_swap_decision = None
    xrp_future_decision = None
    xrp_swap_decision = None
    trx_future_decision = None
    trx_swap_decision = None

    current_status = None
    current_leverage = None
    current_coins_pair = ""

    eth_future = candlePriceDf["ETH-USDT" + futureSuffix].to_numpy()
    eth_spot = candlePriceDf["ETH-USDT-SWAP"].to_numpy()
    xrp_future = candlePriceDf["XRP-USDT" + futureSuffix].to_numpy()
    xrp_spot = candlePriceDf["XRP-USDT-SWAP"].to_numpy()
    trx_future = candlePriceDf["TRX-USDT" + futureSuffix].to_numpy()
    trx_spot = candlePriceDf["TRX-USDT-SWAP"].to_numpy()

    change_position = False
    previous_status = next_state["previous_status"]
    previous_leverage = next_state["previous_leverage"]
    previous_coins_pair = next_state["previous_coins_pair"]

    eth_basis_list = (eth_future - eth_spot) / (eth_spot + eth_future)
    xrp_basis_list = (xrp_future - xrp_spot) / (xrp_spot + xrp_future)
    trx_basis_list = (trx_future - trx_spot) / (trx_spot + trx_future)

    eth_basis = list(eth_basis_list)[-1]
    xrp_basis = list(xrp_basis_list)[-1]
    trx_basis = list(trx_basis_list)[-1]

    df = pd.DataFrame()
    df["eth_xrp"] = np.array(eth_basis_list) - np.array(xrp_basis_list)
    df["eth_trx"] = np.array(eth_basis_list) - np.array(trx_basis_list)
    df["trx_xrp"] = np.array(trx_basis_list) - np.array(xrp_basis_list)

    eth_xrp_ema = ta.ema(df["eth_xrp"], length=14 * 24 * 60).iloc[-1]  # 数据集分钟的，小时的就可以
    eth_trx_ema = ta.ema(df["eth_trx"], length=14 * 24 * 60).iloc[-1]
    trx_xrp_ema = ta.ema(df["trx_xrp"], length=28 * 24 * 60).iloc[-1]

    if previous_status == "ignore":
        # eth_xrp coin pair
        eth_future_decision, eth_swap_decision, xrp_future_decision, xrp_swap_decision, current_status, current_leverage, change_position = Checking_Arbitrage_Opportunity(
            eth_basis, xrp_basis, eth_xrp_ema, previous_status, previous_leverage)
        if current_status != "ignore":
            current_coins_pair = "eth_xrp"
            trx_future_decision = 0
            trx_swap_decision = 0
        else:
            # eth trx coin pair
            eth_future_decision, eth_swap_decision, trx_future_decision, trx_swap_decision, current_status, current_leverage, change_position = Checking_Arbitrage_Opportunity(
                eth_basis, trx_basis, eth_trx_ema, previous_status, previous_leverage)
            if current_status != "ignore":
                current_coins_pair = "eth_trx"
                xrp_future_decision = 0
                xrp_swap_decision = 0
            else:
                # trx xrp coin pair
                trx_future_decision, trx_swap_decision, xrp_future_decision, xrp_swap_decision, current_status, current_leverage, change_position = Checking_Arbitrage_Opportunity(
                    trx_basis, xrp_basis, trx_xrp_ema, previous_status, previous_leverage)
                if current_status != "ignore":
                    current_coins_pair = "trx_xrp"
                    eth_future_decision = 0
                    eth_swap_decision = 0
                else:
                    current_coins_pair = ""
                    eth_future_decision = 0
                    eth_swap_decision = 0
                    xrp_future_decision = 0
                    xrp_swap_decision = 0
                    trx_future_decision = 0
                    trx_swap_decision = 0

    elif previous_coins_pair == "eth_xrp":
        eth_future_decision, eth_swap_decision, xrp_future_decision, xrp_swap_decision, current_status, current_leverage, change_position = Checking_Arbitrage_Opportunity(
            eth_basis, xrp_basis, eth_xrp_ema, previous_status, previous_leverage)
        trx_future_decision = 0
        trx_swap_decision = 0
        if current_status == "ignore":
            current_coins_pair = ""
        else:
            current_coins_pair = previous_coins_pair


    elif previous_coins_pair == "eth_trx":
        eth_future_decision, eth_swap_decision, trx_future_decision, trx_swap_decision, current_status, current_leverage, change_position = Checking_Arbitrage_Opportunity(
            eth_basis, trx_basis, eth_trx_ema, previous_status, previous_leverage)
        xrp_future_decision = 0
        xrp_swap_decision = 0
        if current_status == "ignore":
            current_coins_pair = ""
        else:
            current_coins_pair = previous_coins_pair

    elif previous_coins_pair == "trx_xrp":
        trx_future_decision, trx_swap_decision, xrp_future_decision, xrp_swap_decision, current_status, current_leverage, change_position = Checking_Arbitrage_Opportunity(
            trx_basis, xrp_basis, trx_xrp_ema, previous_status, previous_leverage)
        eth_future_decision = 0
        eth_swap_decision = 0
        if current_status == "ignore":
            current_coins_pair = ""
        else:
            current_coins_pair = previous_coins_pair

    journal += str(f"eth_basis - xrp_basis - eth_xrp_ema: {eth_basis - xrp_basis - eth_xrp_ema}\n")
    journal += str(f"eth_basis - trx_basis - eth_trx_ema: {eth_basis - trx_basis - eth_trx_ema}\n")
    journal += str(f"trx_basis - xrp_basis - trx_xrp_ema: {trx_basis - xrp_basis - trx_xrp_ema}\n")
    journal += str(f"current_status: {current_status}\n")
    journal += str(f"current_leverage: {current_leverage}\n")
    journal += str(f"current_coins_pair: {current_coins_pair}\n")

    return {
        "time_to_order": change_position,
        "decision_payload": {
            "order_settings": {
                "current_status": current_status,
                "current_leverage": current_leverage,
                "current_coins_pair": current_coins_pair
            },
            "ETH-USDT": {
                "future_decision": eth_future_decision,
                "swap_decision": eth_swap_decision,
            },
            "XRP-USDT": {
                "future_decision": xrp_future_decision,
                "swap_decision": xrp_swap_decision,
            },
            "TRX-USDT": {
                "future_decision": trx_future_decision,
                "swap_decision": trx_swap_decision,
            }
        },
        "next_state": {
            "previous_status": current_status,
            "previous_leverage": current_leverage,
            "previous_coins_pair": current_coins_pair
        },
        "journal": journal
    }