import os
import numpy as np
from math import ceil
import yahoo_fin.stock_info as si
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QCheckBox, QProgressBar
from PyQt5.QtGui import QFont

class GetHistData(QWidget):
    def __init__(self, parent=None):
        super(GetHistData, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        try:
            self.etfs = ['^FCHI']#np.load('./Data/etfs.npy').tolist()
        except FileNotFoundError:
            self.etfs = ['^FCHI']#['SPY', 'QQQ', 'TLT', 'GLD', 'IWM', 'EFA', 'HYG', 'XLV']

        self.timeframes = ['1d', '1wk', '1mo']

        etfs_rows = ceil(len(self.etfs) / 4) + 1
        tfs_rows = ceil(len(self.timeframes) / 4) + 1
        # 页面采用栅格布局
        self.grid_layout = QGridLayout()

        # 建立两个label并放入布局
        etfs_label = QLabel('Tickers')
        etfs_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.grid_layout.addWidget(etfs_label, 0, 0)


        timeframes_label = QLabel('Time frames')
        timeframes_label.setFont(QFont('Arial', 16, QFont.Bold))
        etfs_rows = ceil(len(self.etfs) / 4) + 1
        self.grid_layout.addWidget(timeframes_label, etfs_rows, 0)

        # 建立两个list分别用来存储对于etf的选择和对time frame的选择
        self.etfs_check_box = []
        self.etfs_check_box.append(QCheckBox('All'))
        self.etfs_check_box[0].setFont(QFont('Arial', 12, QFont.Bold))
        self.etfs_check_box[0].setChecked(True)
        self.grid_layout.addWidget(self.etfs_check_box[0], 0, 1)
        self.etfs_check_box[0].stateChanged.connect(lambda: self.alletfs_states(self.etfs_check_box[0]))

        self.tfs_check_box = []
        self.tfs_check_box.append(QCheckBox('All'))
        self.tfs_check_box[0].setFont(QFont('Arial', 12, QFont.Bold))
        self.tfs_check_box[0].setChecked(True)
        self.grid_layout.addWidget(self.tfs_check_box[0], etfs_rows, 1)
        self.tfs_check_box[0].stateChanged.connect(lambda: self.alltfs_states(self.tfs_check_box[0]))


        for i in range(len(self.etfs)):
            self.etfs_check_box.append(QCheckBox(self.etfs[i]))
            self.etfs_check_box[i + 1].setFont(QFont('Arial', 12, QFont.Bold))
            row = i // 4 + 1
            column = i % 4 + 1
            self.grid_layout.addWidget(self.etfs_check_box[i + 1], row, column)
            self.etfs_check_box[i + 1].stateChanged.connect(lambda: self.etfs_states(self.etfs_check_box[i + 1]))

        for i in range(3):
            self.tfs_check_box.append(QCheckBox(self.timeframes[i]))
            self.tfs_check_box[i + 1].setFont(QFont('Arial', 12, QFont.Bold))
            row = etfs_rows + i // 4 + 1
            column = i % 4 + 1
            self.grid_layout.addWidget(self.tfs_check_box[i + 1], row, column)
            self.tfs_check_box[i + 1].stateChanged.connect(lambda: self.tfs_states(self.tfs_check_box[i + 1]))

        # 添加开始按钮并加入布局
        self.start_btn = QPushButton('Start')
        self.start_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.start_btn.clicked.connect(self.get_hist_data)
        self.grid_layout.addWidget(self.start_btn, etfs_rows + tfs_rows, 0, 1, 5)

        # 建立进度条并加入布局
        self.pgb = QProgressBar(self)
        self.pgb.setFont(QFont('Arial', 12, QFont.Bold))
        self.pgb.resize(200, 100)
        self.pgb.setValue(0)
        self.pgb.setVisible(False)
        self.grid_layout.addWidget(self.pgb, etfs_rows + tfs_rows + 1, 0, 1, 5)

        self.setLayout(self.grid_layout)


    def get_hist_data(self):
        # 显示进度条
        self.pgb.setVisible(True)
        # 两个list用于存放需要更新的etf名称和对应的timeframe
        etfs_chosen = []
        tfs_chosen = []
        # 如果是第零个复选框被选中，代表需要更新所有etf的数据， 对于timeframe也是一样的道理
        if self.etfs_check_box[0].isChecked():
            etfs_chosen = self.etfs
        else:
            for i in range(1, len(self.etfs_check_box)):
                if self.etfs_check_box[i].isChecked():
                    etfs_chosen.append(self.etfs[i-1])

        if self.tfs_check_box[0].isChecked():
            tfs_chosen = self.timeframes
        else:
            for i in range(1, len(self.tfs_check_box)):
                if self.tfs_check_box[i].isChecked():
                    tfs_chosen.append(self.timeframes[i-1])

        # 文件总数
        total_files = len(etfs_chosen) * len(tfs_chosen)
        current_file = 0
        # 获取数据并存储
        if not os.path.exists('./data'):
            os.makedirs('./data')
        if not os.path.exists('./data/rawdata'):
            os.makedirs('./data/rawdata')

        for ticker in etfs_chosen:
            for interval in tfs_chosen:
                historical_price = si.get_data(ticker, interval=interval)

                # delete column 'ticker'
                historical_price = historical_price.drop(["ticker"], axis=1)

                # use date as index of the dataframe
                historical_price.index.name = "date"

                if interval == "1d":
                    interval = "daily"
                elif interval == "1wk":
                    interval = "weekly"
                    if historical_price.isnull().any().sum() > 0:
                        historical_price.dropna(how='any', inplace=True)
                    else:
                        historical_price = historical_price.iloc[:-1]
                else:
                    if historical_price.isnull().any().sum() > 0:
                        historical_price.dropna(how='any', inplace=True)
                    else:
                        historical_price = historical_price.iloc[:-1]
                    interval = "monthly"
                    # sava files
                historical_price.to_csv("./data/rawdata/" + ticker + "_" + interval + ".csv")

                # 计算当前完成的文件数量占比
                current_file += 1
                finished_ratio = int(current_file/total_files * 100)
                self.pgb.setValue(finished_ratio)


    def alletfs_states(self, cb):
        self.pgb.setValue(0)
        self.pgb.setVisible(False)
        # 如果all被选中，别的选项全都不选，这也是默认情况
        if self.etfs_check_box[0].isChecked():
            for i in range(1, len(self.etfs_check_box)):
                self.etfs_check_box[i].setChecked(False)


    def alltfs_states(self, cb):
        self.pgb.setValue(0)
        self.pgb.setVisible(False)
        # 如果all被选中，别的选项全都不选，这也是默认情况
        if self.tfs_check_box[0].isChecked():
            for i in range(1, len(self.tfs_check_box)):
                self.tfs_check_box[i].setChecked(False)


    def etfs_states(self, cb):
        self.pgb.setValue(0)
        self.pgb.setVisible(False)
        # 如果除了all之外有单独的etf被选中，则all被设置为不选中
        for i in range(1, len(self.etfs_check_box)):
            if self.etfs_check_box[i].isChecked():
                self.etfs_check_box[0].setChecked(False)
                return
        # 如果没有单独的etf被选中，则all自动被选中
        self.etfs_check_box[0].setChecked(True)


    def tfs_states(self,cb):
        self.pgb.setValue(0)
        self.pgb.setVisible(False)
        # 如果除了all之外有单独的time frame被选中，则all被设置为不选中
        for i in range(1, len(self.tfs_check_box)):
            if self.tfs_check_box[i].isChecked():
                self.tfs_check_box[0].setChecked(False)
                return
        # 如果没有单独的time frame被选中，则all自动被选中
        self.tfs_check_box[0].setChecked(True)