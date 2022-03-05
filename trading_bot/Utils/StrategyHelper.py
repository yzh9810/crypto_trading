import pandas as pd
import pandas_ta as ta
import numpy as np

def find_local_extreme(df, current_time, coin_name="BTC-USDT", direction="max", period=8):
    sub_df = df.loc[df.timestamp <= current_time]
    price = sub_df[coin_name].to_numpy()
    diff = sub_df["diff"].to_numpy()
    for i in np.arange(len(sub_df), 1, -1):
        if (diff[i - 1] * diff[i]) <= 0:
            if direction == "max":
                max_price = max(price[i - 24 * 60 * period: i])
                return max_price

            if direction == "min":
                min_price = min(price[i - 24 * 60 * period: i])
                return min_price

    if direction == "max":
        max_price = max(price)
        return max_price

    if direction == "min":
        min_price = min(price)
        return min_price