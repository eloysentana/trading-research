# Date,Open,High,Low,Close,Adj Close,Volume
# Hypothesis and full writeup: see strat2_notes.md

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
    '''
    open_ = float(row[1])
    high = float(row[2])
    low = float(row[3])
    pos_exc = (100 * (high - open_)) / open_
    neg_exc = (100 * (open_ - low)) / open_
    mean_exc = (pos_exc + neg_exc) / 2
    return mean_exc, pos_exc, neg_exc


def is_valid(row0, row1, symbol, pc):
    '''Checks if the strategy criteria are met: bar0 moved more than `pc`% in either direction.

    Returns
    -------
    False: If no criteria were met
    Values (list): [pos_exc %, neg_exc %, close-open (final day's result) %] of the FOLLOWING bar
    '''
    date1 = row1[0]
    o0, o1 = float(row0[1]), float(row1[1])
    h1 = float(row1[2])
    l1 = float(row1[3])
    c0, c1 = float(row0[4]), float(row1[4])
    if abs((c0 - o0) * 100 / o0) > pc:
        lprint([symbol, date1, (h1 - o1) * 100 / o1, (l1 - o1) * 100 / o1, (c1 - o1) * 100 / o1], 0)
        return (h1 - o1) * 100 / o1, (l1 - o1) * 100 / o1, (c1 - o1) * 100 / o1
    else:
        return False


def get_symbols(sorted_symbols_path=None, row_beg=0, row_limit=50):
    import csv

    sorted_symbols_path = sorted_symbols_path or SORTED_SYMBOLS_PATH
    with open(sorted_symbols_path, 'r') as fsorted:
        reader = csv.reader(fsorted)
        next(reader)
        data = list(reader)
        final = [row[0] for row in data[row_beg:row_limit]]
        return final


def calc_indiv(sym, pc=0, tp_pos=False, tp_neg=False, timeframe=10):
    '''Measures the mean eccentricity (both positive and negative) of all the candles that met the
    strategy criteria for ONE symbol. Example: calc_indiv('AAPL', 5, 0.5, 0.4, 5)

    Parameters
    ----------
    sym: Symbol to test
    pc: Minimum % move required in the previous day's candle
    tp_pos: Take profit for the 'Buy' side (checked against the high first)
    tp_neg: Take profit for the 'Sell' side (checked against the low first)
    timeframe: Which dataset folder to read from (e.g. '5ytd', '10ytd')

    Returns
    -------
    [0]: (dict) {'date1':[pos_exc, neg_exc], ...}
    [1]: (list) [tot_pos_exc/count, tot_neg_exc/count] - average eccentricity for both sides
    [2]: (list) [pos_fail/count, neg_fail/count] - how often the take-profit was NOT reached
    [3]: (dict) {'date1':[pos_res, neg_res], ...} - realized result per side per date
    [4]: (list) [tot_pos_res/count, tot_neg_res/count] - average % earned per side
    [5]: (int) count - number of times the criteria was met
    [6]: (list) [general_tot_pos_exc/row_count, general_tot_neg_exc/row_count] - average eccentricity across ALL days, not just qualifying ones
    [7]: (list) [pos_size/row_count, neg_size/row_count] - average candle size, both directions
    '''
    general_tot_pos_exc = 0
    general_tot_neg_exc = 0
    tot_pos_exc, tot_neg_exc = 0, 0
    count = 0
    pos_fail, neg_fail = 0, 0
    tot_pos_res, tot_neg_res = 0, 0
    row_count = 0
    pos_size = 0
    neg_size = 0

    returned = [
        {},  # [0]
        [0, 0],  # [1]
        [0, 0],  # [2]
        {},  # [3]
        [0, 0],  # [4]
        count,  # [5]
        [0, 0],  # [6]
        [0, 0],  # [7]
    ]
    try:
        with open(DATASETS_DIR / f'{timeframe}ytd' / f'{sym}.csv', 'r') as f:
            import csv
            reader = csv.reader(f)
            next(reader)  # Skip the headers ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            prev = next(reader)
            for row in reader:
                row_count += 1
                returned[0][row[0]] = []
                returned[3][row[0]] = []

                daily_outcome = (float(row[1]) - float(row[4])) * 100 / float(row[1])
                if daily_outcome >= 0:
                    pos_size += daily_outcome
                elif daily_outcome < 0:
                    neg_size += abs(daily_outcome)

                general_tot_pos_exc += (float(row[2]) - float(row[1])) * 100 / float(row[1])
                general_tot_neg_exc += (float(row[1]) - float(row[3])) * 100 / float(row[1])

                res = is_valid(prev, row, sym, pc)

                if res:
                    returned[0][row[0]].append(res[0])
                    returned[0][row[0]].append(res[1])
                    tot_pos_exc += res[0]
                    tot_neg_exc += res[1]

                    if tp_pos != False:
                        if abs(res[0]) < tp_pos:
                            pos_fail += 1
                            returned[3][row[0]].append((float(row[4]) - float(row[1])) * 100 / float(row[1]))
                        else:
                            returned[3][row[0]].append(tp_pos)
                        tot_pos_res += returned[3][row[0]][0]

                    if tp_neg != False:
                        if abs(res[1]) < tp_neg:
                            neg_fail += 1
                            returned[3][row[0]].append((float(row[4]) - float(row[1])) * 100 / float(row[1]))
                        else:
                            returned[3][row[0]].append(-tp_neg)
                        tot_neg_res += returned[3][row[0]][1]

                    count += 1

                prev = row
    except Exception as exc:
        print(f'\nERROR OPENING THE FILE OF {sym}:{exc}\n')
        return False

    returned[1][0] = tot_pos_exc / count
    returned[1][1] = -tot_neg_exc / count
    returned[2][0] = pos_fail / count
    returned[2][1] = neg_fail / count
    returned[4][0] = tot_pos_res / count
    returned[4][1] = -tot_neg_res / count
    returned[5] = count
    returned[6][0] = general_tot_pos_exc / row_count
    returned[6][1] = general_tot_neg_exc / row_count
    returned[7][0] = pos_size / row_count
    returned[7][1] = neg_size / row_count

    return returned


if __name__ == '__main__':
    counter = 0
    mean_exc = [0, 0]
    fail_trade = [0, 0]
    profit_trade = [0, 0]
    selected_pos = []
    selected_neg = []
    mean_gen_exc = [0, 0]
    total_count = 0

    syms = get_symbols(row_beg=0, row_limit=1)

    for sym in syms:
        sym = sym.replace('/', '-').upper()
        try:
            s = calc_indiv(sym=sym, pc=5, tp_pos=1, tp_neg=1, timeframe=10)

            print(f'\n\n{sym}: {s[5]}')  # symbol and number of qualifying operations
            counter += 1

            print(f'mean exc: {s[1]}')
            print(f'mean general exc: {s[6][0], s[6][1]}')
            print(f'fail/trade: {s[2]}')
            print(f'average size: {s[7]}')
            print(f'profit/trade: {s[4]}')

            if s[1][0] > 3:
                selected_pos.append(sym)
            if s[1][1] > 3:
                selected_neg.append(sym)

            mean_exc[0] += s[1][0]
            mean_exc[1] += s[1][1]
            fail_trade[0] += s[2][0]
            fail_trade[1] += s[2][1]
            profit_trade[0] += s[4][0]
            profit_trade[1] += s[4][1]
            mean_gen_exc[0] += s[6][0]
            mean_gen_exc[1] += s[6][1]
            total_count += s[5]

        except Exception as exc:
            print(f'\n\n\nERROR WITH SYMBOL {sym}: {exc}')

    print('\n\n------GENERAL INFORMATION------')
    print(f'mean exc: {[mean_exc[i]/counter for i in range(0,2)]}')
    print(f'mean_gen_exc: {mean_gen_exc[0]/counter, mean_gen_exc[1]/counter}')
    print(f'fail/trade: {[fail_trade[i]/counter for i in range(0,2)]}')
    print(f'profit/trade: {[profit_trade[i]/counter for i in range(0,2)]}\n\n')

    print(total_count)
    print(selected_pos)
    print(selected_neg)

    logs.close()
