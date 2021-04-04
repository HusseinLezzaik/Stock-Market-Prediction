from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QHeaderView, QAbstractItemView, \
                            QComboBox, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from data_processing.build_model_data import AMADataBuilder, SVMDataBuilder
from data_processing.load_data import load_svm_modeldata, load_ama_modeldata, load_rawdata
from data_processing.svm_preprocessing import preprocess
from uis.calculate_ama import calculate_ama
from sklearn.svm import SVC,classes
from sklearn.neural_network import MLPRegressor
import yahoo_fin.stock_info as si
import numpy as np
import stockstats
import pickle
import os


class TradingSignal(QWidget):
    def __init__(self):
        super(TradingSignal, self).__init__()

        self.setFont(QFont('arial', 12, QFont.Bold))

        # 采用栅格布局
        main_layout = QGridLayout(self)

        # 首先还是读取数据
        # 读取现在有的etfs
        try:
            self.etfs = ['^FCHI',]#np.load('./Data/etfs.npy').tolist()
        except FileNotFoundError:
            self.etfs = ['^FCHI',]#['SPY', 'QQQ', 'TLT', 'GLD', 'IWM', 'EFA', 'HYG', 'XLV']
        self.signals_names = ['Weekly Over EMA12', 'Monthly Over EMA20', 'Weekly Over AMA', 'AMA Direction',
                              'SVM Probability', 'Conclusion']

        # 读取参数
        try:
            self.model_parameters = np.load('./Data/model_parameters.npy', allow_pickle=True).item()
            print(self.model_parameters)
        except FileNotFoundError:
            self.model_parameters = {'SVM': {'hist_window': 4},
                                     'AMA': {'price_type': 'close', 'er_window': 4, 'slow_window': 22,
                                             'fast_window': 4}}

        # 创建数据集需要的参数
        svm_label = QLabel('SVM')
        main_layout.addWidget(svm_label, 0, 0, 2, 1)

        svm_hist_window_label = QLabel('Back Window')
        main_layout.addWidget(svm_hist_window_label, 0, 1, 2, 1)

        self.svm_hist_window_input = QLineEdit()
        self.svm_hist_window_input.setText(str(self.model_parameters['SVM']['hist_window']))
        main_layout.addWidget(self.svm_hist_window_input, 0, 2, 2, 1)

        self.svm_btn = QPushButton('Build Data')
        self.svm_btn.clicked.connect(self.build_svm_data)
        main_layout.addWidget(self.svm_btn, 0, 3, 2, 1)

        svm_label = QLabel('AMA')
        main_layout.addWidget(svm_label, 2, 0, 1, 1)

        price_type_label = QLabel('Price Type')
        main_layout.addWidget(price_type_label, 3, 0, 2, 1)

        self.price_type_input = QComboBox()
        self.price_type_input.addItems(['open', 'close'])
        self.price_type_input.setCurrentText('open')
        main_layout.addWidget(self.price_type_input, 3, 1, 2, 1)

        er_window_label = QLabel('ER Window')
        main_layout.addWidget(er_window_label, 3, 2, 2, 1)

        self.er_window_input = QLineEdit()
        self.er_window_input.setText(str(self.model_parameters['AMA']['er_window']))
        main_layout.addWidget(self.er_window_input, 3, 3, 2, 1)

        fast_window_label = QLabel('Fast Window')
        main_layout.addWidget(fast_window_label, 3, 4, 2, 1)

        self.fast_window_input = QLineEdit()
        self.fast_window_input.setText(str(self.model_parameters['AMA']['fast_window']))
        main_layout.addWidget(self.fast_window_input, 3, 5, 2, 1)

        slow_window_label = QLabel('Slow Window')
        main_layout.addWidget(slow_window_label, 3, 6, 2, 1)

        self.slow_window_input = QLineEdit()
        self.slow_window_input.setText(str(self.model_parameters['AMA']['slow_window']))
        main_layout.addWidget(self.slow_window_input, 3, 7, 2, 1)

        self.ama_btn = QPushButton('Build Data')
        self.ama_btn.clicked.connect(self.build_ama_data)
        main_layout.addWidget(self.ama_btn, 3, 8, 2, 1)

        # 创建表格1的名称
        signals_label = QLabel('Trading Signals Table')
        main_layout.addWidget(signals_label, 5, 0, 2, 2)

        self.update_models_btn = QPushButton('Update Models')
        self.update_models_btn.clicked.connect(self.update_models)
        main_layout.addWidget(self.update_models_btn, 5, 2, 2, 2)

        self.show_signals_btn = QPushButton('Show Signals')
        self.show_signals_btn.clicked.connect(self.calculate_signals)
        main_layout.addWidget(self.show_signals_btn, 5, 4, 2, 2)

        # 创建表格
        self.signals_table = QTableWidget()
        self.signals_table.setRowCount(len(self.signals_names))
        self.signals_table.setColumnCount(len(self.etfs))
        # 设置放缩方式
        self.signals_table.horizontalHeader().setMinimumHeight(60)
        self.signals_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.signals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.signals_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.signals_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        # self.horizontalHeader().setFixedHeight(80)
        # 设置默认行高
        self.signals_table.verticalHeader().setDefaultSectionSize(30)
        self.signals_table.horizontalHeader().setFont(QFont('arial', 12, QFont.Bold))
        # 设置行和列的名称
        self.signals_table.setHorizontalHeaderLabels(self.etfs)
        self.signals_table.setVerticalHeaderLabels(self.signals_names)
        # 禁止编辑
        self.signals_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        main_layout.addWidget(self.signals_table, 7, 0, 12, 9)

        self.setLayout(main_layout)


    def build_ama_data(self):
        price_type = self.price_type_input.currentText()
        er_window = int(self.er_window_input.text())
        slow_window = int(self.slow_window_input.text())
        fast_window = int(self.fast_window_input.text())
        ama_builder = AMADataBuilder(price_type, er_window, slow_window, fast_window)
        for ticker in self.etfs:
            for tf in ['weekly', 'monthly']:
                ama_builder.build_model_data(ticker, tf)

        # 存储参数
        self.model_parameters['AMA']['price_type'] = price_type
        self.model_parameters['AMA']['er_window'] = er_window
        self.model_parameters['AMA']['slow_window'] = slow_window
        self.model_parameters['AMA']['fast_window'] = fast_window
        np.save('./Data/model_parameters.npy', np.array(self.model_parameters))
        QMessageBox.information(self, 'Success', 'AMA model data built successfully!')


    def build_svm_data(self):
        look_hist_window = int(self.svm_hist_window_input.text())
        svm_builder = SVMDataBuilder(look_hist_window=look_hist_window)
        for ticker in self.etfs:
            for tf in ['weekly', 'monthly']:
                svm_builder.build_model_data(ticker, tf)
        self.model_parameters['SVM']['hist_window'] = look_hist_window
        QMessageBox.information(self, 'Success', 'SVM model data built successfully!')

    def update_models(self):
        print('update_models')
        # 检查需要的目录是否已经存在
        if not os.path.exists('./models/'):
            os.makedirs('./models/')
        svm_path = './models/svm_models/'
        if not os.path.exists(svm_path):
            os.makedirs(svm_path)
        ama_path = './models/ama_models/'
        if not os.path.exists(ama_path):
            os.makedirs(ama_path)

        # svm模型的建立
        for ticker in self.etfs:
            print("Ticker ----- ",ticker)
            for tf in ['weekly', 'monthly']:
                # 加载数据
                data = load_svm_modeldata(ticker, tf)
                # 数据预处理，只采用最近的300个数据
                #Elona
                #if len(data) > 300:
                 #   X, Y = preprocess(data.iloc[-301:-2])

                #else:
                X, Y = preprocess(data)
                # 创建分类器
                classifier = SVC(C=100, kernel='rbf', degree=3, gamma='scale', probability=True,
                                 class_weight='balanced')
                # 拟合分类器
                classifier.fit(X, Y)
                # 保存模型
                file_path_name = svm_path + ticker + '_' + tf + '_svm_model'
                file = open(file_path_name, 'wb')
                pickle.dump(classifier, file)
                file.close()

        # # ama模型的建立
        # for ticker in self.etfs:
        #     for tf in ['weekly', 'monthly']:
        #         # 加载数据
        #         data = load_ama_modeldata(ticker, tf)
        #         # 去掉空值
        #         data.dropna(how='any', inplace=True)
        #         data = np.array(data)
        #         # 将最后一列作为目标
        #         X = data[:-1, :-1]
        #         Y = data[:-1, -1]
        #
        #         # 建立多层回归模型， 两个隐藏层，隐藏层节点个数分别为6和4
        #         regressor = MLPRegressor(hidden_layer_sizes=(4, 6, 2), max_iter=3000, learning_rate='adaptive',
        #                                  learning_rate_init=0.02, epsilon=0.0001)
        #         # 拟合模型
        #         regressor.fit(X, Y)
        #         print(regressor.loss_)
        #         print(regressor.loss_curve_)
        #
        #         # 保存模型
        #         file_path_name = ama_path + ticker + '_' + tf + '_ama_model'
        #         file = open(file_path_name, 'wb')
        #         pickle.dump(regressor, file)
        #         file.close()
        QMessageBox.information(self, 'Success', 'Models updated successfully!')

    def calculate_signals(self):
        self.over_ema12 = []
        self.over_ema20 = []
        self.over_ama = []
        self.ama_direction = []
        self.svm_probability = []
        for i in range(len(self.etfs)):
            # 用weekly数据计算ema12
            data = load_rawdata(self.etfs[i], 'weekly')
            data_stats = stockstats.StockDataFrame.retype(data.copy())
            self.over_ema12.append(data_stats['close_12_ema'].iloc[-1])

            # 用weekly数据计算ama
            # # 首先创建ama的模型数据
            # data = load_ama_modeldata(self.etfs[i], 'weekly')
            # input = np.array(data)[-2:, 0:-1]
            #
            # # 添加ama_direction
            # self.ama_direction.append(input[-1, 1])
            #
            # # 加载模型
            # file = open('./models/ama_models/' + self.etfs[i] + '_weekly_ama_model', 'rb')
            # ama_model = pickle.load(file)
            # # 计算ama
            # self.over_ama.append(ama_model.predict(input)[-1])
            # file.close()

            ama, ama_direction, _ = calculate_ama(data, data_stats, self.model_parameters['AMA']['price_type'],
                                      self.model_parameters['AMA']['er_window'],
                                      self.model_parameters['AMA']['slow_window'],
                                      self.model_parameters['AMA']['fast_window'])
            self.over_ama.append(ama[-1])
            self.ama_direction.append(ama_direction[-1])

            # 用weekly数据计算svm
            # 首先创建svm需要的数据
            data = load_svm_modeldata(self.etfs[i], 'weekly')
            if len(data) > 300:
                X, Y = preprocess(data.iloc[-301:-2])
            else:
                X, Y = preprocess(data)
            input = X[-2:]
            # 加载模型
            file = open('./models/svm_models/' + self.etfs[i] + '_weekly_svm_model', 'rb')
            svm_model = pickle.load(file)

            self.svm_probability.append(svm_model.predict_proba(input)[-1, 1])
            file.close()

            # 用月数据计算ema20
            data = load_rawdata(self.etfs[i], 'monthly')
            data_stats = stockstats.StockDataFrame.retype(data.copy())
            self.over_ema20.append(data_stats['close_20_ema'].iloc[-1])

        self.show_signals()

    def show_signals(self, live_price=None):
        if live_price is None:
            live_price = []
            for etf in self.etfs:
                price = si.get_live_price(etf)
                price = round(price, 2)
                live_price.append(price)

        self.conclusion = []

        # 计算conclusion
        # 比例分配， ema12=0.3， ema20=0.1， ama=0.3， ama_direction=0.15, svm_proba=0.5
        for i in range(len(self.etfs)):
            if live_price[i] > self.over_ema12[i]:
                self.over_ema12[i] = 1
            else:
                self.over_ema12[i] = -1

            if live_price[i] > self.over_ema20[i]:
                self.over_ema20[i] = 1
            else:
                self.over_ema20[i] = -1

            if live_price[i] > self.over_ama[i]:
                self.over_ama[i] = 1
            else:
                self.over_ama[i] = -1

            self.svm_probability[i] = self.svm_probability[i] * 2 - 1


            self.ama_direction[i] = round(self.ama_direction[i], 2)
            self.svm_probability[i] = round(self.svm_probability[i], 2)

            self.conclusion.append(round(0.25 * self.over_ema12[i]
                                         + 0.25 * self.over_ama[i]
                                         + 0.2 * (self.ama_direction[i] + self.svm_probability[i])
                                         + 0.1 * self.over_ema20[i], 2))
            print('Over Ema ' , self.over_ema12[i]," Over ama ", self.over_ama[i],"ama dir svm ", (self.ama_direction[i] + self.svm_probability[i]),"over ema 20",self.over_ema20[i], 2)
            # 保存conclusion
            np.save('./Data/conclusion.npy', np.array(self.conclusion))


        # 将这些数据显示到表格中
        for i in range(len(self.etfs)):

            # over ema12
            new_item = QTableWidgetItem()
            if self.over_ema12[i] == 1:
                new_item.setText('Yes')
                new_item.setForeground(QColor(0, 200, 0))
            else:
                new_item.setText('No')
                new_item.setForeground(QColor(200, 0, 0))
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setFont(QFont('arial', 12, QFont.Bold))
            self.signals_table.setItem(0, i, new_item)

            # over ema20
            new_item = QTableWidgetItem()
            if self.over_ema20[i] == 1:
                new_item.setText('Yes')
                new_item.setForeground(QColor(0, 200, 0))
            else:
                new_item.setText('No')
                new_item.setForeground(QColor(200, 0, 0))
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setFont(QFont('arial', 12, QFont.Bold))
            self.signals_table.setItem(1, i, new_item)

            # over ama
            new_item = QTableWidgetItem()
            if self.over_ama[i] == 1:
                new_item.setText('Yes')
                new_item.setForeground(QColor(0, 200, 0))
            else:
                new_item.setText('No')
                new_item.setForeground(QColor(200, 0, 0))
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setFont(QFont('arial', 12, QFont.Bold))
            self.signals_table.setItem(2, i, new_item)

            # ama direction
            new_item = QTableWidgetItem()
            new_item.setText(str(self.ama_direction[i]))
            if self.ama_direction[i] > 0.2:
                new_item.setForeground(QColor(0, 200, 0))
            elif self.ama_direction[i] < -0.2:
                new_item.setForeground(QColor(200, 0, 0))
            else:
                new_item.setForeground(QColor(200, 200, 0))
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setFont(QFont('arial', 12, QFont.Bold))
            self.signals_table.setItem(3, i, new_item)

            # SVM
            new_item = QTableWidgetItem()
            new_item.setText(str(self.svm_probability[i]))
            if self.svm_probability[i] > 0.2:
                new_item.setForeground(QColor(0, 200, 0))
            elif self.svm_probability[i] < -0.2:
                new_item.setForeground(QColor(200, 0, 0))
            else:
                new_item.setForeground(QColor(200, 200, 0))
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setFont(QFont('arial', 12, QFont.Bold))
            self.signals_table.setItem(4, i, new_item)

            # conclusion
            new_item = QTableWidgetItem()
            new_item.setText(str(self.conclusion[i]))
            if self.conclusion[i] > 0.5:
                new_item.setBackground(QColor(0, 200, 0))
                new_item.setForeground(QColor(0, 0, 0))
            elif self.conclusion[i] < -0.5:
                new_item.setBackground(QColor(200, 0, 0))
            else:
                new_item.setBackground(QColor(200, 200, 0))
                new_item.setForeground(QColor(0, 0, 0))
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setFont(QFont('arial', 12, QFont.Bold))
            self.signals_table.setItem(5, i, new_item)
