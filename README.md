# Trading Research

This is the follow-up to [gap-fade-trading-bot](https://github.com/eloysentana/gap-fade-trading-bot) that I  built between December 2022 and April 2023. After running that bot for a while, I wanted to be more disciplined about it: build a proper historical dataset first, actually backtest my ideas against it, and only then go looking for a broker to execute on. This repo is what came out of that — a data pipeline, five rounds of candle-pattern backtests across stocks and forex, and a survey of three broker APIs, ending with a grid/martingale forex bot.

> ⚠️ Nothing here ever touched a funded account. The Alpaca work used paper trading; the XTB work used a demo account.

## How it's organized

```
data_pipeline/          → scrapes a ticker universe and downloads historical OHLCV data
strategies/              → strat1 through strat5: my backtest research log, in order
broker-experiments/      → Alpaca, FXCM, and XTB, tried as execution venues
```

Each folder has its own README with more detail. The short version, roughly in the order I did it:

1. **Data pipeline**: scrape a Nasdaq screener, sort by market cap, bulk-download about 10 years of daily OHLCV per ticker from Yahoo Finance.
2. **strat1 → strat5**: five rounds of candle-pattern ideas, each tested against that dataset — gap reversal, post-shock volatility straddles, a 3-candle gap-and-go pattern, a raw overnight-gap diagnostic, and finally a candle-streak reversal idea that's where I ended up pivoting from equities to forex (EURUSD).
3. **Broker survey**: once I had a forex idea I liked, I went looking for somewhere to actually run it — Alpaca (crypto quotes, paper), FXCM (looked into it, never wrote any code), and XTB, which is where I ended up building the most developed piece: a grid/martingale bot on a demo account.

## The XTB bot

Everything in `strategies/` is me trying to find a small statistical edge while staying roughly flat. `broker-experiments/xtb/martingale_bot.py` is a completely different approach: it opens a buy-limit and a sell-limit around the current price, and whichever side fills first gets its take-profit set while the *opposite* side's next order roughly doubles in size. That's a martingale — it wins small and often, but a sustained move in one direction without enough account equity behind it can blow through the whole grid. I'm including it here because it's a real part of how this research went, not because I'd recommend it.

## Setup

```bash
pip install -r requirements.txt          # data_pipeline/ + strategies/
pip install -r broker-experiments/alpaca/requirements.txt
pip install -r broker-experiments/xtb/requirements.txt
```

Broker credentials are read from environment variables, never hardcoded:

```bash
export ALPACA_API_KEY=...
export ALPACA_SECRET_KEY=...
export XTB_ACCOUNT_ID=...
export XTB_PASSWORD=...
```
