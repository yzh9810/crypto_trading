from FunctionParams.StaBasisArbParam import StaBasisArbParam
from FunctionParams.SideSwitchParam import SideSwitchParam
from Factory.index import *
from Utils.Logger import *
from FunctionParams.UserAccountParam import *
from Configs import GeneralConfig
import asyncio
import os

# SideSwitch: units of swap purchase = param_coeffcient * ctVal (min trading unit provided by Okex)
# Buy spot $X worth of btc for spot
# Sell short X minimum units for swap

# (
#     OkexTradingParam(
#         TradingTypeEnum.SideSwitch.value.EmaFundamental,
#         "XRP-USDT",
#         {"candle": ["BTC-USDT", "XRP-USDT"]},
#         SideSwitchParam("XRP-USDT", "XRP-USDT-SWAP", 7)
#     ),
#     [genesisAccount]
# ),

# genesisAccount = UserAccountParam(
#     "UserGenesisYue",
#     "6295a5f5-fb9b-4dfb-98f8-b34801ce7bc1",
#     "4BD9C0EA5563A6626159DCA0721CB8BD",
#     GeneralConfig.OKEX_PASS_PHRASE
# )

crossCoinsAccount = UserAccountParam(
    "UserCrosscoins",
    "2541ecd0-88e2-4171-a5c0-dbfdd3579168",
    "22881A9F1C6BD6630F183A4DEAAAC25E",
    GeneralConfig.OKEX_PASS_PHRASE
)

crossCoinsFutureSuffix = "-220325"
tradingList = [
    (
        OkexTradingParam(
            TradingTypeEnum.StaBasisArb.value.StaBasisArbV0,
            "ETH-USDT",
            {
                "candle": [
                    "ETH-USDT-SWAP",
                    "XRP-USDT-SWAP",
                    "TRX-USDT-SWAP",
                    "ETH-USDT"+crossCoinsFutureSuffix,
                    "XRP-USDT"+crossCoinsFutureSuffix,
                    "TRX-USDT"+crossCoinsFutureSuffix
                ],
                # "mark": ["ETH-USDT-SWAP", "XRP-USDT-SWAP", "ETH-USDT"+crossCoinsFutureSuffix, "XRP-USDT"+crossCoinsFutureSuffix]
            },
            StaBasisArbParam(["ETH-USDT", "XRP-USDT", "TRX-USDT"], crossCoinsFutureSuffix)
        ),
        [crossCoinsAccount]
    ),
    # (
    #     OkexTradingParam(
    #         TradingTypeEnum.SideSwitch.value.EmaFundamental,
    #         "ADA-USDT",
    #         {"candle": ["ADA-USDT"]},
    #         SideSwitchParam("ADA-USDT", "ADA-USDT-SWAP", 170)
    #     ),
    #     [genesisAccount]
    # ),
    # (
    #     OkexTradingParam(
    #         TradingTypeEnum.SideSwitch.value.EmaFundamental,
    #         "DOT-USDT",
    #         {"candle": ["DOT-USDT"]},
    #         SideSwitchParam("DOT-USDT", "DOT-USDT-SWAP", 16)
    #     ),
    #     [genesisAccount]
    # ),
    # (
    #     OkexTradingParam(
    #         TradingTypeEnum.SideSwitch.value.EmaFundamental,
    #         "SOL-USDT",
    #         {"candle": ["SOL-USDT"]},
    #         SideSwitchParam("SOL-USDT", "SOL-USDT-SWAP", 8)
    #     ),
    #     [genesisAccount]
    # ),
    # (
    #     OkexTradingParam(
    #         TradingTypeEnum.SideSwitch.value.EmaFundamental,
    #         "LUNA-USDT",
    #         {"candle": ["LUNA-USDT"]},
    #         SideSwitchParam("LUNA-USDT", "LUNA-USDT-SWAP", 21)
    #     ),
    #     [genesisAccount]
    # ),
    # (
    #     OkexTradingParam(
    #         TradingTypeEnum.SideSwitch.value.EmaFundamental,
    #         "ATOM-USDT",
    #         {"candle": ["ATOM-USDT"]},
    #         SideSwitchParam("ATOM-USDT", "ATOM-USDT-SWAP", 23)
    #     ),
    #     [genesisAccount]
    # ),
    # (
    #     OkexTradingParam(
    #         TradingTypeEnum.SideSwitch.value.EmaFundamental,
    #         "AVAX-USDT",
    #         {"candle": ["AVAX-USDT"]},
    #         SideSwitchParam("AVAX-USDT", "AVAX-USDT-SWAP", 20)
    #     ),
    #     [genesisAccount]
    # ),
]

try:
    os.mkdir("Logs")
except:
    pass

for payload in tradingList:
    tradingParam = payload[0]
    try:
        os.mkdir("Logs/" + tradingParam.leader_spot_instId)
    except:
        pass
    accounts = payload[1]
    for acc in accounts:
        try:
            os.mkdir("Logs/" + acc.accountId)
        except:
            continue

# only one thread can connect to server within the period of one second
loop = asyncio.get_event_loop()

# BEGIN GLOBAL SINGLETON INITIALIZATION
connectionSemaphore = asyncio.Lock()
connectionLogger = Logger("Connections")

candleDependencyIdList = []
for payload in tradingList:
    for instId in payload[0].candle_dependent_instIdList:
        if not instId in candleDependencyIdList:
            candleDependencyIdList.append(instId)
if len(candleDependencyIdList) > 0:
    GeneralHelper.printOnDevPrinterMode(
        "Price Manager listens to following candles:\n"
        + ",".join(candleDependencyIdList)
    )

markPriceDependencyIdList = []
for payload in tradingList:
    for instId in payload[0].markprice_dependent_instIdList:
        if not instId in markPriceDependencyIdList:
            markPriceDependencyIdList.append(instId)
if len(markPriceDependencyIdList) > 0:
    GeneralHelper.printOnDevPrinterMode(
        "Price Manager listens to following mark:\n"
        + ",".join(markPriceDependencyIdList)
    )

priceManager = PriceQueueManager(
    loop, candleDependencyIdList, markPriceDependencyIdList, connectionSemaphore, connectionLogger
)

fundamentalFetcher = DayFundamentalFetcher(loop)
# GLOBAL SINGLETON INITIALIZATION FINISHED

warRoomFactory = WarRoomFactory(loop, priceManager, fundamentalFetcher)
for pair in tradingList:
    tradingParam = pair[0]
    accList = pair[1]
    warRoomFactory.initWarRoom(tradingParam, accList)
# positionExporter = HourPositionExporter(loop, connectionSemaphore)
loop.run_forever()