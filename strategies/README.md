# Strategy backtests (strat1 → strat5)

This is my research log of candle-pattern hypotheses, each tested against the dataset from `../data_pipeline/`. Every script here is a standalone backtest — I never wired any of these up to live order execution. Worth reading in order, since each one is a variation on or a lesson learned from the last.

| Script | Idea |
|---|---|
| `strat1_gap_reversal.py` | If a candle closes down and the next one opens above its body (or vice versa), does that next candle tend to close in the "expected" direction? |
| `strat2_volatility_straddle.py` (+ `strat2_notes.md`) | After a big (>5%) move, straddle the open with a small take-profit on both sides — betting on next-day volatility rather than direction. |
| `strat3_gap_and_go.py` | A 3-candle pattern: does a clean gap that holds through the next candle's close predict a pullback two candles later? |
| `strat4_overnight_gap.py` | A stripped-down diagnostic — just logs every overnight gap above a threshold, no follow-up rule. I built this as a sanity check before layering anything on top. |
| `strat5_candle_streak.py` / `strat5_candle_streak_forex.py` (+ `strat5_notes.md`) | Detects streaks of "pure" (barely-retracing) same-direction candles and bets on a reversal after 2-3 in a row. This is where I pivoted from equities to forex (EURUSD). |

## Running one

```bash
pip install -r ../requirements.txt
python strat3_gap_and_go.py
```

Each script expects `../datasets/<timeframe>/<TICKER>.csv` files (from `data_pipeline/`) and `../data_pipeline/symbols folder/sorted_symbols` for the symbol list. Logs go to a local `logs/` folder (gitignored).

## One thing I left out

I also had a Selenium-driven "candle visualizer" running alongside strat2–strat4, which drove TradingView through a persistent Chrome profile so I could double-check signals visually. I didn't include it here since it depended on a personal, already-logged-in browser profile — the analysis scripts above are the part that's actually useful to anyone else.
