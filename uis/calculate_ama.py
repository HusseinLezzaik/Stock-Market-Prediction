import numpy as np

def calculate_ama(raw_data, data_stats, price_type='close',er_window = 9, slow_window = 20, fast_window = 4):
    er_window = er_window
    slow_window = slow_window
    fast_window = fast_window
    price = price_type

    # step1: calculate ER (Efficiency Ratio)
    price = np.array(raw_data[price])
    open_price = np.array(raw_data['open'])
    close_price = np.array(raw_data['close'])
    tr = np.array(data_stats['tr'])
    er = np.zeros_like(price)
    pn_er = np.zeros_like(price)
    er[0:er_window] = 1
    for i in range(er_window, len(er)):
        direction = price[i] - price[i - er_window]
        volatility = [price[i] - price[i - 1] for i in range(i, i - er_window, -1)]
        volatility = sum(abs(np.array(volatility)))
        pn_er[i] = direction / volatility
        er[i] = abs(direction / volatility)

    # step2 calculate SCS, SCF and SSC
    scs = 2 / (slow_window + 1)
    scf = 2 / (fast_window + 1)
    ssc = (er * scf + (1 - er) * scs)

    # step3 calculate ama
    ama = np.zeros_like(er)
    ama[0] = price[0]
    for i in range(1, len(ama)):
        # if pn_er[i] > 0.1:
        #     ama[i] = ama[i - 1] + 0.5 * ssc[i] * (min(open_price[i], close_price[i]) - ama[i - 1] - pn_er[i] * tr[i])
        # if -0.1 <= pn_er[i] <= 0.1:
        #     ama[i] = ama[i - 1] + ssc[i] * (min(open_price[i], close_price[i]) - ama[i - 1])
        # if pn_er[i] < -0.1:
        #     ama[i] = ama[i - 1] + 0.5 * ssc[i] * (max(open_price[i], close_price[i]) - ama[i - 1] + pn_er[i] * tr[i])
        ama[i] = ama[i - 1] + ssc[i] * (min(open_price[i], close_price[i]) - ama[i - 1])
    return ama, pn_er, ssc