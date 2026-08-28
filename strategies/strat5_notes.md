# Strat 5 — candle-streak reversal

Working notes from the original research log:

1. Only act (for the "alternate"/reversal mode) when there are streaks of 2 same-direction
   "pure" candles — noticed a tendency for AAPL to reverse after such a streak.
2. Try the same idea for streaks of 3.
3. Intuition: the more same-direction candles in a row, the more "overheated" things are,
   and the higher the odds that the next candle breaks the streak.

This is the point where the project pivots from equities toward forex (see
`strat5_candle_streak_forex.py`, applying the same streak logic to EURUSD).
