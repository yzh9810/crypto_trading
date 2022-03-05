import pandas as pd
import pandas_ta as ta
from Configs import TradingConfig

def BTCStrategy(priceDf, fundmental_df, basic_leverage=10):
    ema_2 = ta.ema(priceDf["BTC-USDT"], length=2 * 24 * 60).to_numpy()
    ema_3 = ta.ema(priceDf["BTC-USDT"], length=3 * 24 * 60).to_numpy()
    ema_5 = ta.ema(priceDf["BTC-USDT"], length=5 * 24 * 60).to_numpy()
    ema_8 = ta.ema(priceDf["BTC-USDT"], length=8 * 24 * 60).to_numpy()
    ema_12 = ta.ema(priceDf["BTC-USDT"], length=12 * 24 * 60).to_numpy()
    ema_14 = ta.ema(priceDf["BTC-USDT"], length=14 * 24 * 60).to_numpy()
    ema_28 = ta.ema(priceDf["BTC-USDT"], length=28 * 24 * 60).to_numpy()

    priceDf["ema_volume"] = ta.ema(priceDf["BTC-USDT-volume"], length=2 * 24 * 60).to_numpy() / ta.ema(priceDf["BTC-USDT-volume"],
                                                                                            length=60 * 24 * 60).to_numpy()

    fear_ema_decision = 0
    if (ema_3[-1] > ema_5[-1]) and (ema_5[-1] > ema_8[-1]):
        fear_ema_decision = 1
    elif (ema_3[-1] < ema_5[-1]) and (ema_5[-1] < ema_8[-1]):
        fear_ema_decision = -1

    fear_decision = 0
    if (fundmental_df["fear"].iloc[-1] > 30) and (priceDf["ema_volume"].iloc[-1] < 1.2):
        fear_decision = 1
    elif (fundmental_df["fear"].iloc[-1] > 30) and (priceDf["ema_volume"].iloc[-1] >= 1.2) and (fear_ema_decision != -1):
        fear_decision = 1

    simple_decision = 0
    if (ema_2[-1] > ema_5[-1]) and (ema_14[-1] > ema_28[-1]):
        simple_decision = 1
    if (ema_2[-1] < ema_5[-1]) and (ema_14[-1] < ema_28[-1]):
        simple_decision = -1

    future_decision = 1
    swap_decision = -1
    future_position = None
    swap_position = None

    if (fear_decision == 1) and (simple_decision == 0):
        future_position = basic_leverage
        swap_position = basic_leverage

    if (fear_decision == 1) and (simple_decision == 1):
        future_position = basic_leverage + 2
        swap_position = basic_leverage

    if (fear_decision == 1) and (simple_decision == -1):
        future_position = basic_leverage
        swap_position = basic_leverage + 2

    if (fear_decision == 0) and (simple_decision == 0):
        future_position = 0
        swap_position = 0

    if (fear_decision == 0) and (simple_decision == 1):
        future_position = 2
        swap_position = 0

    if (fear_decision == 0) and (simple_decision == -1):
        future_position = 0
        swap_position = 2

    return {
        "future_decision": future_decision,
        "swap_decision": swap_decision,
        "future_position": future_position,
        "swap_position": swap_position
    }