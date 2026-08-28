# A grid/martingale EURUSD bot on XTB, using the community `XTBApi` wrapper.
# Reads account credentials from environment variables — set these before running:
#   XTB_ACCOUNT_ID / XTB_PASSWORD
#
# Only ever run against mode='demo'. See ../../README.md for how the strategy works
# and why this approach carries real tail risk if ever pointed at a live account.

import os
from time import sleep
from datetime import datetime, time
from XTBApi.api import Client

ACCOUNT_ID = os.environ.get('XTB_ACCOUNT_ID', '')
PASSWORD = os.environ.get('XTB_PASSWORD', '')

# FIRST INIT THE CLIENT
client = Client()
# THEN LOGIN
print('\n\tLOGGING IN')
logg_in = client.login(ACCOUNT_ID, PASSWORD, mode='demo')
print('Logging info: ', logg_in)
print('\n\tLOGGED IN')


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def get_next_volume(prev_volume):
    if prev_volume == 0:
        return 0.01, 0.01
    elif prev_volume == 0.01:
        return 0.02, 0.03
    elif prev_volume == 0.03:
        return 0.04, 0.07
    elif prev_volume == 0.07:
        return 0.08, 0.15
    elif prev_volume == 0.15:
        return 0.16, 0.31
    else:
        return 0.01, 0.01


def get_orders():
    client.update_trades()
    trades = client.get_trades()
    trade_ids = {
        '0': [],  # buy
        '1': [],  # sell
        '2': [],  # buy limit
        '3': [],  # sell limit
        '4': [],  # buy stop
        '5': [],  # sell stop
        '6': [],  # balance
        '7': [],  # credit
    }
    for order in trades:
        trade_ids[str(order['cmd'])].append(order['order2'])
    return trade_ids


get_orders()

while is_time_between(time(20, 0, 0), time(4, 59, 59)):
    sleep(0.3)
