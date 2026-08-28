# Lists recent closed AAPL orders via the older `alpaca-trade-api` SDK.
# Reads API credentials from environment variables — set these before running:
#   ALPACA_API_KEY / ALPACA_SECRET_KEY

import os
import alpaca_trade_api as tradeapi

KEY = os.environ.get('ALPACA_API_KEY', '')
SECRET = os.environ.get('ALPACA_SECRET_KEY', '')

url = "https://paper-api.alpaca.markets/v2"
api = tradeapi.REST(KEY, SECRET, url)

# Get the last 100 closed orders
closed_orders = api.list_orders(
    status='closed',
    limit=100,
    nested=True  # show nested multi-leg orders
)

# Get only the closed orders for a particular stock
closed_aapl_orders = [o for o in closed_orders if o.symbol == 'AAPL']
print(closed_aapl_orders)
