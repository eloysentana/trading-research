# Strategy backtests (strat1 → strat5)

A research log of candle-pattern hypotheses, each tested against the dataset produced by
`../data_pipeline/`. Every script is a standalone backtest — none of these were ever wired
up to live order execution. Read in order; each one is a variation or lesson learned from
the last.

| Script | Idea |
|---|---|
| `strat1_gap_reversal.py` | If a candle closes down and the next candle opens above its body (or vice versa), does that next candle tend to close in the "expected" direction? |
| `strat2_volatility_straddle.py` (+ `strat2_notes.md`) | After a big (>5%) move, straddle the open with a small take-profit on both sides, betting on next-day volatility rather than direction. |
| `strat3_gap_and_go.py` | A 3-candle pattern: does a clean gap that holds through the next candle's close predict a pullback two candles later? |
| `strat4_overnight_gap.py` | A stripped-down diagnostic: just logs every overnight gap above a threshold, without a follow-up rule — a sanity check before building on top of it. |
| `strat5_candle_streak.py` / `strat5_candle_streak_forex.py` (+ `strat5_notes.md`) | Detects streaks of "pure" (barely-retracing) same-direction candles and bets on reversal after 2-3 in a row. This is where the project pivots from equities to forex (EURUSD). |

## Running one

```bash
pip install -r ../requirements.txt
python strat3_gap_and_go.py
```

Each script expects `../datasets/<timeframe>/<TICKER>.csv` files (from `data_pipeline/`) and
`../data_pipeline/symbols folder/sorted_symbols` for the symbol list. Logs are written to a
local `logs/` folder (gitignored).

## Note

A Selenium-driven "candle visualizer" also existed alongside strat2–strat4, which drove
TradingView through a persistent Chrome profile so signals could be double-checked visually.
It isn't included here since it depended on a personal, already-logged-in browser profile —
the analysis scripts above are the useful, portable part.
