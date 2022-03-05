import pandas_ta as ta
from Configs import TradingConfig
from Utils.StrategyHelper import *
from Utils.Logger import *

def ETHStrategy(priceMapping, fundamentalDf, next_state: dict):
    mvrv_state = next_state["mvrv_state"]
    mvrv_realized_price = next_state["mvrv_realized_price"]
    mvrv_start_time = next_state["mvrv_start_time"]
    lefttime = next_state["lefttime"]

    decision_payload = None
    journal = ""

    periodList = TradingConfig.EMA_FOUR_LINES_PERIOD_LIST
    df = pd.DataFrame(priceMapping)
    btc_ema_2 = ta.ema(df["BTC-USDT"], length=periodList[0]).to_numpy()
    btc_ema_5 = ta.ema(df["BTC-USDT"], length=periodList[1]).to_numpy()
    diff_2_5 = btc_ema_2 - btc_ema_5
    diff_2_5_value = list(diff_2_5)[-1]

    btc_ema_3 = ta.ema(df["BTC-USDT"], length=3 * 24 * 60).to_numpy()
    btc_ema_9 = ta.ema(df["BTC-USDT"], length=9 * 24 * 60).to_numpy()
    diff_3_9 = btc_ema_3 - btc_ema_9

    btc_ema_14 = ta.ema(df["BTC-USDT"], length=periodList[2]).to_numpy()
    btc_ema_28 = ta.ema(df["BTC-USDT"], length=periodList[3]).to_numpy()
    diff_14_28 = btc_ema_14 - btc_ema_28
    diff_14_28_value = list(diff_14_28)[-1]

    eth_ema_2 = list(ta.ema(df["ETH-USDT"], length=periodList[0]))[-1]
    eth_ema_5 = list(ta.ema(df["ETH-USDT"], length=periodList[1]))[-1]

    eth_diff_2_5 = eth_ema_2 - eth_ema_5

    eth_ema_14 = list(ta.ema(df["ETH-USDT"], length=periodList[2]))[-1]
    eth_ema_28 = list(ta.ema(df["ETH-USDT"], length=periodList[3]))[-1]
    eth_diff_14_28 = eth_ema_14 - eth_ema_28

    btc_decision = 0
    eth_decision = 0
    if (diff_2_5_value > 0 and diff_14_28_value > 0):
        btc_decision = 1

    if (diff_2_5_value < 0 and diff_14_28_value < 0):
        btc_decision = -1

    if (eth_diff_2_5 > 0 and eth_diff_14_28 > 0):
        eth_decision = 1

    if (eth_diff_2_5 < 0 and eth_diff_14_28 < 0):
        eth_decision = -1

    ema_decision = 0
    if btc_decision == 1 and eth_decision == -1:
        ema_decision = 0
    elif btc_decision == -1 and eth_decision == 1:
        ema_decision = 0
    elif btc_decision == 1:
        ema_decision = 1
    elif eth_decision == 1:
        ema_decision = 1
    elif btc_decision == -1:
        ema_decision = -1
    elif eth_decision == -1:
        ema_decision = -1

    current_price = df["BTC-USDT"].iloc[-1]
    current_mvrv_value = fundamentalDf.mvrv.iloc[-1]
    current_time = fundamentalDf.timestamp.iloc[-1]

    if current_mvrv_value >= 7:
        if mvrv_state == "Ignore" or mvrv_state == "Keep_long" or mvrv_state == "Keep_short":
            mvrv_start_time = current_time
            mvrv_state = "Ready_short"
            mvrv_realized_price = 0
            lefttime = 0
        decision_payload = ema_decision

    elif current_mvrv_value <= 0:
        if mvrv_state == "Ignore" or mvrv_state == "Keep_long" or mvrv_state == "Keep_short":
            mvrv_start_time = current_time
            mvrv_state = "Ready_long"
            mvrv_realized_price = 0
            lefttime = 0

        decision_payload = ema_decision


    elif current_mvrv_value < 7 and current_mvrv_value > 0:
        if mvrv_state == "Ignore":
            mvrv_start_time = 0
            mvrv_state = "Ignore"
            mvrv_realized_price = 0
            lefttime = 0
            decision_payload = ema_decision

        elif mvrv_state == "Ready_long":
            min_price = df.loc[df.timestamp >= mvrv_start_time]["BTC-USDT"].min()
            if current_time - mvrv_start_time >= 14 * 24 * 60 * 60:
                df["diff"] = diff_14_28
                max_price = find_local_extreme(df, mvrv_start_time, coin_name="BTC-USDT",
                                               direction="max", period=14)

                realized_change_ratio = (min_price - max_price) / max_price * 0.5
                mvrv_realized_price = max_price * (1 + realized_change_ratio)
                if current_price < mvrv_realized_price:
                    mvrv_state = "Keep_long"
                    newString = "in time " + str(current_time) + "realized_price = " + str(mvrv_realized_price) + '\n'
                    journal += newString
                    decision_payload = 1
                    lefttime = current_time + 10 * 24 * 60 * 60 + 2 * (current_time - mvrv_start_time)

                else:
                    mvrv_state = "Ignore"
                    decision_payload = ema_decision
                    lefttime = 0

            if current_time - mvrv_start_time < 14 * 24 * 60 * 60:
                df["diff"] = diff_3_9
                max_price = find_local_extreme(df, mvrv_start_time, coin_name="BTC-USDT",
                                               direction="max", period=8)
                realized_change_ratio = (min_price - max_price) / max_price * 0.5
                mvrv_realized_price = max_price * (1 + realized_change_ratio)
                if current_price < mvrv_realized_price:
                    mvrv_state = "Keep_long"
                    newString = "in time " + str(current_time) + "realized_price = " + str(mvrv_realized_price) + '\n'
                    journal += newString
                    decision_payload = 1
                    lefttime = current_time + 10 * 24 * 60 * 60 + 2 * (current_time - mvrv_start_time)

                else:
                    mvrv_state = "Ignore"
                    decision_payload = ema_decision
                    lefttime = 0

        elif mvrv_state == "Ready_short":
            max_price = df.loc[df.timestamp >= mvrv_start_time]["BTC-USDT"].max()
            if current_time - mvrv_start_time >= 14 * 24 * 60 * 60:
                df["diff"] = diff_14_28
                min_price = find_local_extreme(df, mvrv_start_time, coin_name="BTC-USDT",
                                               direction="min", period=14)
                realized_change_ratio = (max_price - min_price) / min_price * 0.5
                mvrv_realized_price = min_price * (1 + realized_change_ratio)
                if current_price > mvrv_realized_price:
                    mvrv_state = "Keep_short"
                    newString = "in time " + str(current_time) + "realized_price = " + str(mvrv_realized_price) + '\n'
                    journal += newString
                    decision_payload = -1
                    lefttime = current_time + 10 * 24 * 60 * 60 + 2 * (current_time - mvrv_start_time)

                else:
                    mvrv_state = "Ignore"
                    decision_payload = ema_decision
                    lefttime = 0

            if current_time - mvrv_start_time < 14 * 24 * 60 * 60:
                df["diff"] = diff_3_9
                min_price = find_local_extreme(df, mvrv_start_time, coin_name="BTC-USDT",
                                               direction="min", period=8)

                realized_change_ratio = (max_price - min_price) / min_price * 0.5
                mvrv_realized_price = min_price * (1 + realized_change_ratio)
                if current_price > mvrv_realized_price:
                    mvrv_state = "Keep_short"
                    newString = "in time " + str(current_time) + "realized_price = " + str(mvrv_realized_price) + '\n'
                    journal += newString
                    decision_payload = -1
                    lefttime = current_time + 10 * 24 * 60 * 60 + 2 * (current_time - mvrv_start_time)

                else:
                    mvrv_state = "Ignore"
                    decision_payload = ema_decision
                    lefttime = 0

        elif mvrv_state == "Keep_long":
            if current_price >= mvrv_realized_price:
                newString = "Shut down at time " + str(current_price) + '\n'
                journal += newString
                decision_payload = ema_decision
                mvrv_state = "Ignore"
                lefttime = 0

            elif current_time < lefttime:
                decision_payload = 1

            elif current_time >= lefttime:
                decision_payload = ema_decision
                mvrv_state = "Ignore"
                lefttime = 0

        elif mvrv_state == "Keep_short":
            if current_price <= mvrv_realized_price:
                newString = "Shut down at time " + str(current_price) + '\n'
                journal += newString
                decision_payload = ema_decision
                mvrv_state = "Ignore"
                lefttime = 0
            elif current_time < lefttime:
                decision_payload = -1

            elif current_time >= lefttime:
                decision_payload = ema_decision
                mvrv_state = "Ignore"
                lefttime = 0

    if decision_payload is None:
        errorLogger = Logger("ETH-USDT/ErrCommodore")
        errorLogger.logSync("No Matching cases for Final Decision, Terminate All Program!")
        print("No Matching cases for Final Decision, Terminate All Program!")
        exit(1)

    newString = "Final Decision: " + str(decision_payload) + "\n"
    journal += newString

    return {
        "decision_payload": decision_payload,
        "next_state" : {
            "mvrv_state": mvrv_state,
            "mvrv_realized_price": mvrv_realized_price,
            "mvrv_start_time": mvrv_start_time,
            "lefttime": lefttime,
        },
        "journal": journal
    }