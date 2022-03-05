import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

MODE=os.environ.get("MODE") or "dev" # prod || dev
PRINTER=os.environ.get("PRINTER") or "off" # on || off
SOCKET_CONNECTION_BUFFER_SEC = 1
SOCKET_URGENT_RECV_TIMEOUT_SEC = 30
SOCKET_URGENT_RECONNECT_HIBERNATE_SEC = 2
SOCKET_RECV_TIMEOUT_SEC = 30
SOCKET_RECONNECT_HIBERNATE_SEC = 60
OKEX_ENDPOINT = "https://www.okex.com"
OKEX_V5_BATCH_ORDER_PATH = "/api/v5/trade/batch-orders"
OKEX_V5_BALANCE_PATH = "/api/v5/account/balance"
OKEX_V5_POSITION_PATH = "/api/v5/account/positions"
OKEX_V5_REST_CANDLE_HISTORY_ENDPOINT = "https://www.okex.com/api/v5/market/history-candles"
OKEX_V5_REST_SWAP_INFO_ENDPOINT = "https://www.okex.com/api/v5/public/instruments?instType=SWAP"
OKEX_V5_REST_FUTURES_INFO_ENDPOINT = "https://www.okex.com/api/v5/public/instruments?instType=FUTURES"
OKEX_V5_REST_CANDLE_ENDPOINT = "https://www.okex.com/api/v5/market/candles"
OKEX_V5_WSS_ENDPOINT_PUBLIC = "wss://ws.okex.com:8443/ws/v5/public"
OKEX_V5_WSS_ENDPOINT_PRIVATE = "wss://ws.okex.com:8443/ws/v5/private"
OKEX_API_SECRET = os.environ.get("OKEX_API_SECRET")
OKEX_API_KEY = os.environ.get("OKEX_API_KEY")
OKEX_PASS_PHRASE = os.environ.get("OKEX_PASS_PHRASE")
OKEX_VERIFY_ROUTE = "GET/users/self/verify"
GLASSNODE_API_KEY = "1soahyHxlIOjgHCEzZtluSD5AMi"
GLASSNODE_MVRV_ZSCORE_ENDPOINT = "https://api.glassnode.com/v1/metrics/market/mvrv_z_score"
