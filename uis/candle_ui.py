from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QLineEdit, QComboBox,\
                            QListWidget, QListWidgetItem, QPushButton
from PyQt5.QtGui import QFont, QPicture, QPainter
from PyQt5.QtCore import Qt, QPointF, QRectF
import numpy as np
import pyqtgraph as pg
import stockstats
from uis.calculate_ama import calculate_ama
from data_processing.load_data import load_rawdata, load_ama_modeldata

class Candle(QWidget):
    def __init__(self):
        super(Candle, self).__init__()

        # 创建字体格式
        self.myfont = QFont('Arial', 12, QFont.Bold)
        self.setFont(self.myfont)

        # 创建页面布局，采用栅格
        layout = QGridLayout(self)

        # 先读取etf名称列表
        try:
            self.etfs = ['^FCHI']#np.load('./Data/etfs.npy').tolist()
        except FileNotFoundError:
            self.etfs = ['^FCHI']#['SPY', 'QQQ', 'TLT', 'GLD', 'IWM', 'EFA', 'HYG', 'XLV']
        # 创建etf名称下拉框
        self.etf_label = QLabel('Index')
        self.etf_label.setAlignment(Qt.AlignCenter)
        self.chosen_etf = QLineEdit()
        self.chosen_etf.setReadOnly(True)
        self.etfs_options = QComboBox()
        self.etfs_options.addItems(self.etfs)
        self.etfs_options.currentIndexChanged.connect(self.show_chosen_etf)
        self.etfs_options.setLineEdit(self.chosen_etf)

        # 创建time frame下拉列表
        self.tfs = ['weekly', 'monthly']
        # 创建etf名称下拉框
        self.tf_label = QLabel('Time frame')
        self.tf_label.setAlignment(Qt.AlignCenter)
        self.chosen_tf = QLineEdit()
        self.chosen_tf.setReadOnly(True)
        self.tfs_options = QComboBox()
        self.tfs_options.addItems(self.tfs)
        self.tfs_options.currentIndexChanged.connect(self.show_chosen_tf)
        self.tfs_options.setLineEdit(self.chosen_tf)

        # 创建指标的下拉复选框
        self.indicators = ['ama', 'ema12', 'ema20']
        self.indicators_label = QLabel('Index')
        self.indicators_label.setAlignment(Qt.AlignCenter)
        self.chosen_indicator = QLineEdit()
        self.chosen_indicator.setFont(QFont('Arial', 9, QFont.Bold))
        self.chosen_indicator.setReadOnly(True)
        self.indicators_checkbox = []
        self.indicators_options = QComboBox()
        self.indicators_listwidget = QListWidget()
        for i in range(len(self.indicators)):
            self.indicators_checkbox.append(QCheckBox(self.indicators[i]))
            self.indicators_checkbox[i].setFont(QFont('Arial', 9, QFont.Bold))
            self.indicators_checkbox[i].setContentsMargins(0, 0, 0, 5)
            qItem = QListWidgetItem(self.indicators_listwidget)
            self.indicators_checkbox[i].stateChanged.connect(self.show_chosen_indicators)
            self.indicators_listwidget.setItemWidget(qItem, self.indicators_checkbox[i])
        self.indicators_options.setModel(self.indicators_listwidget.model())
        self.indicators_options.setView(self.indicators_listwidget)
        self.indicators_options.setLineEdit(self.chosen_indicator)

        # 创建开始按钮
        self.show_candle_btn = QPushButton('Show')
        self.show_candle_btn.clicked.connect(self.k_plot)

        # 将这些空间加入栅格的第一行
        layout.addWidget(self.etf_label, 0, 0)
        layout.addWidget(self.etfs_options, 0, 1)
        layout.addWidget(self.tf_label, 0, 2)
        layout.addWidget(self.tfs_options, 0, 3)
        layout.addWidget(self.indicators_label, 0, 4)
        layout.addWidget(self.indicators_options, 0, 5)
        layout.addWidget(self.show_candle_btn, 0, 6, 1, 2)

        # 添加实时价格显示行
        self.current_label = QLabel('Current:  ' +'--')
        self.current_label.setAlignment(Qt.AlignCenter)
        self.open_label = QLabel('Open: ' + '--')
        self.open_label.setAlignment(Qt.AlignCenter)
        self.high_label = QLabel('High:  ' + '--')
        self.high_label.setAlignment(Qt.AlignCenter)
        self.low_label = QLabel('Low:  ' + '--')
        self.low_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.current_label, 1, 0)
        layout.addWidget(self.open_label, 1, 1)
        layout.addWidget(self.high_label, 1, 2)
        layout.addWidget(self.low_label, 1, 3)

        # 创建用于图例的labels
        self.ama_label = QLabel('ama')
        self.ama_label.setStyleSheet('color: white')
        self.ama_label.setFont(self.myfont)
        self.ama_label.setAlignment(Qt.AlignCenter)
        self.ama_label.setVisible(False)
        self.ema12_label = QLabel('ema12')
        self.ema12_label.setStyleSheet('color: darkCyan')
        self.ema12_label.setFont(self.myfont)
        self.ema12_label.setAlignment(Qt.AlignCenter)
        self.ema12_label.setVisible(False)
        self.ema20_label = QLabel('ema20')
        self.ema20_label.setStyleSheet('color: darkMagenta')
        self.ema20_label.setFont(self.myfont)
        self.ema20_label.setAlignment(Qt.AlignCenter)
        self.ema20_label.setVisible(False)

        layout.addWidget(self.ama_label, 1, 5)
        layout.addWidget(self.ema12_label, 1, 6)
        layout.addWidget(self.ema20_label, 1, 7)

        # 创建k线图画布
        self.k_plt = pg.PlotWidget()
        self.k_plt.setContentsMargins(0, 20, 0, 0)

        # 连接鼠标活动
        self.move_slot = pg.SignalProxy(self.k_plt.scene().sigMouseMoved, rateLimit=60, slot=self.print_slot)
        # 将k线图实例加入布局
        layout.addWidget(self.k_plt, 2, 0, 8, 8)

        self.setLayout(layout)

    # 由于在行中显示被选中的etf
    def show_chosen_etf(self, index):
        self.chosen_etf.setReadOnly(False)
        self.chosen_etf.setText(self.etfs_options.itemText(index))
        self.chosen_etf.setReadOnly(True)

    # 由于在行中显示被选中的time frame
    def show_chosen_tf(self, index):
        self.chosen_tf.setReadOnly(False)
        self.chosen_tf.setText(self.tfs_options.itemText(index))
        self.chosen_tf.setReadOnly(True)

    # 由于在行中显示被选中的指标
    def show_chosen_indicators(self):
        self.chosen_indicator.setReadOnly(False)
        show_content = ''
        for i in range(len(self.indicators)):
            if self.indicators_checkbox[i].isChecked():
                show_content += self.indicators[i] + ';'

        self.chosen_indicator.setText(show_content)
        self.chosen_indicator.setReadOnly(True)

    def update_price(self, live_price):
        # 如果还没有进行k线的显示，直接跳过
        if self.open_label.text() == 'Open: --':
            return
        # 这里live_price是一个数组，我们首先需要根据etf的名称来获得他的最新价格
        index = self.etfs.index(self.chosen_etf.text())
        self.current_price = round(live_price[index], 2)
        if  self.current_price > self.high_price:
            self.high_price =  self.current_price
        if  self.current_price < self.low_price:
            self.low_price =  self.current_price

        # 更新页面上显示的价格， open不需要改变
        self.current_label.setText('Current: ' + str( self.current_price))
        if  self.current_price > self.open_price:
            self.current_label.setStyleSheet("color:green")
            self.current_label.setFont(self.myfont)
        else:
            self.current_label.setStyleSheet("color:red")
            self.current_label.setFont(self.myfont)

        self.high_label.setText('High: ' + str(self.high_price))
        self.low_label.setText('Low: ' + str(self.low_price))

        # 更新self.data的最后一列
        self.data.iloc[-1][['open', 'high', 'low', 'close']] = [self.open_price, self.high_price, self.low_price, self.current_price]




    def prepare_data(self):
        # 获取被选中的etf名称和time frame
        etf = self.chosen_etf.text()
        tf = self.chosen_tf.text()
        indicators = self.chosen_indicator.text().split(';')
        _ = indicators.pop()
        # load data
        self.data = load_rawdata(etf, tf)
        self.data_stats = stockstats.StockDataFrame.retype(self.data.copy())
        # 去掉volume和adj close列
        self.data.drop(['adjclose', 'volume'], axis=1, inplace=True)

        # 添加所指标ama, ema12, ema20

        ama, _, _ = calculate_ama(self.data, self.data_stats)

        self.data['ama'] = ama

        self.data[['ema12', 'ema20']] = self.data_stats[['close_12_ema', 'close_20_ema']]

        # 数值保留两位小数
        self.data[['open', 'high', 'low', 'close', 'ama', 'ema12', 'ema20']] = self.data[['open', 'high', 'low', 'close', 'ama', 'ema12', 'ema20']].round(decimals=2)


        # 设置价格显示面板
        # 获取四个价
        self.current_price = self.data.iloc[-1]['close']
        self.open_price = self.data.iloc[-1]['open']
        self.high_price = self.data.iloc[-1]['high']
        self.low_price = self.data.iloc[-1]['low']

        self.current_label.setText('Current: ' + str(self.current_price))
        if self.current_price > self.open_price:
            self.current_label.setStyleSheet("color:green")
            self.current_label.setFont(self.myfont)
        else:
            self.current_label.setStyleSheet("color:red")
            self.current_label.setFont(self.myfont)

        self.open_label.setText('Open: ' + str(self.open_price))
        self.high_label.setText('High: ' + str(self.high_price))
        self.low_label.setText('Low: ' + str(self.low_price))


    def k_plot(self):
        # 显示图例
        self.ama_label.setVisible(True)
        self.ema12_label.setVisible(True)
        self.ema20_label.setVisible(True)

        self.prepare_data()
        # 获取被选中的技术指标
        indicator_state = []
        for i in range(len(self.indicators_checkbox)):
            indicator_state.append(self.indicators_checkbox[i].isChecked())

        # 获取价格的最大最小值, 使用最近的100个
        y_min = self.data.iloc[-100:-1]['low'].min() * 0.9
        y_max = self.data.iloc[-100:-1]['high'].max() * 1.1
        date_time = np.arange(len(self.data))
        ohlc_ma_price = self.data[['open', 'high', 'low', 'close', 'ama', 'ema12', 'ema20']].to_numpy()
        data_list = np.insert(ohlc_ma_price, 0, values=date_time, axis=1)

        self.axis_dict = dict(enumerate(self.data.index))

        # 创建刻度
        self.axis_dict = dict(enumerate(self.data.index))

        # 获取日期值
        axis_1 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 3)]
        axis_2 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 5)]
        axis_3 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 8)]
        axis_4 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 10)]
        axis_5 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 30)]
        stringaxis = pg.AxisItem(orientation='bottom')  # 创建一个刻度项
        # 设置X轴刻度值
        stringaxis.setTicks([axis_5, axis_4, axis_3, axis_2, axis_1, self.axis_dict.items()])
        self.k_plt.getAxis("bottom").setTicks([axis_5, axis_4, axis_3, axis_2, axis_1, self.axis_dict.items()])

        self.k_plt.plotItem.clear()  # 清空绘图部件中的项
        self.candles = CandlestickItem(data_list, indicator_state)  # 生成蜡烛图数据
        self.k_plt.addItem(self.candles, )  # 在绘图部件中添加蜡烛图项目
        self.k_plt.showGrid(x=True, y=True)  # 设置绘图部件显示网格线
        self.k_plt.setYRange(y_min, y_max)
        self.k_plt.setXRange(len(data_list)-70, len(data_list)+30)
        self.k_plt.setLabel(axis='left', text='price')  # 设置Y轴标签
        self.k_plt.setLabel(axis='bottom', text='date')  # 设置X轴标签
        self.label = pg.TextItem()  # 创建一个文本项
        self.k_plt.addItem(self.label)  # 在图形部件中添加文本项


    # 响应鼠标移动绘制十字光标
    def print_slot(self, event=None):
        if event is None:
            pass
        else:
            pos = event[0]  # 获取事件的鼠标位置
            try:
                # 如果鼠标位置在绘图部件中
                if self.k_plt.sceneBoundingRect().contains(pos):
                    mousePoint = self.k_plt.plotItem.vb.mapSceneToView(pos)  # 转换鼠标坐标
                    index = int(mousePoint.x())  # 鼠标所处的X轴坐标
                    pos_y = int(mousePoint.y())  # 鼠标所处的Y轴坐标
                    if -1 < index < len(self.data.index):
                        # 在label中写入HTML
                        self.label.setHtml(
                            "<p style='color:white'><strong>date：{0}</strong> \
                            </p><p style='color:white'>open：{1} \
                            </p><p style='color:white'>close：{2} \
                            </p><p style='color:white'>high：{3} \
                            </p><p style='color:white'>low：{4}</p>".format(
                                self.axis_dict[index], self.data['open'][index], self.data['close'][index],
                                self.data['high'][index], self.data['low'][index]))
                        self.label.setPos(mousePoint.x(), mousePoint.y())  # 设置label的位置
                    # 设置垂直线条和水平线条的位置组成十字光标
                    self.vLine.setPos(mousePoint.x())
                    self.hLine.setPos(mousePoint.y())
            except Exception as e:
                pass




