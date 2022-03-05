from enum import Enum


class OkexTradingParam:
    def __init__(self,
        strategyEnum: Enum,
        leader_spot_instId: str,
        data_dependents: dict,
        customizedParam=None
    ):
        if (leader_spot_instId.endswith("SWAP")):
            raise Exception("Program Setup Failure: Wrong Spot Name")
        self.strategyEnum = strategyEnum
        self.strategyId = strategyEnum.value
        self.leader_spot_instId = leader_spot_instId

        self.candle_dependent_instIdList = data_dependents["candle"]
        self.markprice_dependent_instIdList = []
        if "mark" in data_dependents:
            self.markprice_dependent_instIdList = data_dependents["mark"]

        self.customizedParam = customizedParam
        self.warRoomGap = 60
        try:
            self.warRoomGap = customizedParam.warRoomGap
        except:
            pass

