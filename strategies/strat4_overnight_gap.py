print('STRAT4')

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


def is_valid(row0, row1, sym, gap_pc=0):
    '''Stripped-down overnight-gap diagnostic: just logs every day where the open
    gapped away from the previous close by more than `gap_pc`%.'''
    date1 = row1[0]
    o1 = float(row1[1])
    c0 = float(row0[4])

    if abs((c0 - o1) * 100 / c0) > gap_pc:
        lprint([sym, '+', date1, (o1 - c0) * 100 / c0])


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

    for sym in syms:
        try:
            with open(DATASETS_DIR / '5ytd' / f'{sym}.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip the headers ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                row0 = next(reader)
                for row in reader:
                    row1 = row
                    is_valid(row0, row1, sym, 5)
                    row0 = row1
        except FileNotFoundError:
            print(f'***COULD NOT OPEN {sym}')

    logs.close()
