# Broker experiments

Once I had backtested some ideas in `../strategies/`, I looked at three broker APIs for actually placing orders:

- **`alpaca/`** — live crypto quote monitoring (BTC/USD, ETH/USD) against Alpaca's paper account. I used both their newer (`alpaca-py`) and older (`alpaca-trade-api`) SDKs at different points. I sketched out order submission but never actually turned it on.
- **`fxcm/`** — I looked into their ForexConnect SDK but dropped it before writing any real code. See `fxcm/README.md`.
- **`xtb/`** — the most developed of the three: a grid/martingale EURUSD bot I ran against an XTB **demo** account via the community `XTBApi` wrapper. It's a pretty different (and much higher-risk) approach than the market-neutral strategies in `../strategies/` — see `xtb/martingale_bot.py`'s docstring and the root README for why.

None of this ever ran against a live, funded account.
