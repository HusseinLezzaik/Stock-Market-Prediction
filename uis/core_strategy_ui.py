from PyQt5.QtWidgets import QWidget,QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import pandas as pd
import numpy as np


class CoreStrategy(QWidget):
    def __init__(self):
        super(CoreStrategy, self).__init__()
        myfont = QFont('Arial', 12, QFont.Bold)
        self.setFont(myfont)

        # 首先还是读取数据
        # 读取现在有的etfs
        try:
            self.etfs = ['^FCHI']#np.load('./Data/etfs.npy').tolist()
        except FileNotFoundError:
            self.etfs = ['^FCHI']#['SPY', 'QQQ', 'TLT', 'GLD', 'IWM', 'EFA', 'HYG', 'XLV']

        self.supply_demande_zones_rownames = ['SZ Distal', 'SZ Proximal', 'DZ Proximal', 'DZ Distal']
        self.proposed_trade_rownames = ['Trade Type', 'Entry Proximal', 'Entry Distal', 'Exit Proximal', 'Risk', 'Reward', 'Ratio']
        self.odds_enhancers_rownames = ['Freshness(2)', 'Profit Zone(2)', 'Strength(2)', 'Time(1)', 'Curve(1)', 'Trend(2)', 'Total Score', 'Trade Stastus']

        # 读取表格数据，如果其中某个etf的数据不在self.etfs中的，将其删除
        # 在self.etfs中而不在表格中的，需要添加一行
        try:
            self.supply_demande_zones_data = pd.read_csv('./Data/zones.csv', index_col=0)
        except FileNotFoundError:
            self.supply_demande_zones_data = pd.DataFrame(index=self.etfs, columns=self.supply_demande_zones_rownames)

        try:
            self.proposed_trade_data = pd.read_csv('./Data/proposed_trades.csv', index_col=0)
        except FileNotFoundError:
            self.proposed_trade_data = pd.DataFrame(index=self.etfs, columns=self.proposed_trade_rownames)

        try:
            self.odds_enhancers_data = pd.read_csv('./Data/odds_enhancers.csv', index_col=0)
        except FileNotFoundError:
            self.odds_enhancers_data = pd.DataFrame(index=self.etfs, columns=self.odds_enhancers_rownames)

        # 创建主布局
        main_layout = QGridLayout(self)

        # 创建表格1的名称
        supply_demande_zones_label = QLabel('Supply and Demand Zones')
        main_layout.addWidget(supply_demande_zones_label, 0, 0, 1, 1)

        # 创建第一个表格
        self.supply_demande_zones_table = QTableWidget()
        self.supply_demande_zones_table.setRowCount(len(self.supply_demande_zones_rownames))
        self.supply_demande_zones_table.setColumnCount(len(self.etfs))
        # 设置放缩方式
        self.supply_demande_zones_table.horizontalHeader().setMinimumHeight(60)
        self.supply_demande_zones_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.supply_demande_zones_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.supply_demande_zones_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.supply_demande_zones_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        # self.horizontalHeader().setFixedHeight(80)
        # 设置默认行高
        self.supply_demande_zones_table.verticalHeader().setDefaultSectionSize(20)
        self.supply_demande_zones_table.horizontalHeader().setFont(myfont)
        # 设置行和列的名称
        self.supply_demande_zones_table.setHorizontalHeaderLabels(self.etfs)
        self.supply_demande_zones_table.setVerticalHeaderLabels(self.supply_demande_zones_rownames)
        # 禁止编辑
        self.supply_demande_zones_table.setEditTriggers(QAbstractItemView.AllEditTriggers)

        main_layout.addWidget(self.supply_demande_zones_table, 1, 0, 4, 1)

        # 创建表格2的名称
        proposed_trades_label = QLabel('Proposed Trades')
        main_layout.addWidget(proposed_trades_label, 5, 0, 1, 1)

        # 创建第二个表格
        self.proposed_trades_table = QTableWidget()
        self.proposed_trades_table.setRowCount(len(self.proposed_trade_rownames))
        self.proposed_trades_table.setColumnCount(len(self.etfs))
        # 设置放缩方式
        self.proposed_trades_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.proposed_trades_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.proposed_trades_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.proposed_trades_table.horizontalHeader().setFixedHeight(80)
        # 设置默认行高
        self.proposed_trades_table.verticalHeader().setDefaultSectionSize(20)
        self.proposed_trades_table.horizontalHeader().setFont(myfont)
        # 设置行和列的名称
        self.proposed_trades_table.setHorizontalHeaderLabels(self.etfs)
        self.proposed_trades_table.setVerticalHeaderLabels(self.proposed_trade_rownames)
        # 禁止编辑
        self.proposed_trades_table.setEditTriggers(QAbstractItemView.AllEditTriggers)

        main_layout.addWidget(self.proposed_trades_table, 6, 0, 8, 1)

        # 创建表格3的名称
        odds_enhancers_label = QLabel('Odds Enhancers')
        main_layout.addWidget(odds_enhancers_label, 14, 0, 1, 1)

        # 创建第三个表格
        self.odds_enhancers_table = QTableWidget()
        self.odds_enhancers_table.setRowCount(len(self.odds_enhancers_rownames))
        self.odds_enhancers_table.setColumnCount(len(self.etfs))
        # 设置放缩方式
        self.odds_enhancers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.odds_enhancers_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.odds_enhancers_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.odds_enhancers_table.horizontalHeader().setFixedHeight(80)
        # 设置默认行高
        self.odds_enhancers_table.verticalHeader().setDefaultSectionSize(20)
        self.odds_enhancers_table.horizontalHeader().setFont(myfont)
        # 设置行和列的名称
        self.odds_enhancers_table.setHorizontalHeaderLabels(self.etfs)
        self.odds_enhancers_table.setVerticalHeaderLabels(self.odds_enhancers_rownames)
        # 禁止编辑
        self.odds_enhancers_table.setEditTriggers(QAbstractItemView.AllEditTriggers)

        main_layout.addWidget(self.odds_enhancers_table,15, 0, 9, 1)


        # 添加保存按钮
        self.save_btn = QPushButton('Save')
        self.save_btn.clicked.connect(self.save_tables)
        main_layout.addWidget(self.save_btn, 24, 0, 1, 1)

        # 设置页面布局
        self.setLayout(main_layout)

        # 显示数据
        self.show_data()


    def show_data(self):
        # 把已经删除的etf从数据㕜删除
        for etf in self.supply_demande_zones_data.index:
            if etf not in self.etfs:
                self.supply_demande_zones_data.drop(etf, inplace=True)
                self.proposed_trade_data.drop(etf, inplace=True)
                self.odds_enhancers_data.drop(etf, inplace=True)

        # 把新添加的etf加入到数据中
        for etf in self.etfs:
            if etf not in self.supply_demande_zones_data.index:
                self.supply_demande_zones_data.loc[etf] = np.nan
                self.proposed_trade_data.loc[etf] = np.nan
                self.odds_enhancers_data.loc[etf] = np.nan

        for i in range(len(self.etfs)):
            for j in range(len(self.supply_demande_zones_rownames)):
                new_item = QTableWidgetItem(str(self.supply_demande_zones_data.iloc[i, j]))
                new_item.setFont(QFont('arial', 10, QFont.Bold))
                new_item.setTextAlignment(Qt.AlignCenter)
                self.supply_demande_zones_table.setItem(j, i, new_item)

            for j in range(len(self.proposed_trade_rownames)):
                new_item = QTableWidgetItem(str(self.proposed_trade_data.iloc[i, j]))
                new_item.setFont(QFont('arial', 10, QFont.Bold))
                new_item.setTextAlignment(Qt.AlignCenter)
                if j > 0:
                    new_item.setFlags(Qt.ItemIsEnabled)
                self.proposed_trades_table.setItem(j, i, new_item)

            for j in range(len(self.odds_enhancers_rownames) -1):
                new_item = QTableWidgetItem(str(self.odds_enhancers_data.iloc[i, j]))
                new_item.setFont(QFont('arial', 10, QFont.Bold))
                new_item.setTextAlignment(Qt.AlignCenter)
                if j == 1 or j == 6:
                    new_item.setFlags(Qt.ItemIsEnabled)
                self.odds_enhancers_table.setItem(j, i, new_item)
        # 设置第三个表格最后一行
        for i in range(len(self.etfs)):
            try:
                total_score = float(self.odds_enhancers_table.item(6, i).text())
            except Exception as ex:
                continue
            else:
                if total_score >= 9:
                    new_item = QTableWidgetItem('Proximal')
                    new_item.setFont(QFont('arial', 10, QFont.Bold))
                    new_item.setTextAlignment(Qt.AlignCenter)
                    new_item.setBackground(QColor(0, 250, 0))
                    new_item.setForeground(QColor(0, 0, 0))
                    new_item.setFlags(Qt.ItemIsEnabled)
                    self.odds_enhancers_table.setItem(7, i, new_item)
                elif 7 <= total_score < 9:
                    new_item = QTableWidgetItem('Comfirm')
                    new_item.setFont(QFont('arial', 10, QFont.Bold))
                    new_item.setTextAlignment(Qt.AlignCenter)
                    new_item.setBackground(QColor(250, 250, 0))
                    new_item.setForeground(QColor(0, 0, 0))
                    new_item.setFlags(Qt.ItemIsEnabled)
                    self.odds_enhancers_table.setItem(7, i, new_item)
                else:
                    new_item = QTableWidgetItem('No Trade!')
                    new_item.setFont(QFont('arial', 10, QFont.Bold))
                    new_item.setTextAlignment(Qt.AlignCenter)
                    new_item.setBackground(QColor(250, 0, 0))
                    new_item.setFlags(Qt.ItemIsEnabled)
                    self.odds_enhancers_table.setItem(7, i, new_item)

        self.supply_demande_zones_table.itemChanged.connect(self.price_synchronize)
        self.proposed_trades_table.itemChanged.connect(self.side_synchronize)
        self.odds_enhancers_table.itemChanged.connect(self.score_synchronize)


    def price_synchronize(self):
        column = self.supply_demande_zones_table.currentColumn()
        row = self.supply_demande_zones_table.currentRow()
        content = self.supply_demande_zones_table.item(row, column).text()

        if self.proposed_trades_table.item(0, column).text() in ['long', 'Long', 'LONG']:
            print('Long')
            if row == 0:
                return
            if row == 1:
                self.proposed_trades_table.item(3, column).setText(content)
            if row == 2:
                self.proposed_trades_table.item(1, column).setText(content)
            if row == 3:
                self.proposed_trades_table.item(2, column).setText(content)
        elif self.proposed_trades_table.item(0, column).text() in ['short', 'Short', 'SHORT']:
            if row == 0:
                self.proposed_trades_table.item(2, column).setText(content)
            if row == 1:
                self.proposed_trades_table.item(1, column).setText(content)
            if row == 2:
                self.proposed_trades_table.item(3, column).setText(content)
            if row == 3:
                return
        else:
            # 如果还没有决定好是long还是short，不用更新下面第二个表格
            return


    def side_synchronize(self):
        column = self.supply_demande_zones_table.currentColumn()
        side = self.proposed_trades_table.item(0, column).text()

        if side not in ['long', 'Long', 'LONG', 'short', 'Short', 'SHORT']:
            QMessageBox.warning(self, 'Input Error',
                                'Trade type must be long, Long, LONG, or short, Short, SHORT')
            return


        if side == 'Long' or side == 'long':
            self.proposed_trades_table.item(1, column).setText(self.supply_demande_zones_table.item(2, column).text())
            self.proposed_trades_table.item(2, column).setText(self.supply_demande_zones_table.item(3, column).text())
            self.proposed_trades_table.item(3, column).setText(self.supply_demande_zones_table.item(1, column).text())

        if side == 'Short' or side == 'short':
            self.proposed_trades_table.item(1, column).setText(self.supply_demande_zones_table.item(1, column).text())
            self.proposed_trades_table.item(2, column).setText(self.supply_demande_zones_table.item(0, column).text())
            self.proposed_trades_table.item(3, column).setText(self.supply_demande_zones_table.item(2, column).text())

        # 如果三个价格都有了，计算风险和收益
        try:
            entry_proximal = float(self.proposed_trades_table.item(1, column).text())
            entry_distal = float(self.proposed_trades_table.item(2, column).text())
            exit_proximal = float(self.proposed_trades_table.item(3, column).text())
        except Exception as ex:
            return
        else:
            risk = round(abs(entry_distal - entry_proximal), 2)
            reward = round(abs(entry_proximal - exit_proximal), 2)
            ratio = round(reward / risk, 2)

            self.proposed_trades_table.item(4, column).setText(str(risk))
            self.proposed_trades_table.item(5, column).setText(str(reward))
            self.proposed_trades_table.item(6, column).setText(str(ratio))

            # 给profit zone dafen
            if ratio >= 5:
                self.odds_enhancers_table.item(1, column).setText('2')
            elif ratio >= 3:
                self.odds_enhancers_table.item(1, column).setText('1')
            else:
                self.odds_enhancers_table.item(1, column).setText('0')

    def score_synchronize(self):
        column = self.odds_enhancers_table.currentColumn()

        try:
            freness = int(self.odds_enhancers_table.item(0, column).text())
            profit_zone = int(self.odds_enhancers_table.item(1, column).text())
            strength = int(self.odds_enhancers_table.item(2, column).text())
            time = float(self.odds_enhancers_table.item(3, column).text())
            curve = float(self.odds_enhancers_table.item(4, column).text())
            trend = int(self.odds_enhancers_table.item(5, column).text())
        except Exception as ex:
            return
        else:
            total_score = round(freness + profit_zone + strength + time + curve + trend, 1)
            self.odds_enhancers_table.item(6, column).setText(str(total_score))

            if total_score >= 9:
                self.odds_enhancers_table.item(7, column).setText('Proximal')
                self.odds_enhancers_table.item(7, column).setBackground(QColor(0, 250, 0))
            elif 7 <= total_score < 9:
                self.odds_enhancers_table.item(7, column).setText('Comfirm')
                self.odds_enhancers_table.item(7, column).setForeground(QColor(0, 0, 0))
                self.odds_enhancers_table.item(7, column).setBackground(QColor(250, 250, 0))
            else:
                self.odds_enhancers_table.item(7, column).setText('No Trade!')
                self.odds_enhancers_table.item(7, column).setBackground(QColor(250, 0, 0))


    def save_tables(self):

        for i in range(len(self.supply_demande_zones_rownames)):
            for j in range(len(self.etfs)):
                self.supply_demande_zones_data.iloc[j, i] = self.supply_demande_zones_table.item(i, j).text()
                self.supply_demande_zones_data.to_csv('./Data/zones.csv')


        for i in range(len(self.proposed_trade_rownames)):
            for j in range(len(self.etfs)):
                self.proposed_trade_data.iloc[j, i] = self.proposed_trades_table.item(i, j).text()
                self.proposed_trade_data.to_csv('./Data/proposed_trades.csv')

        for i in range(len(self.odds_enhancers_rownames)):
            for j in range(len(self.etfs)):
                self.odds_enhancers_data.iloc[j, i] = self.odds_enhancers_table.item(i, j).text()
                self.odds_enhancers_data.to_csv('./Data/odds_enhancers.csv')

        # 消息框提示保存成功
        QMessageBox.information(self, 'saved', 'Data successfully saved！')