# Date,Open,High,Low,Close,Adj Close,Volume
#
# Hypothesis: if a candle closes down and the next day opens above the
# previous candle's body, that next candle tends to close up (and vice versa).
# See ../README.md for the full writeup.

from datetime import datetime
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR.parent / 'datasets'
SORTED_SYMBOLS_PATH = BASE_DIR.parent / 'data_pipeline' / 'symbols folder' / 'sorted_symbols'

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
now = datetime.now().strftime("%y_%m_%d-%H_%M_%S")
logs = open(LOGS_DIR / f"logfile-{now}.txt", "a", newline='')
writer = csv.writer(logs)  # writer.writerow(['string', number, ...])


def lprint(cont, log_and_print=1):
    '''Prints and logs `cont` (from content) via csv.writer(logs)

    Parameters
    --
    cont: list
    log_and_print: 0 (for logging only), 1 for both printing and logging
    '''
    if log_and_print == 1:
        print(cont)
    writer.writerow(cont)


def calc_excentricity(row):
    '''Measures the eccentricity of a bar

    Parameters
    ----------
    row: list
        In the format [Date,Open,High,Low,Close,Adj Close,Volume]

    Returns
    ----------
    list
        [mean_excentricity, positive_excentricity, negative_excentricity] per cent, relative to the open price

    Example
    ----------
        row=[Date,Open,High,Low,Close,Adj Close,Volume]
        pos_exc = (100*(high-open_))/open_
        neg_exc = (100*(open_-low))/open_
        mean_exc = (pos_exc+neg_exc)/2
    '''
    open_ = float(row[1])  # open_ has been used instead of open to avoid confusion with open(file)
    high = float(row[2])
    low = float(row[3])
    pos_exc = (100 * (high - open_)) / open_
    neg_exc = (100 * (open_ - low)) / open_
    mean_exc = (pos_exc + neg_exc) / 2
    return mean_exc, pos_exc, neg_exc


def is_valid(row0, row1, symbol, tp=False):
    '''Checks if the strategy criteria are met

    Returns
    -------
    False: If no criteria were met
    Value (float): If any of the strategy criteria is met
    '''
    result = False
    date1 = row1[0]
    o0, o1 = float(row0[1]), float(row1[1])
    h1 = float(row1[2])
    l1 = float(row1[3])
    c0, c1 = float(row0[4]), float(row1[4])

    # Case 1: bar0 down, open1 above bar0's body -> does bar1 go up?
    if ((c0 - o0) < 0) and (o1 > o0):
        if tp is False:
            result = [((c1 - o1) * 100) / o1, 1]
        else:
            if tp < ((h1 - o1) * 100) / o1:
                result = [tp, 1]
            else:
                result = [((c1 - o1) * 100) / o1, 1]

    # Case 2: bar0 up, open1 below bar0's body -> does bar1 go down?
    elif ((c0 - o0) > 0) and (o1 < o0):
        if tp is False:
            result = [(-1) * ((c1 - o1) * 100) / o1, 2]
        else:
            if tp < ((-1) * (l1 - o1) * 100) / o1:
                result = [tp, 2]
            else:
                result = [(-1) * ((c1 - o1) * 100) / o1, 2]

    if result != False:
        lprint([symbol, result[1], date1, result[0], row1], 0)
    return result


def get_symbols(sorted_symbols_path=None, row_beg=0, row_limit=50):
    '''
    Returns a list with the n top symbols by market cap, being n=row_limit
    Example of outcome: ['AAPL', 'MSFT', 'GOOG', 'GOOGL', 'AMZN']
    '''
    import csv

    sorted_symbols_path = sorted_symbols_path or SORTED_SYMBOLS_PATH
    with open(sorted_symbols_path, 'r') as fsorted:
        reader = csv.reader(fsorted)
        next(reader)
        data = list(reader)
        final = [row[0] for row in data[row_beg:row_limit]]
        print(final)
        return final


if __name__ == '__main__':
    timeframe = 5
    syms = get_symbols(row_beg=1, row_limit=3)
    for sym in syms:
        s1 = 0
        s2 = 0
        with open(DATASETS_DIR / f'{timeframe}ytd' / f'{sym}.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the headers ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            prev = next(reader)
            for rows in reader:
                res = is_valid(prev, rows, sym, 0.5)
                if res != False:
                    if res[1] == 1:
                        s1 += res[0] - 0.1
                    if res[1] == 2:
                        s2 += res[0] - 0.1
                prev = rows
        print(sym)
        print(f's1: {s1}')
        print(f's2: {s2}')

    logs.close()
