# Trading Research

A research log of quantitative trading ideas: a data pipeline, five rounds of candle-pattern
backtests across stocks and forex, and a survey of three broker APIs for execution — ending
in a grid/martingale forex bot. Built between December 2022 and April 2023, as a follow-up to
[gap-fade-trading-bot](https://github.com/eloysentana/gap-fade-trading-bot), a more disciplined
second pass: build a proper historical dataset first, backtest hypotheses against it, *then*
go looking for a broker to execute on.

> ⚠️ Nothing here was ever run against a funded/live account. The Alpaca work used paper
> trading; the XTB work used a demo account.

## How it's organized

```
data_pipeline/          → scrapes a ticker universe and downloads historical OHLCV data
strategies/              → strat1 through strat5: a backtest research log, in chronological order
broker-experiments/      → Alpaca, FXCM, and XTB, evaluated as execution venues
```

Each folder has its own README with more detail. The short version, in the order it happened:

1. **Data pipeline**: scrape a Nasdaq screener, sort by market cap, bulk-download ~10 years
   of daily OHLCV per ticker from Yahoo Finance.
2. **strat1 → strat5**: five rounds of candle-pattern hypotheses tested against that dataset —
   gap reversal, post-shock volatility straddles, a 3-candle gap-and-go pattern, a raw
   overnight-gap diagnostic, and finally a candle-streak reversal idea that prompted a pivot
   from equities to forex (EURUSD).
3. **Broker survey**: with a forex idea in hand, three broker APIs were evaluated for
   execution — Alpaca (crypto quotes, paper), FXCM (evaluated, no code written), and XTB
   (the most developed: a grid/martingale bot on a demo account).

## Why the XTB bot is a different animal

Everything in `strategies/` is trying to find a small statistical edge while staying roughly
flat. `broker-experiments/xtb/martingale_bot.py` is a different paradigm entirely: it opens a
buy-limit and a sell-limit around the current price, and whichever side fills first gets its
take-profit set while the *opposite* side's next order size roughly doubles. That's a
martingale — it wins small and often, but a sustained one-directional move without enough
account equity behind it can blow through the whole grid. It's included here as a real
artifact of the research process, not a recommendation.

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

## Security note

Every credential in this repo is read from an environment variable. The originals (Alpaca
paper-trading keys, an XTB demo account login) were hardcoded in the source during
development — treat any such leaked credential as compromised, and if a password was ever
reused elsewhere, rotate that too.
