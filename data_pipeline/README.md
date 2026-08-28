# Data pipeline

Builds the historical daily-OHLCV dataset that `../strategies/` backtests against.

`main_engine.py`:

1. Scrapes a Nasdaq stock screener (via Selenium) into `symbols folder/`, sorted by market cap.
2. For each of the top ~150 symbols, downloads full daily OHLCV history from Yahoo Finance's
   CSV download endpoint into a temporary folder, then copies the result into
   `../datasets/yearly2/<year1>to<year2>/`.
3. Repeats that per two-year window from 2011 to 2021, so the final dataset is chunked by
   period rather than one giant pull.

Run with:

```bash
pip install -r ../requirements.txt
python main_engine.py
```

Output (`symbols folder/`, `drivers/`, and `../datasets/`) is gitignored — this is meant to be
regenerated locally, not committed.
