print('STRAT5 - equities')
# Hypothesis and notes: see strat5_notes.md
# This is the equities variant; strat5_candle_streak_forex.py applies the same idea to EURUSD.

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR.parent / 'datasets'
SORTED_SYMBOLS_PATH = BASE_DIR.parent / 'data_pipeline' / 'symbols folder' / 'sorted_symbols'


def is_valid(row, pc=0):
    '''Classifies a candle as a "pure" up or down move (i.e. it barely retraced
    in the opposite direction), used to detect streaks of same-direction candles.

    Returns
    -------
    (candletype, date, (neg_count, pos_count)): candletype is '+' / '-' / None
    '''
    date = row[0]
    o = float(row[1])
    h = float(row[2])
    l = float(row[3])

    if (((h - o) * 100 / o) > abs(pc)) and (((o - l) * 100 / o) < abs(pc)):
        return '+', date, (0, 1)
    elif (((h - o) * 100 / o) < abs(pc)) and (((o - l) * 100 / o) > abs(pc)):
        return '-', date, (1, 0)
    else:
        return None, date, (1, 1)


def get_symbols(sorted_symbols_path=None, row_beg=0, row_limit=50):
    import csv

    sorted_symbols_path = sorted_symbols_path or SORTED_SYMBOLS_PATH
    with open(sorted_symbols_path, 'r') as fsorted:
        reader = csv.reader(fsorted)
        next(reader)
        data = list(reader)
        final = [row[0].replace('/', '-').upper() for row in data[row_beg:row_limit]]
        print(final)
        return final


def oprint(verbose, values):
    if verbose:
        print(values)


if __name__ == '__main__':
    import csv

    syms = get_symbols(row_beg=0, row_limit=1)
    alternate = True  # bet on reversal after a streak, rather than continuation
    verbose = True
    alternate_coef = -1 if alternate else 1
    pc = 0.8
    total = 0
    count = 0
    for sym in syms:
        count += 1
        balance = 0
        try:
            with open(DATASETS_DIR / 'max_temp' / f'{sym}.csv', 'r') as f:
                results = {'pos': 0, 'neg': 0}
                reader = csv.reader(f)
                next(reader)  # Skip the headers ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                prev = next(reader)
                for row in reader:
                    outcome = 0
                    if alternate_coef * (float(prev[4]) - float(prev[1])) < 0:
                        if ((float(row[2]) - float(row[1])) * 100 / float(row[1])) < pc:
                            if ((float(row[1]) - float(row[3])) * 100 / float(row[1])) > pc:
                                oprint(verbose, (row[0], '+', pc))
                                results['pos'] += 1
                                outcome = 1
                            else:
                                oprint(verbose, (row[0], ((float(row[1]) - float(row[4])) * 100 / float(row[1]))))
                                if ((float(row[4]) - float(row[1])) * 100 / float(row[1])) > 0:
                                    results['neg'] += 1
                                    outcome = -1
                                else:
                                    results['pos'] += 1
                                    outcome = 1
                        elif (((float(row[2]) - float(row[1])) * 100 / float(row[1])) > pc) and ((float(row[1]) - float(row[3])) * 100 / float(row[1])) > pc:
                            oprint(verbose, (row[0], '-', pc, '(Indeterminate)'))
                            results['neg'] += 1
                            outcome = -1
                        else:
                            oprint(verbose, (row[0], '-', pc, '(L)'))
                            results['neg'] += 1
                            outcome = -1

                    elif alternate_coef * (float(prev[4]) - float(prev[1])) > 0:
                        if ((float(row[1]) - float(row[3])) * 100 / float(row[1])) < pc:
                            if ((float(row[2]) - float(row[1])) * 100 / float(row[1])) > pc:
                                oprint(verbose, (row[0], '+', pc))
                                results['pos'] += 1
                                outcome = 1
                            else:
                                oprint(verbose, (row[0], ((float(row[4]) - float(row[1]))) * 100 / float(row[1])))
                                if ((float(row[4]) - float(row[1])) * 100 / float(row[1])) > 0:
                                    results['pos'] += 1
                                    outcome = 1
                                else:
                                    results['neg'] += 1
                                    outcome = -1
                        elif (((float(row[1]) - float(row[3])) * 100 / float(row[1])) > pc) and (((float(row[2]) - float(row[1])) * 100 / float(row[1])) > pc):
                            oprint(verbose, (row[0], '-', pc, '(Indeterminate)'))
                            results['neg'] += 1
                            outcome = -1
                        else:
                            oprint(verbose, (row[0], '-', pc, '(L)'))
                            results['neg'] += 1
                            outcome = -1
                    balance += outcome
                    prev = row
            oprint(verbose, results)
            print(sym, results['pos'] / results['neg'])
            total += results['pos'] / results['neg']
            oprint(verbose, balance)
        except FileNotFoundError:
            print(f'***COULD NOT OPEN {sym}')
    print(total / count)
