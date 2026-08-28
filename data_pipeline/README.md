# Data pipeline

This builds the historical daily-OHLCV dataset that everything in `../strategies/` backtests against.

`main_engine.py`:

1. Scrapes a Nasdaq stock screener (via Selenium) into `symbols folder/`, sorted by market cap.
2. For each of the top ~150 symbols, downloads full daily OHLCV history from Yahoo Finance's CSV download endpoint into a temp folder, then copies the result into `../datasets/yearly2/<year1>to<year2>/`.
3. Repeats that per two-year window from 2011 to 2021 — I chunked it by period instead of doing one giant pull, mostly so a failed run wouldn't cost me everything.

Run it with:

```bash
pip install -r ../requirements.txt
python main_engine.py
```

The output (`symbols folder/`, `drivers/`, and `../datasets/`) is gitignored — I meant this to be regenerated locally, not committed.
