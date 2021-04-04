from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,\
                            QHeaderView, QAbstractItemView, QMessageBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from backtest.ama_backtest import AMABackTest
from backtest.svm_backtest import SVMBackTest
import numpy as np
import pandas as pd
import datetime
import re
import os


class BackTest(QWidget):
    def __init__(self):
        super(BackTest, self).__init__()

        # 采用栅格布局
        main_layout = QGridLayout(self)
        self.setFont(QFont('arial', 11, QFont.Bold))

        # 首先还是读取数据
        # 读取现在有的etfs
        try:
            self.etfs = ['^FCHI',]#Haifei: np.load('./Data/etfs.npy').tolist()
        except FileNotFoundError:
            self.etfs = ['^FCHI',]#['SPY', 'QQQ', 'TLT', 'GLD', 'IWM', 'EFA', 'HYG', 'XLV']
        self.row_names = ['Start date', 'End date', 'Initial deposit', 'Total trades', 'Profit trades', 'Loss trades', 'Maximal drawdown',
                          'Sharpe ratio', 'Total net profit', 'Total return', 'CAGR']

        # 选择需要回测的模型
        model_label = QLabel('Model')
        main_layout.addWidget(model_label, 0, 0, 1, 1)

        self.model_choice = QComboBox()
        self.model_choice.addItems(['AMA', 'SVM'])
        # 根据选中的模型决定是否显示AMA的参数选择
        self.model_choice.currentIndexChanged.connect(self.hide_ama_parameters)
        main_layout.addWidget(self.model_choice, 0, 1, 1, 1)

        # 选择需要回测的世间跨度
        period_label = QLabel('Period')
        main_layout.addWidget(period_label, 0, 2, 1, 1)

        self.period_choice = QComboBox()
        self.period_choice.addItems(['Year To Date', '1 Year', '3 Years', '5 Years', '10 Years'])
        main_layout.addWidget(self.period_choice, 0, 3, 1, 1)

        # 输入回测的初始资金
        deposit_label = QLabel('Initial Deposit')
        main_layout.addWidget(deposit_label, 0, 4, 1, 1)

        self.deposit_input = QLineEdit()
        self.deposit_input.setText('100000')
        main_layout.addWidget(self.deposit_input, 0, 5, 1, 1)



        # AMA的回测参数
        self.price_type_label = QLabel('Price Type')
        main_layout.addWidget(self.price_type_label, 1, 0, 1, 1)

        self.price_type_input = QComboBox()
        self.price_type_input.addItems(['open', 'close'])
        self.price_type_input.setCurrentText('close')
        main_layout.addWidget(self.price_type_input, 1, 1, 1, 1)

        self.er_window_label = QLabel('ER Window')
        main_layout.addWidget(self.er_window_label, 1, 2, 1, 1)

        self.er_window_input = QLineEdit()
        self.er_window_input.setText('4')
        main_layout.addWidget(self.er_window_input, 1, 3, 1, 1)

        self.fast_window_label = QLabel('Fast Window')
        main_layout.addWidget(self.fast_window_label, 1, 4, 1, 1)

        self.fast_window_input = QLineEdit()
        self.fast_window_input.setText('4')
        main_layout.addWidget(self.fast_window_input, 1, 5, 1, 1)

        self.slow_window_label = QLabel('Slow Window')
        main_layout.addWidget(self.slow_window_label, 1, 6, 1, 1)

        self.slow_window_input = QLineEdit()
        self.slow_window_input.setText('22')
        main_layout.addWidget(self.slow_window_input, 1, 7, 1, 1)


        # 回测开始按钮
        backtest_btn = QPushButton('Do Backtest')
        backtest_btn.clicked.connect(self.do_backtest)
        main_layout.addWidget(backtest_btn, 2, 0, 1, 8)

        # 历史回测纪录下拉框
        hist_reports_label = QLabel('Historical Backtests')
        main_layout.addWidget(hist_reports_label, 3, 0, 2, 1)

        self.hist_reports_choice = QComboBox()
        backtest_done_list = os.listdir('./backtest/reports')
        backtest_done_list.insert(0, 'Choose one report')
        self.hist_reports_choice.addItems(backtest_done_list)
        self.hist_reports_choice.currentTextChanged.connect(self.show_hist_report)
        main_layout.addWidget(self.hist_reports_choice, 3, 1, 2, 2)

        # 删除历史回测的按钮
        delete_backtest_btn = QPushButton('Delete Current Backtest')
        delete_backtest_btn.clicked.connect(self.delete_backtest)
        main_layout.addWidget(delete_backtest_btn, 3, 3, 2, 2)


        # 初始化显示报告的表格
        # 创建表格
        self.backtest_table = QTableWidget()
        self.backtest_table.setRowCount(len(self.row_names))
        self.backtest_table.setColumnCount(len(self.etfs))
        # 设置放缩方式
        self.backtest_table.horizontalHeader().setMinimumHeight(60)
        self.backtest_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.backtest_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.backtest_table.horizontalHeader().setFont(QFont('arial', 11, QFont.Bold))
        self.backtest_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.backtest_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.backtest_table.verticalHeader().setFont(QFont('arial', 11, QFont.Bold))
        # self.horizontalHeader().setFixedHeight(80)
        # 设置默认行高
        self.backtest_table.verticalHeader().setDefaultSectionSize(30)
        # 设置行和列的名称
        self.backtest_table.setHorizontalHeaderLabels(self.etfs)
        self.backtest_table.setVerticalHeaderLabels(self.row_names)
        # 禁止编辑
        self.backtest_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        main_layout.addWidget(self.backtest_table, 5, 0, 5, 8)

        self.setLayout(main_layout)



    def hide_ama_parameters(self, index):
        if index == 1:
            self.price_type_label.setVisible(False)
            self.price_type_input.setVisible(False)
            self.er_window_label.setVisible(False)
            self.er_window_input.setVisible(False)
            self.fast_window_label.setVisible(False)
            self.fast_window_input.setVisible(False)
            self.slow_window_label.setVisible(False)
            self.slow_window_input.setVisible(False)
        if index == 0:
            self.price_type_label.setVisible(True)
            self.price_type_input.setVisible(True)
            self.er_window_label.setVisible(True)
            self.er_window_input.setVisible(True)
            self.fast_window_label.setVisible(True)
            self.fast_window_input.setVisible(True)
            self.slow_window_label.setVisible(True)
            self.slow_window_input.setVisible(True)


    def show_hist_report(self):
        if self.hist_reports_choice.currentText() != 'Choose one report':
            file_name = self.hist_reports_choice.currentText()
            report = pd.read_csv('./backtest/reports/' + file_name, index_col=0)
            parameters = re.split(r'[. _]', file_name)
            if parameters[0] == 'AMA':
                self.model_choice.setCurrentText('AMA')
                if parameters[1] == 'YTD':
                    self.period_choice.setCurrentText('Year To Date')
                elif parameters[1] == '1year':
                    self.period_choice.setCurrentText('1 Year')
                elif parameters[1] == '3years':
                    self.period_choice.setCurrentText('3 Years')
                elif parameters[1] == '5years':
                    self.period_choice.setCurrentText('5 Years')
                else:
                    self.period_choice.setCurrentText('10 Years')
                self.price_type_input.setCurrentText(parameters[2])
                self.er_window_input.setText(parameters[3])
                self.fast_window_input.setText(parameters[4])
                self.slow_window_input.setText(parameters[5])
            else:
                self.model_choice.setCurrentText('SVM')
                if parameters[1] == 'YTD':
                    self.period_choice.setCurrentText('Year To Date')
                elif parameters[1] == '1year':
                    self.period_choice.setCurrentText('1 Year')
                elif parameters[1] == '3years':
                    self.period_choice.setCurrentText('3 Years')
                elif parameters[1] == '5years':
                    self.period_choice.setCurrentText('5 Years')
                else:
                    self.period_choice.setCurrentText('10 Years')

            # 这里需要重新设置表格的列，防止很久之前做的test中的ETF和现在的不一致
            etfs = list(report['ETF'])
            print("Report ", report['ETF'])
            self.backtest_table.setColumnCount(len(etfs))
            self.backtest_table.setHorizontalHeaderLabels(etfs)

            # 更新表格
            for i in range(len(etfs)):
                for j in range(len(self.row_names)):
                    content = str(report.iloc[i, j+1])
                    if j in [4, 5, 6, 9, 10]:
                        content = content + '%'
                    new_item = QTableWidgetItem(content)
                    new_item.setFont(QFont('arial', 11, QFont.Bold))
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.backtest_table.setItem(j, i, new_item)
        else:
            self.backtest_table.clearContents()
            self.model_choice.setCurrentText('AMA')


    def delete_backtest(self, index):
        if self.hist_reports_choice.currentText() != 'Choose one report':
            file_name = self.hist_reports_choice.currentText()
            os.remove('./backtest/reports/'+file_name)
            QMessageBox.information(self, 'Delete', 'Backtest ' + file_name + 'has been deleted successfully！')
            self.backtest_table.clearContents()
            self.hist_reports_choice.removeItem(self.hist_reports_choice.currentIndex())
            self.model_choice.setCurrentText('AMA')
            self.hist_reports_choice.setCurrentText('Choose one report')




    def do_backtest(self):
        #创建回测报告的dataframe
        backtest_report = pd.DataFrame(columns=['ETF', 'Start date', 'End date', 'Initial deposit', 'Total trades', 'Profit trades',
                                               'Loss trades', 'Maximal drawdown', 'Sharpe ratio', 'Total net profit', 'Total return', 'CAGR'])
        # 处理好开始和阶数日期
        # 阶数日期都是当天
        end_date = str(datetime.date.today())
        if self.period_choice.currentText() == 'Year To Date':
            period = 'YTD'
            start_date = str(datetime.date.today().year) + '-01-01'
        else:
            if self.period_choice.currentText() == '1 Year':
                period = '1year'
                year = datetime.date.today().year - 1
            if self.period_choice.currentText() == '3 Years':
                period = '3years'
                year = datetime.date.today().year - 3
            if self.period_choice.currentText() == '5 Years':
                period = '5years'
                year = datetime.date.today().year - 5
            if self.period_choice.currentText() == '10 Years':
                period = '10years'
                year = datetime.date.today().year - 10
            start_date = str(datetime.date(year, datetime.date.today().month, datetime.date.today().day))

        # 获取初始资本
        deposit = int(self.deposit_input.text())

        if self.model_choice.currentText() == 'AMA':

            # 准备好参数
            price_type = self.price_type_input.currentText()
            er_window = int(self.er_window_input.text())
            fast_window = int(self.fast_window_input.text())
            slow_window = int(self.slow_window_input.text())

            # 对所有的etf依次做回测
            for i in range(len(self.etfs)):
                ama_backtest = AMABackTest(self.etfs[i], start_date, end_date, 'AMA', deposit, price_type, er_window, slow_window, fast_window)
                # 接收到的测试结果是一个字典
                test_result = ama_backtest.run_test()
                backtest_report = backtest_report.append(test_result, ignore_index=True)

                # 更新表格
                for j in range(len(self.row_names)):
                    content = str(test_result[self.row_names[j]])
                    if j in [4, 5, 6, 9, 10]:
                        content = content + '%'
                    new_item = QTableWidgetItem(content)
                    new_item.setFont(QFont('arial', 11, QFont.Bold))
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.backtest_table.setItem(j, i, new_item)
            file_name = "AMA_{}_{}_{}_{}_{}".format(period, price_type, er_window, fast_window, slow_window)
        else:
            # 关于SVM的回测
            for i in range(len(self.etfs)):
                svm_backtest = SVMBackTest(self.etfs[i], start_date, end_date, 'AMA', deposit)
                # 接收到的测试结果是一个字典
                test_result = svm_backtest.run_test()

                backtest_report = backtest_report.append(test_result, ignore_index=True)

                # 更新表格
                for j in range(len(self.row_names)):
                    content = str(test_result[self.row_names[j]])
                    if j in [4, 5, 6, 9, 10]:
                        content = content + '%'
                    new_item = QTableWidgetItem(content)
                    new_item.setFont(QFont('arial', 11, QFont.Bold))
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.backtest_table.setItem(j, i, new_item)
            file_name = "SVM_{}".format(period)

        backtest_report.to_csv('./backtest/reports/'+file_name+'.csv')

        # 将这个回测添加到历史回测列表中
        exist = False
        for i in range(self.hist_reports_choice.count()):
            if file_name+'.csv' == self.hist_reports_choice.itemText(i):
                exist = True
                break
        if exist == False:
            self.hist_reports_choice.addItem(file_name+'.csv')
        self.hist_reports_choice.setCurrentText(file_name+'.csv')