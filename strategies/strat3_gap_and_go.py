print('STRAT3')

from datetime import datetime
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR.parent / 'datasets'
SORTED_SYMBOLS_PATH = BASE_DIR.parent / 'data_pipeline' / 'symbols folder' / 'sorted_symbols'

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
now = datetime.now().strftime("%y_%m_%d-%H_%M_%S")
logs = open(LOGS_DIR / f"logfile-{now}.csv", "a", newline='')
writer = csv.writer(logs)


def lprint(cont, log_and_print=1):
    if log_and_print == 1:
        print(cont)
    writer.writerow(cont)


def is_valid(row0, row1, row2, sym, gap_pc=0):
    '''3-candle pattern: bar1 gaps clean away from bar0 in the direction bar0 closed, and
    holds that gap all the way through the close of bar2. Checks if the strategy criteria are met.

    Returns
    -------
    [0, 0]: If no criteria were met
    [1, result, date]: If the pattern matched, where `result` is bar2's return (%) counter to the gap direction
    '''
    date1 = row1[0]
    o0, o1, o2 = float(row0[1]), float(row1[1]), float(row2[1])
    c0, c1, c2 = float(row0[4]), float(row1[4]), float(row2[4])

    if (o1 > o0 * (1 + (gap_pc / 100))) and (o1 > c0 * (1 + (gap_pc / 100))) and (c1 > o0 * (1 + (gap_pc / 100))) and (c1 > c0 * (1 + (gap_pc / 100))) and (c1 > o2 * (1 + (gap_pc / 100))) and (o1 > o2 * (1 + (gap_pc / 100))) and (c0 - o0) > 0:
        lprint([sym, '+', date1, (o2 - c2) * 100 / o2])
        return [1, (o2 - c2) * 100 / o2, date1]
    elif (o1 < o0 * (1 - (gap_pc / 100))) and (o1 < c0 * (1 - (gap_pc / 100))) and (c1 < o0 * (1 - (gap_pc / 100))) and (c1 < c0 * (1 - (gap_pc / 100))) and (c1 < o2 * (1 - (gap_pc / 100))) and (o1 < o2 * (1 - (gap_pc / 100))) and (c0 - o0) < 0:
        lprint([sym, '-', date1, (c2 - o2) * 100 / o2])
        return [1, (c2 - o2) * 100 / o2, date1]
    else:
        return [0, 0]


def get_symbols(sorted_symbols_path=None, row_beg=0, row_limit=50):
    import csv

    sorted_symbols_path = sorted_symbols_path or SORTED_SYMBOLS_PATH
    with open(sorted_symbols_path, 'r') as fsorted:
        reader = csv.reader(fsorted)
        next(reader)
        data = list(reader)
        return [row[0].replace('/', '-').upper() for row in data[row_beg:row_limit]]


if __name__ == '__main__':
    syms = get_symbols(row_beg=0, row_limit=20)
    total = {'count': 0, 'value': 0, 'overall_count': 0, 'overall_value': 0}
    for sym in syms:
        total['count'] = 0
        total['value'] = 0
        try:
            with open(DATASETS_DIR / '10ytd' / f'{sym}.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip the headers ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                row0 = next(reader)
                row1 = next(reader)
                for row in reader:
                    row2 = row
                    res = is_valid(row0, row1, row2, sym, 1)
                    row0 = row1
                    row1 = row2
                    total['count'] += res[0]
                    total['value'] += res[1]
            if total['count'] != 0:
                print(total['value'] / total['count'])
            else:
                print((sym, 0, 0))
        except FileNotFoundError:
            print(f'***COULD NOT OPEN {sym}')
        total['overall_count'] += total['count']
        total['overall_value'] += total['value']

    print(total['overall_value'] / total['overall_count'])

    logs.close()