# K线图绘制类
class CandlestickItem(pg.GraphicsObject):
    # 州的先生zmister.com
    def __init__(self, data, indicators_state):
        pg.GraphicsObject.__init__(self)
        # data里面必须有以下字段: 时间, 开盘价, 收盘价, 最低价, 最高价
        self.data = data
        self.indicators_state = indicators_state
        self.generatePicture()

    def generatePicture(self):
        # 实例化一个绘图设备
        self.picture = QPicture()

        # 在picture上实例化QPainter用于绘图
        self.p = QPainter(self.picture)

        # 设置画笔颜色

        self.w = (self.data[1][0] - self.data[0][0]) / 3

        pre_ama = 0
        pre_ema12 = 0
        pre_ema20 = 0

        for (t, open, high, low, close, ama, ema12, ema20) in self.data:
            # 绘制线条
            self.p.setPen(pg.mkPen('w'))
            self.p.drawLine(QPointF(t, low), QPointF(t, high))
            # 开盘价大于收盘价
            if close >= open:
                # 设置画刷颜色为绿
                self.p.setPen(pg.mkPen('g'))
                self.p.setBrush(pg.mkBrush('g'))
            else:
                # 设置画刷颜色为红
                self.p.setPen(pg.mkPen('r'))
                self.p.setBrush(pg.mkBrush('r'))
            # 绘制箱子
            self.p.drawRect(QRectF(t - self.w, open, self.w * 2, close - open))

            # 根据是否被选中画均线
            if pre_ama != 0:
                if self.indicators_state[0]:
                    self.p.setPen(pg.mkPen('w'))
                    self.p.setBrush(pg.mkBrush('w'))
                    self.p.drawLine(QPointF(t - 1, pre_ama), QPointF(t, ama))
            pre_ama = ama

            if pre_ema12 != 0:
                if self.indicators_state[1]:
                    self.p.setPen(pg.mkPen('c'))
                    self.p.setBrush(pg.mkBrush('c'))
                    self.p.drawLine(QPointF(t - 1, pre_ema12), QPointF(t, ema12))
            pre_ema12 = ema12

            if pre_ema20 != 0:
                if self.indicators_state[2]:
                    self.p.setPen(pg.mkPen('m'))
                    self.p.setBrush(pg.mkBrush('m'))
                    self.p.drawLine(QPointF(t - 1, pre_ema20), QPointF(t, ema20))
            pre_ema20 = ema20

        self.p.end()
        self.last_t = t

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())
