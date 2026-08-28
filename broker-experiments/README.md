# Broker experiments

After backtesting strategy ideas in `../strategies/`, three broker APIs were evaluated for
actually placing orders:

- **`alpaca/`** — live crypto quote monitoring (BTC/USD, ETH/USD) against Alpaca's paper
  account, using both their newer (`alpaca-py`) and older (`alpaca-trade-api`) SDKs at
  different points. Order submission code was sketched but never activated.
- **`fxcm/`** — evaluated via their ForexConnect SDK, but abandoned before any code was
  written. See `fxcm/README.md`.
- **`xtb/`** — the most developed of the three: a grid/martingale EURUSD bot run against an
  XTB **demo** account via the community `XTBApi` wrapper. This is a markedly different (and
  much higher-risk) approach than the market-neutral strategies in `../strategies/` — see
  `xtb/martingale_bot.py`'s docstring and the root README for why.

None of this was ever run against a live/funded account.
