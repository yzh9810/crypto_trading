from .Calculator.ETHXRP import *

def getCalculator(leader_spot_instId):
    handlerMapping = {
        "ETH-USDT": ETHXRPCalc
    }
    return handlerMapping.get(leader_spot_instId, None)