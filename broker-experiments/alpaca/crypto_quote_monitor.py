# Live BTC/USD and ETH/USD bid-ask spread monitor, using Alpaca's newer `alpaca-py` SDK.
# Reads API credentials from environment variables — set these before running:
#   ALPACA_API_KEY / ALPACA_SECRET_KEY
#
# This only ever polled market data; no orders were placed from this script (the
# commented-out block below sketches what order submission would have looked like).

import os
from time import sleep
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest

KEY = os.environ.get('ALPACA_API_KEY', '')
SECRET = os.environ.get('ALPACA_SECRET_KEY', '')

print('Initiated program')
############################################################

client = CryptoHistoricalDataClient()

pair1 = "BTC/USD"
pair2 = 'ETH/USD'
while True:
    sleep(0.1)
    request_params1 = CryptoLatestQuoteRequest(symbol_or_symbols=pair1)
    request_params2 = CryptoLatestQuoteRequest(symbol_or_symbols=pair2)
    latest_quote1 = client.get_crypto_latest_quote(request_params1)
    latest_quote2 = client.get_crypto_latest_quote(request_params2)
    b1 = latest_quote1[pair1].bid_price
    a1 = latest_quote1[pair1].ask_price
    b2 = latest_quote1[pair1].bid_price
    a2 = latest_quote1[pair1].ask_price
    s1 = float(round((a1 - b1), 2))
    s2 = float(round((a2 - b1), 2))
    print("%.5f" % latest_quote1[pair1].bid_size, "%.2f" % b1, "%.2f" % s1, "%.2f" % a1, "%.4f" % (s1 * 100 / b1), "%.5f" % latest_quote1[pair1].ask_size, '    --    ',
          "%.5f" % latest_quote2[pair2].bid_size, "%.2f" % b2, "%.2f" % s2, "%.2f" % a2, "%.4f" % (s2 * 100 / b2), "%.5f" % latest_quote2[pair2].ask_size)


###############################################################
# Sketch of a bracket order this could have submitted (never activated):
#
# from alpaca.trading.client import TradingClient
# from alpaca.trading.requests import MarketOrderRequest
# from alpaca.trading.enums import OrderSide, TimeInForce
#
# trading_client = TradingClient(KEY, SECRET, paper=True)
#
# market_order_data = MarketOrderRequest(
#     symbol="BTC/USD",
#     qty=1,
#     side=OrderSide.BUY,
#     time_in_force=TimeInForce.GTC
# )
# market_order = trading_client.submit_order(order_data=market_order_data)
