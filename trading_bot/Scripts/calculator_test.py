def ETHXRPCalc(total_usdt, markPriceMapping, next_state, order_settings: dict, futureSuffix):
    ignore_position = next_state["ignore_position"]
    eth_quantity = 0
    xrp_quantity = 0
    trx_quantity = 0

    current_status = order_settings["current_status"]
    current_leverage = order_settings["current_leverage"]
    current_coins_pair = order_settings["current_coins_pair"]


    eth_spot = markPriceMapping["ETH-USDT-SWAP"]
    eth_future = markPriceMapping["ETH-USDT" + futureSuffix]

    xrp_spot = markPriceMapping["XRP-USDT-SWAP"]
    xrp_future = markPriceMapping["XRP-USDT" + futureSuffix]

    trx_spot = markPriceMapping["TRX-USDT-SWAP"]
    trx_future = markPriceMapping["TRX-USDT" + futureSuffix]

    if current_status == "ignore" or ignore_position == 0:
        ignore_position = total_usdt

    if current_status != "ignore":
        if current_coins_pair == "eth_xrp":
            eth_quantity = int((ignore_position / 2 / (eth_spot + eth_future) * current_leverage) / 0.1) * 0.1
            xrp_quantity = int(ignore_position / 2 / (xrp_spot + xrp_future) * current_leverage / 100) * 100
            if ((eth_quantity * (eth_spot + eth_future)) - (xrp_quantity * (xrp_spot + xrp_future))) / (
                eth_spot + eth_future) >= 1:
                min_position = min(eth_quantity * (eth_spot + eth_future), xrp_quantity * (xrp_spot + xrp_future))
                eth_quantity = min_position / (eth_spot + eth_future)
                xrp_quantity = min_position / (xrp_spot + xrp_future)
            elif ((xrp_quantity * (xrp_spot + xrp_future)) - (eth_quantity * (eth_spot + eth_future))) / (
                xrp_spot + xrp_future) >= 1:
                min_position = min(eth_quantity * (eth_spot + eth_future), xrp_quantity * (xrp_spot + xrp_future))
                eth_quantity = min_position / (eth_spot + eth_future)
                xrp_quantity = min_position / (xrp_spot + xrp_future)
        elif current_coins_pair == "eth_trx":
            print((ignore_position / 2 / (eth_spot + eth_future) * current_leverage) / 0.1)
            eth_quantity = int((ignore_position / 2 / (eth_spot + eth_future) * current_leverage) / 0.1) * 0.1
            trx_quantity = int(ignore_position / 2 / (trx_spot + trx_future) * current_leverage / 1000) * 1000
            if ((eth_quantity * (eth_spot + eth_future)) - (trx_quantity * (trx_spot + trx_future))) / (
                    eth_spot + eth_future) >= 1:
                min_position = min(eth_quantity * (eth_spot + eth_future), trx_quantity * (trx_spot + trx_future))
                eth_quantity = min_position / (eth_spot + eth_future)
                trx_quantity = min_position / (trx_spot + trx_future)
            elif ((trx_quantity * (trx_spot + trx_future)) - (eth_quantity * (eth_spot + eth_future))) / (
                    trx_spot + trx_future) >= 1:
                min_position = min(eth_quantity * (eth_spot + eth_future), trx_quantity * (trx_spot + trx_future))
                eth_quantity = min_position / (eth_spot + eth_future)
                trx_quantity = min_position / (trx_spot + trx_future)
        elif current_coins_pair == "trx_xrp":
            trx_quantity = int(ignore_position / 2 / (trx_spot + trx_future) * current_leverage / 1000) * 1000
            xrp_quantity = int(ignore_position / 2 / (xrp_spot + xrp_future) * current_leverage / 100) * 100
            if ((trx_quantity * (trx_spot + trx_future)) - (xrp_quantity * (xrp_spot + xrp_future))) / (
                    trx_spot + trx_future) >= 1:
                min_position = min(xrp_quantity * (xrp_spot + xrp_future), trx_quantity * (trx_spot + trx_future))
                trx_quantity = min_position / (trx_spot + trx_future)
                xrp_quantity = min_position / (xrp_spot + xrp_future)
            elif ((trx_quantity * (trx_spot + trx_future)) - (xrp_quantity * (xrp_spot + xrp_future))) / (
                    xrp_spot + xrp_future) >= 1:
                min_position = min(xrp_quantity * (xrp_spot + xrp_future), trx_quantity * (trx_spot + trx_future))
                trx_quantity = min_position / (trx_spot + trx_future)
                xrp_quantity = min_position / (xrp_spot + xrp_future)

    print(f"total_usdt: {total_usdt}")
    print(f"markPriceMapping: {markPriceMapping}")
    print(f"next_state: {next_state}")
    print(f"order_settings: {order_settings}")
    print(f"futureSuffix: {futureSuffix}")
    return {
        "ETH-USDT": abs(eth_quantity),
        "XRP-USDT": abs(xrp_quantity),
        "TRX-USDT": abs(trx_quantity),
        "next_state": {
            "ignore_position": ignore_position
        }
    }

print(
    ETHXRPCalc(
        1205.736342199996,
        {"ETH-USDT-SWAP": 2865.25, "XRP-USDT-SWAP": 0.936, "TRX-USDT-SWAP": 0.08607, "ETH-USDT-220325": 2977.62, "XRP-USDT-220325": 0.95948, "TRX-USDT-220325": 0.08647},
        {'ignore_position': 0},
        {"current_status": "short", "current_leverage": 4, "current_coins_pair": "eth_trx"},
        "-220325"
    )
)