import os
import numpy as np
import pandas as pd
import stockstats
from uis.calculate_ama import calculate_ama
from data_processing.load_data import load_rawdata


class AMADataBuilder():
    def __init__(self, price_type='close', er_window=3, slow_window=22, fast_window=4):
        self.price_type = price_type
        self.er_window = er_window
        self.slow_window = slow_window
        self.fast_window = fast_window

    def build_model_data(self, ticker, time_frame):
        raw_data = load_rawdata(ticker, time_frame)
        data_stats = stockstats.StockDataFrame.retype(raw_data.copy())
        columns = ['ama', 'pn_er',  'tr', 'target']
        ama, pn_er, ssc = calculate_ama(raw_data, data_stats, self.price_type, self.er_window, self.slow_window, self.fast_window)
        tr = np.array(data_stats['tr'])
        tr[0] = abs(raw_data.iloc[0]['open'] - raw_data.iloc[0]['close'])
        # 计算target
        target = []
        price_open = np.array(raw_data['open'])
        price_close = np.array(raw_data['close'])
        target.append(price_close[0])
        for i in range(1, len(price_open)):
            if pn_er[i] > -0.1:
                target.append(min(price_close[i], price_open[i]) - pn_er[i] * tr[i])
            else:
                target.append(max(price_close[i], price_open[i] - 0.3 * pn_er[i] * tr[i]))
        #对ama曲线进行指数平滑， 窗口取7
        if time_frame == 'weekly':
            for i in range(1, len(target)):
                target[i] = (2 * target[i] + 6 * target[i-1])/8
        else:
            for i in range(1, len(target)):
                target[i] = (2 * target[i] + 9 * target[i-1])/11

        model_data = np.array([ama, pn_er, tr, target]).T
        print(model_data.shape)
        model_data = pd.DataFrame(model_data, index=raw_data.index, columns=columns)
        self.save_model_data(model_data, ticker, time_frame)


    def save_model_data(self, model_data, ticker, time_frame):
        if not os.path.exists('./Data'):
            os.makedirs('./Data')
        if not os.path.exists('./Data/modeldata'):
            os.makedirs('./Data/modeldata')
        if not os.path.exists('Data/modeldata/ama_data'):
            os.makedirs('Data/modeldata/ama_data')
        model_data.to_csv("Data/modeldata/ama_data/" + ticker + "_" + time_frame + "_modeldata.csv")


class SVMDataBuilder():
    # the input includes Underlying object, how many candles to check trend and how many candles to predict
    def __init__(self,  look_hist_window=4, trend_check_window=4):

        self.look_hist_window = look_hist_window
        self.trend_check_window = trend_check_window


    def build_trend_data(self, raw_data):
        trend = np.ones(len(raw_data))
        price = np.array(raw_data['close'])
        # first loop: strong trend
        for i in range(len(raw_data)-self.trend_check_window):
            if price[i] > price[i + self.trend_check_window]:
                trend[i] = -1

        return trend

    def build_model_data(self, ticker, time_frame):
        raw_data = load_rawdata(ticker, time_frame)
        data_stats = stockstats.StockDataFrame.retype(raw_data.copy())
        raw_data['trend'] = self.build_trend_data(raw_data)


        if time_frame == 'monthly':
            raw_data['ema'] = (data_stats["close_12_ema"].round(2))
        else:
            raw_data['ema'] = (data_stats["close_20_ema"].round(2))
        raw_data['rsi'] = data_stats['rsi_6']
        raw_data['cci'] = data_stats['cci']
        raw_data['macd'] = data_stats['macd']
        raw_data['kdjk'] = data_stats['kdjk']
        raw_data['kdjd'] = data_stats['kdjd']
        raw_data['wr'] = data_stats['wr_6']

        columns = ['h-l', 'c-o', 'h-cp', 'l-cp', 'diff_ema', 'diff_volume', 'cci', 'rsi', 'macd', 'kdjk', 'kdjd', 'wr',
                   'trend']
        new_columns = []
        # create new columns name
        for i in range(self.look_hist_window):
            offset = i + 1
            for indicator in columns:
                new_columns.append(indicator + '_' + str(offset))

        # create new data frame
        model_data = pd.DataFrame(columns=new_columns)

        # use look_hist_window(equals 4 default) candles to build the input data of current candles trend
        raw_data['h-l'] = raw_data['high'] - raw_data['low']
        raw_data['c-o'] = raw_data['open'] - raw_data['low']
        raw_data['h-cp'] = raw_data['high'] - raw_data['close'].shift(1)
        raw_data['l-cp'] = raw_data['low'] - raw_data['close'].shift(1)
        raw_data['diff_ema'] = raw_data['close'] - raw_data['ema']
        raw_data['diff_volume'] = raw_data['volume'].pct_change()
        for i in range(1, self.look_hist_window + 1):
            model_data[new_columns[(i - 1) * 13:i * 13]] = raw_data[['h-l', 'c-o', 'h-cp', 'l-cp',
                                                                     'diff_ema', 'diff_volume', 'cci', 'rsi',
                                                                     'macd', 'kdjk', 'kdjd', 'wr','trend']].shift(i).copy()
        # self.model_data = self.model_data.set_index(self.raw_data.index)
        model_data = round(model_data, 2)
        model_data['target'] = raw_data['trend']
        self.save_model_data(ticker, time_frame, model_data)

    def save_model_data(self, ticker, time_frame, model_data):
        if not os.path.exists('./Data'):
            os.makedirs('./Data')
        if not os.path.exists('./Data/modeldata'):
            os.makedirs('./Data/modeldata')
        if not os.path.exists('Data/modeldata/svm_data'):
            os.makedirs('Data/modeldata/svm_data')
        model_data.to_csv("Data/modeldata/svm_data/" + ticker + "_" + time_frame + "_modeldata.csv")

if __name__ == '__main__':
    try:
        etfs = ['^FCHI',]#np.load('./Data/etfs.npy').tolist()
    except FileNotFoundError:
        etfs = ['^FCHI',]#['SPY', 'QQQ', 'TLT', 'GLD', 'IWM', 'EFA', 'HYG', 'XLV']
    tfs = ['weekly', 'monthly']
    ama_builder = AMADataBuilder()
    svm_builder = SVMDataBuilder()
    for ticker in etfs:
        for tf in tfs:
            print(ticker, tf)
            ama_builder.build_model_data(ticker, tf)
            svm_builder.build_model_data(ticker, tf)