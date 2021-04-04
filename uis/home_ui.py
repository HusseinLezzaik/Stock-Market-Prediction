import pandas as pd
import numpy as  np
pd.set_option('mode.chained_assignment', None)
import yahoo_fin.stock_info as si
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel
from PyQt5.QtGui import  QFont, QColor
from PyQt5.QtCore import Qt
from uis.calculate_ama import calculate_ama
from data_processing.load_data import load_rawdata, load_ama_modeldata

import stockstats


class Home(QWidget):
    # show the table of price track
    def __init__(self, parent=None):
        super(Home, self).__init__(parent)
        # 设置表格的列名称
        self.columns = ['ETF', 'current', 'pre close', 'net change', 'pct change', 'open', 'high', 'low', 'volume', 'ama', 'ema12', 'ema20']
        

        # 创建两个data frame来存储需要显示的数据
        self.weekly_data = pd.DataFrame(columns=self.columns)
        self.monthly_data = pd.DataFrame(columns=self.columns)

        # 获取本地的etf名称列表
        try:
            self.etfs = ['^FCHI']#np.load('./Data/etfs.npy').tolist()
        except FileNotFoundError:
            self.etfs = ['^FCHI']#['SPY', 'QQQ', 'TLT', 'GLD', 'IWM', 'EFA', 'HYG', 'XLV']

        self.tfs = ['weekly', 'monthly']

        # 本页面使用垂直布局
        layout = QVBoxLayout()

        # weekly表格的表名称
        self.weekly_label = QLabel('Weekly ETF Price Dashboard')
        self.weekly_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.weekly_label.setContentsMargins(0, 10, 0, 10)
        layout.addWidget(self.weekly_label)

        # 创建weekly的表格
        self.weekly_table = QTableWidget()
        self.weekly_table.setRowCount(len(self.etfs))
        self.weekly_table.setColumnCount(12)
        # self.horizontalHeader().setStretchLastSection(True)
        self.weekly_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.horizontalHeader().setFixedHeight(80)
        self.weekly_table.horizontalHeader().setMinimumHeight(60)
        self.weekly_table.horizontalHeader().setFont(QFont(QFont('Arial', 12, QFont.Bold)))
        self.weekly_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置默认行高
        self.weekly_table.verticalHeader().setDefaultSectionSize(42)
        self.weekly_table.setHorizontalHeaderLabels(self.columns)

        # 禁止编辑
        self.weekly_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 整行选择
        self.weekly_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.weekly_table.setSelectionMode(QAbstractItemView.NoSelection)
        # 自动调整行和列
        # price_table.resizeColumnsToContents()
        # price_table.resizeRowsToContents()
        # 隐藏纵向header
        self.weekly_table.verticalHeader().setVisible(False)

        # 将weekly table加入布局
        layout.addWidget(self.weekly_table)


        # 添加monthly table
        # weekly表格的表名称
        self.monthly_label = QLabel('Monthly ETF Price Dashboard')
        self.monthly_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.monthly_label.setContentsMargins(0, 10, 0, 10)
        layout.addWidget(self.monthly_label)

        # 创建weekly的表格
        self.monthly_table = QTableWidget()
        self.monthly_table.setRowCount(len(self.etfs))
        self.monthly_table.setColumnCount(12)
        self.monthly_table.setGeometry(50, 50, 800, 640)
        # 设置按窗口伸缩
        self.monthly_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.horizontalHeader().setFixedHeight(80)
        self.monthly_table.horizontalHeader().setMinimumHeight(60)
        self.monthly_table.horizontalHeader().setFont(QFont(QFont('Arial', 12, QFont.Bold)))
        self.monthly_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置默认行高
        self.monthly_table.verticalHeader().setDefaultSectionSize(42)
        self.monthly_table.setHorizontalHeaderLabels(self.columns)

        # 禁止编辑
        self.monthly_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 整行选择
        self.monthly_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.monthly_table.setSelectionMode(QAbstractItemView.NoSelection)
        # 自动调整行和列
        # price_table.resizeColumnsToContents()
        # price_table.resizeRowsToContents()
        # 隐藏纵向header
        self.monthly_table.verticalHeader().setVisible(False)

        # 将weekly table加入布局
        layout.addWidget(self.monthly_table)

        self.setLayout(layout)

        # 载入并显示数据
        self.load_data()

        # 直接下载最新数据并显示
        self.show_live_price(data = None)


    def load_data(self):
        for tf in self.tfs:
            index = -1
            for etf in self.etfs:
                index += 1
                data = load_rawdata(etf, tf)
                if data is None:
                    continue

                data_stats = stockstats.StockDataFrame.retype(data.copy())
                data[['ema12', 'ema20']] = data_stats[['close_12_ema', 'close_20_ema']]
                # 数值保留两位小数
                data[['open', 'high', 'low', 'close', 'ema12', 'ema20']] = data[
                    ['open', 'high', 'low', 'close', 'ema12', 'ema20']].round(decimals=2)
                # ama = calculate_ama(data, data_stats)[0][-1]

                # 计算ama
                ama, _, _ = calculate_ama(data, data_stats)
                ama = ama[-1]

                # 获取倒数第二行数据，是最新的
                tmp = data.iloc[-1]
                dict = {'ETF': etf,
                        'current': tmp['close'],
                        'pre close': data.iloc[-2]['close'],
                        'net change': round(tmp['close'] - data.iloc[-2]['close']),
                        'pct change': round((tmp['close'] / data.iloc[-2]['close'] -1) * 100, 2),
                        'open': tmp['open'],
                        'high': tmp['high'],
                        'low': tmp['low'],
                        'volume': int(tmp['volume']),
                        'ama': round(ama, 2),
                        'ema12': tmp['ema12'],
                        'ema20': tmp['ema20']}
                df = pd.DataFrame(dict, index=[index])
                if tf == 'weekly':
                    self.weekly_data = self.weekly_data.append(df, ignore_index=True)
                if tf == 'monthly':
                    self.monthly_data = self.monthly_data.append(df, ignore_index=True)



    def show_live_price(self, data):
        if data is None:
            data = []
            for etf in self.etfs:
                live_price = si.get_live_price(etf)
                live_price = round(live_price, 2)
                data.append(live_price)
        # data是一个list，是各个etf的最新价格
        for i in range(0, len(self.etfs)):
            # 0.设置ETF列
            etf_weekly = QTableWidgetItem(self.etfs[i])
            etf_weekly.setTextAlignment(Qt.AlignCenter)
            etf_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            self.weekly_table.setItem(i, 0, etf_weekly)

            etf_monthly = QTableWidgetItem(self.etfs[i])
            etf_monthly.setTextAlignment(Qt.AlignCenter)
            etf_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            self.monthly_table.setItem(i, 0, etf_monthly)


            # 1.设置current列
            cur_weekly = QTableWidgetItem(str(data[i]))
            cur_weekly.setTextAlignment(Qt.AlignCenter)
            cur_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            if data[i] >= self.weekly_data.iloc[i]['pre close']:
                wup = 1
                cur_weekly.setForeground(QColor(0, 255, 0))
            else:
                wup = 0
                cur_weekly.setForeground(QColor(255, 0, 0))
            self.weekly_table.setItem(i, 1, cur_weekly)

            cur_monthly = QTableWidgetItem(str(data[i]))
            cur_monthly.setTextAlignment(Qt.AlignCenter)
            cur_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            if data[i] >= self.monthly_data.iloc[i]['pre close']:
                mup = 1
                cur_monthly.setForeground(QColor(0, 255, 0))
            else:
                mup = 0
                cur_monthly.setForeground(QColor(255, 0, 0))
            self.monthly_table.setItem(i, 1, cur_monthly)

            # 2.设置pre close列
            preclose_weekly = QTableWidgetItem(str(self.weekly_data.iloc[i]['pre close']))
            preclose_weekly.setTextAlignment(Qt.AlignCenter)
            preclose_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            self.weekly_table.setItem(i, 2, preclose_weekly)

            preclose_monthly = QTableWidgetItem(str(self.monthly_data.iloc[i]['pre close']))
            preclose_monthly.setTextAlignment(Qt.AlignCenter)
            preclose_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            self.monthly_table.setItem(i, 2, preclose_monthly)


            # 3.设置net change
            net_change = round(data[i] - self.weekly_data.iloc[i]['pre close'], 2)
            net_weekly = QTableWidgetItem(str(net_change))
            net_weekly.setTextAlignment(Qt.AlignCenter)
            net_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            if  wup == 1:
                net_weekly.setForeground(QColor(0, 255, 0))
            else:
                net_weekly.setForeground(QColor(255, 0, 0))
            self.weekly_table.setItem(i, 3, net_weekly)

            net_change = round(data[i] - self.monthly_data.iloc[i]['pre close'], 2)
            net_monthly = QTableWidgetItem(str(net_change))
            net_monthly.setTextAlignment(Qt.AlignCenter)
            net_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            if mup == 1:
                net_monthly.setForeground(QColor(0, 255, 0))
            else:
                net_monthly.setForeground(QColor(255, 0, 0))
            self.monthly_table.setItem(i, 3, net_monthly)


            # 4.设施pct列
            pct_change = round((data[i]/self.weekly_data.iloc[i]['pre close'] - 1) * 100, 2)
            pct_weekly = QTableWidgetItem(str(pct_change)+'%')
            pct_weekly.setTextAlignment(Qt.AlignCenter)
            pct_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            if wup == 1:
                pct_weekly.setForeground(QColor(0, 255, 0))
            else:
                pct_weekly.setForeground(QColor(255, 0, 0))
            self.weekly_table.setItem(i, 4, pct_weekly)

            pct_change = round((data[i] / self.monthly_data.iloc[i]['pre close'] - 1) * 100, 2)
            pct_monthly = QTableWidgetItem(str(pct_change)+'%')
            pct_monthly.setTextAlignment(Qt.AlignCenter)
            pct_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            if mup == 1:
                pct_monthly.setForeground(QColor(0, 255, 0))
            else:
                pct_monthly.setForeground(QColor(255, 0, 0))
            self.monthly_table.setItem(i, 4, pct_monthly)


            # 5.设置open列
            open_weekly = QTableWidgetItem(str(self.weekly_data.iloc[i]['open']))
            open_weekly.setTextAlignment(Qt.AlignCenter)
            open_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            self.weekly_table.setItem(i, 5, open_weekly)

            open_monthly = QTableWidgetItem(str(self.monthly_data.iloc[i]['open']))
            open_monthly.setTextAlignment(Qt.AlignCenter)
            open_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            self.monthly_table.setItem(i, 5, open_monthly)

            # 6.设置high列
            if data[i] > self.weekly_data.iloc[i]['high']:
                self.weekly_data.iloc[i]['high'] = data[i]
            high_weekly = QTableWidgetItem(str(self.weekly_data.iloc[i]['high']))
            high_weekly.setTextAlignment(Qt.AlignCenter)
            high_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            self.weekly_table.setItem(i, 6, high_weekly)

            if data[i] > self.monthly_data.iloc[i]['high']:
                self.monthly_data.iloc[i]['high'] = data[i]
            high_monthly = QTableWidgetItem(str(self.monthly_data.iloc[i]['high']))
            high_monthly.setTextAlignment(Qt.AlignCenter)
            high_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            self.monthly_table.setItem(i, 6, high_monthly)

            # 7.设置low列
            if data[i] < self.weekly_data.iloc[i]['low']:
                self.weekly_data.iloc[i]['low'] = data[i]
            low_weekly = QTableWidgetItem(str(self.weekly_data.iloc[i]['low']))
            low_weekly.setTextAlignment(Qt.AlignCenter)
            low_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            self.weekly_table.setItem(i, 7, low_weekly)

            if data[i] < self.monthly_data.iloc[i]['low']:
                self.monthly_data.iloc[i]['low'] = data[i]
            low_monthly = QTableWidgetItem(str(self.monthly_data.iloc[i]['low']))
            low_monthly.setTextAlignment(Qt.AlignCenter)
            low_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            self.monthly_table.setItem(i, 7, low_monthly)


            # 8.设置volume列
            vol_weekly = QTableWidgetItem(str(self.weekly_data.iloc[i]['volume']))
            vol_weekly.setTextAlignment(Qt.AlignCenter)
            vol_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            self.weekly_table.setItem(i, 8, vol_weekly)

            vol_monthly = QTableWidgetItem(str(self.monthly_data.iloc[i]['volume']))
            vol_monthly.setTextAlignment(Qt.AlignCenter)
            vol_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            self.monthly_table.setItem(i, 8, vol_monthly)


            # 9.设施ama列
            ama_weekly = QTableWidgetItem(str(self.weekly_data.iloc[i]['ama']))
            ama_weekly.setTextAlignment(Qt.AlignCenter)
            ama_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            if data[i] >= self.weekly_data.iloc[i]['ama']:
                ama_weekly.setForeground(QColor(0, 255, 0))
            else:
                ama_weekly.setForeground(QColor(255, 0, 0))
            self.weekly_table.setItem(i, 9, ama_weekly)

            ama_monthly = QTableWidgetItem(str(self.monthly_data.iloc[i]['ama']))
            ama_monthly.setTextAlignment(Qt.AlignCenter)
            ama_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            if data[i] >= self.monthly_data.iloc[i]['ama']:
                ama_monthly.setForeground(QColor(0, 255, 0))
            else:
                ama_monthly.setForeground(QColor(255, 0, 0))
            self.monthly_table.setItem(i, 9, ama_monthly)

            # 10.设施ema12列
            ema12_weekly = QTableWidgetItem(str(self.weekly_data.iloc[i]['ema12']))
            ema12_weekly.setTextAlignment(Qt.AlignCenter)
            ema12_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            if data[i] >= self.weekly_data.iloc[i]['ema12']:
                ema12_weekly.setForeground(QColor(0, 255, 0))
            else:
                ema12_weekly.setForeground(QColor(255, 0, 0))
            self.weekly_table.setItem(i, 10, ema12_weekly)

            ema12_monthly = QTableWidgetItem(str(self.monthly_data.iloc[i]['ema12']))
            ema12_monthly.setTextAlignment(Qt.AlignCenter)
            ema12_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            if data[i] >= self.monthly_data.iloc[i]['ema12']:
                ema12_monthly.setForeground(QColor(0, 255, 0))
            else:
                ema12_monthly.setForeground(QColor(255, 0, 0))
            self.monthly_table.setItem(i, 10, ema12_monthly)

            # 11.设施ema20列
            ema20_weekly = QTableWidgetItem(str(self.weekly_data.iloc[i]['ema20']))
            ema20_weekly.setTextAlignment(Qt.AlignCenter)
            ema20_weekly.setFont(QFont('Arial', 12, QFont.Bold))
            if data[i] >= self.weekly_data.iloc[i]['ema20']:
                ema20_weekly.setForeground(QColor(0, 255, 0))
            else:
                ema20_weekly.setForeground(QColor(255, 0, 0))
            self.weekly_table.setItem(i, 11, ema20_weekly)

            ema20_monthly = QTableWidgetItem(str(self.monthly_data.iloc[i]['ema20']))
            ema20_monthly.setTextAlignment(Qt.AlignCenter)
            ema20_monthly.setFont(QFont('Arial', 12, QFont.Bold))
            if data[i] >= self.monthly_data.iloc[i]['ema20']:
                ema20_monthly.setForeground(QColor(0, 255, 0))
            else:
                ema20_monthly.setForeground(QColor(255, 0, 0))
            self.monthly_table.setItem(i, 11, ema20_monthly)
