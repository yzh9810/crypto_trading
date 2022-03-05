from Configs import TradingConfig, GeneralConfig
import requests

class SideSwitchParam:
    def __init__(self, leader_spot_instId: str, short_instId: str, short_coefficient: float):
        self.short_instId = short_instId
        self.short_coefficient = short_coefficient

        self.ctValMinSwapUnit = 1
        endpoint = None
        if short_instId.endswith("SWAP"):
            endpoint = GeneralConfig.OKEX_V5_REST_SWAP_INFO_ENDPOINT
        else: # FUTURES
            endpoint = GeneralConfig.OKEX_V5_REST_FUTURES_INFO_ENDPOINT
        if leader_spot_instId in TradingConfig.SIDESWITCH_SHORT_ENABLE_LIST:
            # first we get instruments contract value, i.e. minimum units of exchanging swap shorts
            resp = requests.get(endpoint + "&instId=" + self.short_instId)
            # Contract value, Only applicable to FUTURES/SWAP/OPTION
            # For example, BTC-USDT-SWAP has a ctVal of 0.01, the lowest amount of position of BTC-SWAP we can purchase
            self.ctValMinSwapUnit = float(resp.json()["data"][0]["ctVal"])