else:
    bid, ask = client.get_current_bid_ask('EURUSD')
    average = round((bid + ask) / 2, 5)
    print(bid, ask, average)
    buy_volume = 0.01
    sell_volume = 0.01

    # Place a buy-limit slightly below and a sell-limit slightly above the current price
    BUY_LIMIT = client.trade_transaction(symbol='EURUSD', mode=2, trans_type=0, volume=buy_volume, price=round(average * 0.9987, ndigits=5))
    print(f'Sent BUY_LIMIT  {BUY_LIMIT}')
    SELL_LIMIT = client.trade_transaction(symbol='EURUSD', mode=3, trans_type=0, volume=sell_volume, price=round(average * 1.0013, ndigits=5))
    print(f'Sent SELL_LIMIT {SELL_LIMIT}')

    while True:
        buy_limit_id = BUY_LIMIT['order']
        sell_limit_id = SELL_LIMIT['order']

        if client.is_executed(buy_limit_id):
            print(f'\t**WARNING: {buy_limit_id} BUY LIMIT ORDER HAS BEEN EXECUTED')
            # Set the take-profit (and stop-loss, once the grid has grown enough) for every open buy
            tp_price = client.get_open_price(buy_limit_id)
            orders_id = get_orders()
            for ident in orders_id['0']:
                try:
                    print('ident:', ident)
                    print(f'>>>BUY Volume is {buy_volume}')
                    if buy_volume >= 0.15:
                        if buy_volume >= 0.31:
                            print(f'SETTING UP Take Profit for {ident} at {round(tp_price*1.00095, 5)}')
                            client.set_tp_sl(ident, 'tp', round(tp_price * 1.00095, 5))

                            print(f'***SETTING UP STOP LOSS FOR {ident} at {round(tp_price*0.9987, 5)}')
                            client.set_tp_sl(ident, 'sl', round(tp_price * 0.9987, 5))
                        else:
                            print(f'SETTING UP Take Profit for {ident} at {round(tp_price*1.00095, 5)}')
                            client.set_tp_sl(ident, 'tp', round(tp_price * 1.00095, 5))
                    else:
                        print(f'SETTING UP Take Profit for {ident} at {round(tp_price*1.0013, 5)}')
                        client.set_tp_sl(ident, 'tp', round(tp_price * 1.0013, 5))
                except Exception as exc:
                    print('* * * ERROR WITH TP AT SELL LIMIT ORDER ', ident, ':', exc)

            # Re-arm the buy limit at the next grid step (volume doubles/escalates)
            sell_volume = 0.01
            add_volume, buy_volume = get_next_volume(buy_volume)

            print('SENDING:', dict(symbol='EURUSD', mode=2, trans_type=0, volume=add_volume, price=round(tp_price * 0.9987, ndigits=5)))
            BUY_LIMIT = client.trade_transaction(symbol='EURUSD', mode=2, trans_type=0, volume=add_volume, price=round(tp_price * 0.9987, ndigits=5))

            if is_time_between(time(5, 59, 58), time(15, 0, 0)):  # so it does not open more positions after 5pm
                print('SENDING:', dict(symbol='EURUSD', mode=3, trans_type=0, volume=sell_volume, price=round(tp_price * 1.0013, ndigits=5)))
                SELL_LIMIT = client.trade_transaction(symbol='EURUSD', mode=3, trans_type=0, volume=sell_volume, price=round(tp_price * 1.0013, ndigits=5))
            else:
                print('**NOT SETTING SELL LIMIT ORDER BECAUSE OF TIME')
                SELL_LIMIT = {'order': None}  # so it does not raise an error when asking for the order number when the while loop begins

            # Deleting the previous opposite-side order
            if SELL_LIMIT['order'] != None:
                print(f'DELETING {sell_limit_id} PREVIOUS PENDING SELL LIMIT ORDER')
                print(client.delete_pending_order(sell_limit_id))
            elif SELL_LIMIT['order'] == None:
                print('**No SELL LIMIT ORDER to delete')

        elif client.is_executed(sell_limit_id):
            print(f'\t**WARNING: {sell_limit_id} SELL LIMIT ORDER HAS BEEN EXECUTED')
            tp_price = client.get_open_price(sell_limit_id)
            orders_id = get_orders()
            print(orders_id)
            for ident in orders_id['1']:
                try:
                    print('ident:', ident)
                    print(f'>>>SELL Volume is {sell_volume}')
                    if sell_volume >= 0.15:
                        if sell_volume >= 0.31:
                            print(f'SETTING UP Take Profit for {ident} at {tp_price*0.99905}')
                            client.set_tp_sl(ident, 'tp', round(tp_price * 0.99905, 5))

                            print(f'***SETTING UP STOP LOSS for {ident} at {tp_price*1.0013}')
                            client.set_tp_sl(ident, 'sl', round(tp_price * 1.0013, 5))
                        else:
                            print(f'SETTING UP Take Profit for {ident} at {tp_price*0.99905}')
                            client.set_tp_sl(ident, 'tp', round(tp_price * 0.99905, 5))
                    else:
                        print(f'SETTING UP Take Profit for {ident} at {round(tp_price*0.9987, 5)}')
                        client.set_tp_sl(ident, 'tp', round(tp_price * 0.9987, 5))
                except Exception as exc:
                    print('* * * ERROR WITH TP AT SELL LIMIT ORDER ', ident, ':', exc)

            # Re-arm the sell limit at the next grid step
            buy_volume = 0.01
            add_volume, sell_volume = get_next_volume(sell_volume)

            if is_time_between(time(5, 59, 58), time(15, 0, 0)):
                print('SENDING: ', dict(symbol='EURUSD', mode=2, trans_type=0, volume=buy_volume, price=round(tp_price * 0.9987, ndigits=5)))
                BUY_LIMIT = client.trade_transaction(symbol='EURUSD', mode=2, trans_type=0, volume=buy_volume, price=round(tp_price * 0.9987, ndigits=5))
            else:
                print('**NOT SETTING BUY LIMIT ORDER BECAUSE OF TIME')
                BUY_LIMIT = {'order': None}

            print('SENDING: ', dict(symbol='EURUSD', mode=3, trans_type=0, volume=add_volume, price=round(tp_price * 1.0013, ndigits=5)))
            SELL_LIMIT = client.trade_transaction(symbol='EURUSD', mode=3, trans_type=0, volume=add_volume, price=round(tp_price * 1.0013, ndigits=5))

            if BUY_LIMIT['order'] != None:
                print(f'DELETING {buy_limit_id} PREVIOUS PENDING BUY LIMIT ORDER')
                print(client.delete_pending_order(buy_limit_id))
            elif BUY_LIMIT['order'] == None:
                print('No BUY LIMIT ORDER TO DELETE')

        if (BUY_LIMIT['order'] == None) and (SELL_LIMIT['order'] == None):
            print('\n\n\n****FINISHED PROGRAM****\n\n\n')
            break

        # TODO (never implemented): clear out the leftover 0.01 leg once the London/NY
        # session window closes, rather than leaving it open overnight.
        # if is_time_between(time(16, 30, 0), time(0, 0, 0)):
        #     ...
