import Utils.GeneralHelper

EMA_FOUR_LINES_PERIOD_LIST=[2*24*60, 5*24*60, 14*24*60, 28*24*60]
MAINSTREAM_CANDLE_LIST_DEFAULT_LENGTH=120 * 24 * 60
MAINSTREAM_CANDLE_LIST_LENGTH_MAPPING={
    "ETH-USDT-SWAP": 29*24*60,
    "XRP-USDT-SWAP": 29*24*60,
    "TRX-USDT-SWAP": 29*24*60,
    "ETH-USDT-220325": 29*24*60,
    "XRP-USDT-220325": 29*24*60,
    "TRX-USDT-220325": 29*24*60,
}
OKEX_MAINSTREAM_CANDLES_INSTID=[
    "BTC-USDT",
    "ETH-USDT",
    "LTC-USDT",
    "XRP-USDT",
    "ETH-USDT-SWAP",
    "XRP-USDT-SWAP",
    "TRX-USDT-SWAP",
    "ETH-USDT-220325",
    "XRP-USDT-220325",
    "TRX-USDT-220325",
]
SIDESWITCH_SHORT_ENABLE_LIST=["BTC-USDT", "ETH-USDT", "LTC-USDT", "XRP-USDT"]
LONG_ENUM=1
SHORT_ENUM=-1
LIQUIDATION_ENUM=0
OKEX_ACCEPTABLE_SCODE=['0', '51020', '51119', '51121']
# 0: no error;
# 51020: must be greater than available;
# 51119: insufficient balance;
# 51121: must be integer unit (happens when selling short, see NOTES in SideSwitchOrderer)
# 51112: trying to cover more shorts than you opens in total, close order size exceeds available size