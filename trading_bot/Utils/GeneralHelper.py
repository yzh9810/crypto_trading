from Utils import TimeHelper
from Configs import GeneralConfig
import traceback

def formattedFloatString(num):
    # counter float scientific notation
    return '{0:.20f}'.format(float(num)).rstrip('0').rstrip('.')

def printOnDevPrinterMode(message: str):
    if GeneralConfig.MODE == "dev" and GeneralConfig.PRINTER == "on":
        print(message)

def printErrorStackOnDevPrinterMode():
    if GeneralConfig.MODE == "dev" and GeneralConfig.PRINTER == "on":
        traceback.print_exc()

def logOneFileSyncOnDevMode(logger, content):
    if GeneralConfig.MODE == "dev":
        logger.logSync(content, True)

def keysMissingInDict(obj: dict, keys: list):
    for key in keys:
        if not key in obj:
            return True
    return False