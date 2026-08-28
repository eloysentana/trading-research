# Standalone REPL for sanity-checking the martingale math behind martingale_bot.py
# before running it live. After each round, type 1 if the buy side hit its
# take-profit, 2 if the sell side did, and anything else (e.g. Ctrl+C) to see the totals.

ans = 0
total1 = 0
total2 = 0
spread1 = 0.0001
spread2 = 0.00008
gain = 0.001
buy_equity = 100
sell_equity = 100
prev = 1
while True:
    try:
        ans = float(input('RESULT: '))
        if ans == 1:
            total1 += buy_equity * (gain - spread1)
            total2 += buy_equity * (gain - spread2)
            total1 -= sell_equity * gain
            total2 -= sell_equity * gain
            sell_equity *= 2
            buy_equity = 100

        if ans == 2:
            total1 += sell_equity * (gain - spread1)
            total2 += sell_equity * (gain - spread2)
            total1 -= buy_equity * gain
            total2 -= buy_equity * gain
            buy_equity *= 2
            sell_equity = 100
    except:
        print(f'Result with spread {spread1} is {total1}')
        print(f'Result with spread {spread2} is {total2}')
        break
