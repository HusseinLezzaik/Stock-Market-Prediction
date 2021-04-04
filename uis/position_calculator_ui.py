from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, \
                            QPushButton, QAbstractItemView, QHeaderView, QMessageBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import pandas as pd
import numpy as  np
import stockstats
pd.set_option('mode.chained_assignment', None)
import yahoo_fin.stock_info as si
from data_processing.load_data import load_rawdata


class PositionCalculator(QWidget):
    def __init__(self):
        super(PositionCalculator, self).__init__()

        # 获取本地的etf名称列表
        try:
            self.etfs = ['^FCHI']#np.load('./Data/etfs.npy').tolist()
        except FileNotFoundError:
            self.etfs = ['^FCHI']#['SPY', 'QQQ', 'TLT', 'GLD', 'IWM', 'EFA', 'HYG', 'XLV']


        # 创建atr列表
        self.atr_list = []


        # get ATR
        self.lines = []
        for i in range(len(self.etfs)):
            raw_data = load_rawdata(self.etfs[i], 'daily')
            if raw_data is None:
                continue
            data_stats = stockstats.StockDataFrame.retype(raw_data.copy())
            atr = round(data_stats['atr'].iloc[-1], 2)
            self.atr_list.append(atr)

            #计算周上面的五条线指标
            raw_data = load_rawdata(self.etfs[i], 'weekly')
            data_stats = stockstats.StockDataFrame.retype(raw_data.copy())
            BB = round(data_stats["close_20_ema"][-1], 2)
            UBB = round(BB + 2 * data_stats["close_20_mstd"][-1], 2)
            plus_half_sd = round(BB + 0.5 * data_stats["close_20_mstd"][-1], 2)
            minus_half_sd = round(BB - 0.5 * data_stats["close_20_mstd"][-1], 2)
            LBB = round(BB - 2 * data_stats["close_20_mstd"][-1], 2)
            self.lines.append([UBB, plus_half_sd, BB, minus_half_sd, LBB])

        # 开始创建页面
        # 设置主要字体
        self.myfont = QFont('Arial', 12, QFont.Bold)
        # 页面的主要布局采用垂直布局
        self.main_layout = QVBoxLayout(self)

        # 创建顶部选择控件
        top_widget  = QWidget()
        # 采用水平布局
        top_layout = QHBoxLayout()

        # 创建控件
        capital_label = QLabel('Capital')
        capital_label.setFont(self.myfont)

        self.capital_lineedit = QLineEdit()
        self.capital_lineedit.setPlaceholderText('ex: 100000')
        self.capital_lineedit.setFont(self.myfont)

        risk_label = QLabel('Risk tolerance')
        risk_label.setFont(self.myfont)

        self.risk_lineedit = QLineEdit()
        self.risk_lineedit.setPlaceholderText('ex: 0.02')
        self.risk_lineedit.setFont(self.myfont)

        stop_coef_label = QLabel('Stop Coefficient')
        stop_coef_label.setFont(self.myfont)

        self.stop_coef_lineedit = QLineEdit()
        self.stop_coef_lineedit.setPlaceholderText('ex: 0.1')
        self.stop_coef_lineedit.setFont(self.myfont)


        self.calculate_btn = QPushButton('Calculate')
        self.calculate_btn.setFont(self.myfont)
        self.calculate_btn.setShortcut(Qt.Key_Return)
        self.calculate_btn.clicked.connect(self.show_position_table)

        # 将这些控件加入top_layout
        top_layout.addWidget(capital_label)
        top_layout.addWidget(self.capital_lineedit)
        top_layout.addWidget(risk_label)
        top_layout.addWidget(self.risk_lineedit)
        top_layout.addWidget(stop_coef_label)
        top_layout.addWidget(self.stop_coef_lineedit)
        top_layout.addWidget(self.calculate_btn)

        # 设置top_widget的layout
        top_widget.setLayout(top_layout)
        top_widget.setContentsMargins(0, 40, 0, 40)

        # 将top_widget加入到总的main_layout
        self.main_layout.addWidget(top_widget)

        # 创建显示position的表格
        self.rows_name = ['Current Price','Risk Exposure','Daily ATR','Trend','Trend Score','Position','Entry Proximal',
                          'Entry Distal','Target','Stop Price','Position Size','Position Value']
        self.position_table = QTableWidget()
        self.position_table.setColumnCount(len(self.etfs))
        self.position_table.setRowCount(len(self.rows_name))
        
        # 设置宽度自由扩展
        self.position_table.horizontalHeader().setMinimumHeight(60)
        self.position_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.position_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.position_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.position_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)

        # 设置表头高度
        self.position_table.horizontalHeader().setMinimumHeight(60)
        self.position_table.horizontalHeader().setFont(self.myfont)
        self.position_table.verticalHeader().setFont(self.myfont)
        # 设置表头内容
        self.position_table.setHorizontalHeaderLabels(self.etfs)
        self.position_table.setVerticalHeaderLabels(self.rows_name)

        # 禁止编辑
        self.position_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
 
        # 隐藏纵向header
        #self.position_table.verticalHeader().setVisible(False)

        # 将表格加入main_layout
        self.main_layout.addWidget(self.position_table)


    def get_cur_price(self):
        # 获取最新价格
        current_price = []
        for etf in self.etfs:
            live_price = si.get_live_price(etf)
            live_price = round(live_price, 2)
            current_price.append(live_price)

        return current_price


    def calculate_position(self, capital, risk_tolerance, stop_coef, data=None):
        # 获取交易信号
        try:
            self.conclusion = np.load('./Data/conclusion.npy').tolist()
        except FileNotFoundError:
            self.conclusion = [0] * len(self.etfs)
            
        if data is None:
            # 此时是由鼠标点击造成的
            current_price = self.get_cur_price()
        else:
            current_price = data

        # 计算风险敞口
        risk_exposure = round(capital * risk_tolerance, 2)

        # 计算stop price, position size, position value
        #stop_prices = []
        #position_sizes = []
        #position_values = []

        table_content = [[]] * len(self.etfs)
        for i in range(len(self.etfs)):
            trend_score = self.conclusion[i]
            if trend_score >= 0:
                trend = 'Up'
                if trend_score < 0.4:
                    position = 'No Trade'
                else:
                    position = 'Long'
                proximal = round(self.lines[i][1],2)
                distal = round(self.lines[i][2],2)
                target = round(self.lines[i][0],2)
                stop =  round(distal - self.atr_list[i] * stop_coef, 2)
                size = int(risk_exposure/self.atr_list[i])
                if size * current_price[i] > capital:
                    size = int(capital/current_price[i])
                value = round(size*current_price[i], 2)

            else:
                trend = 'Down'
                if trend_score > -0.4:
                    position = 'No Trade'
                else:
                    position = 'Short'
                proximal = round(self.lines[i][3],2)
                distal = round(self.lines[i][2],2)
                target = round(self.lines[i][4],2)
                stop =  round(distal + self.atr_list[i] * stop_coef, 2)
                size = int(risk_exposure/self.atr_list[i])
                if size * current_price[i] > capital:
                    size = int(capital/current_price[i])
                value = round(size*current_price[i], 2)

            table_content[i] = [str(current_price[i]),
                                str(risk_exposure),
                                str(self.atr_list[i]),
                                trend,
                                str(trend_score),
                                position,
                                str(proximal),
                                str(distal),
                                str(target),
                                str(stop),
                                str(size),
                                str(value)]


        # 设置表格的值
        for i in range(len(self.etfs)):
            # 确定配色
            if float(table_content[i][4]) >= 0.4:
                # long为绿色
                color = QColor(0, 255, 0)
            elif float(table_content[i][4]) <= -0.4:
                # short为红色
                color = QColor(255, 0, 0)
            else:
                # sideways为黄色
                color = QColor(255, 255, 0)
            for j in range(len(self.rows_name)):
                item = QTableWidgetItem(table_content[i][j])
                item.setTextAlignment(Qt.AlignCenter)
                if j > 2:
                    item.setForeground(color)
                item.setFont(self.myfont)
                self.position_table.setItem(j, i, item)


    def show_position_table(self):
        try:
            capital = float(self.capital_lineedit.text())
            risk_tolerance = float(self.risk_lineedit.text())
            stop_coef = float(self.stop_coef_lineedit.text())
        except Exception as ex:
            # 弹窗，必须输入数字
            QMessageBox.warning(self, 'Input Error',
                                'All inputs should be numerical')
        else:
            if capital <= 0 or risk_tolerance < 0 or risk_tolerance > 1 or stop_coef <= 0:
                QMessageBox.warning(self, 'Input Error',
                                    'Capital and Stop Coefficient must be biger than zero, \n Risk tolerance must be between zero and one')
            else:
                self.calculate_position(capital, risk_tolerance, stop_coef, data=None)


    def update_position_table(self, data):
        if self.capital_lineedit.text() == '' or \
                self.risk_lineedit.text() == '' or \
                self.stop_coef_lineedit.text() == '':
            return
        try:
            capital = float(self.capital_lineedit.text())
            risk_tolerance = float(self.risk_lineedit.text())
            stop_coef = float(self.stop_coef_lineedit.text())
        except Exception as ex:
            return
        else:
            if capital <= 0 or risk_tolerance < 0 or risk_tolerance > 1 or stop_coef <= 0:
                return
            else:
                # 这里就是保证所有输入都是没有问题的
                self.calculate_position(capital, risk_tolerance, stop_coef, data)


