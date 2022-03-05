from Configs import TradingConfig, GeneralConfig
import requests

class StaBasisArbParam:
    def __init__(self, tradeSpotIdList, futureSuffix):
        self.tradeSpotIdList = tradeSpotIdList
        self.futureSuffix = futureSuffix
        # minimum trade unit
        self.ctValMapping = {}
        for spot_id in tradeSpotIdList:
            resp = requests.get(GeneralConfig.OKEX_V5_REST_SWAP_INFO_ENDPOINT + "&instId=" + spot_id + "-SWAP")
            self.ctValMapping[spot_id] = float(resp.json()["data"][0]["ctVal"])
        self.warRoomGap = 20
