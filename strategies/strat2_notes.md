# Strat 2 — post-shock volatility straddle

This strategy tries to take advantage of the volatility and confusion after a big
movement in the markets. For example, when a stock moves more than 5% in one day,
some volatility is expected the next day, since confusion still reigns around that stock.

If we buy and sell at the open, each with a take-profit, we can capture a profit without
actually having to guess the direction of the follow-through move.

If we observe that after such a big candle, the next day's candle tends to move some
percentage up **and** some percentage down, we can buy and sell at the opening — closing
the long position once it reaches a percentage above the opening, and closing the short
position once it falls to some percentage below the opening.

**Example** (the previous day the XYZ symbol moved +5%):

- 9am: Market opens at $100 → Buy n shares with a take-profit at 0.5% ($100.50), and Sell n shares with a take-profit at 0.5% ($99.50)
- 1pm: XYZ price reaches $100.50 → Close 'Buy' position with 0.5% profit
- 3pm: XYZ price falls to $99.50 → Close 'Sell' position with 0.5% profit
- Final profit: 1%

**Notes and considerations**

1. Since a candle doesn't always move 0.5% up *and* down, sometimes a position may be left unclosed and end up with a loss.
