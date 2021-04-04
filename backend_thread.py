import time
import numpy as np
import yahoo_fin.stock_info as si
from PyQt5.QtCore import QThread, pyqtSignal
from data_processing.download_data import download_data


class GetLivePrice(QThread):
    # 产生信号, 用于传输数据和通知UI进行更改
    update_data = pyqtSignal(list)

    # 从本地读取etf名称
    # Haifei: etfs = np.load('./Data/etfs.npy').tolist()
    #Elona:
    def run(self):
        etfs=['^FCHI',]
        while True:
            for etf in etfs:
                live_price_array = []
                live_price = si.get_live_price(etf)
                live_price = round(live_price, 2)
                live_price_array.append(live_price)

                print(live_price)

            # 通过emit发送信号
                self.update_data.emit(live_price_array)

            # 每十秒更新一次数据
            time.sleep(30)


class UpdateHistData(QThread):
    #Elona Comment : etfs = np.load('./Data/etfs.npy').tolist()
    tfs = ['1d', '1wk', '1mo']
    update_hist_data_signal = pyqtSignal(str)

    def run(self):
        #Haifei
        #download_data(self.etfs, self.tfs)
        #Elona
        download_data(['^FCHI',], self.tfs)
        self.update_hist_data_signal.emit('finish')