#import numpy as np
import sys
#import os
from uis.login_ui import Login, LoginForm
from uis.home_ui import Home
from uis.etf_management_ui import ETFManagement
from uis.get_hist_data_ui import GetHistData
from uis.candle_ui import Candle
from uis.trading_signal import TradingSignal
from uis.backtest_ui import BackTest
from uis.core_strategy_ui import CoreStrategy
from uis.position_calculator_ui import PositionCalculator
from backend_thread import GetLivePrice, UpdateHistData
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QStackedLayout, QSplitter, QPushButton, QDialog, QApplication, QDesktopWidget
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QCoreApplication
import qdarkstyle


class MainUI(QWidget):
    def __init__(self, parent=None):
        # 创建更新历史数据的线程
        self.hist_data_thread = UpdateHistData()
        self.hist_data_thread.update_hist_data_signal.connect(self.update_hist_data)
        self.hist_data_thread.start()

        # 创建实时价格更新线程
        self.live_price_thread = GetLivePrice()
        self.live_price_thread.update_data.connect(self.update_price)
        # 在历史数据更新完成后再启动


        super(MainUI, self).__init__(parent)
        # 设置窗口名称
        self.setWindowTitle("APIA Quant")
        # initial size
        self.resize(1200, 600)
        # 完成一些复杂的主要的布局
        self.init_ui()
        # 窗口居中显示
        self.center()
        # 设置窗口透明度
        self.setWindowOpacity(0.98)
        self.main_layout.setSpacing(0)
        #设置窗口主题
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())



    def init_ui(self):
        # 创建主部件的网格布局
        self.main_layout = QHBoxLayout(self)

        # 左侧布局开始
        # 创建左侧frame
        self.left_frame = QFrame(self)
        self.left_frame.setFrameShape(QFrame.StyledPanel)

        #在这个frame中使用垂直布局
        self.left_verticalLayout = QVBoxLayout(self.left_frame)

        # function buttons
        self.login_btn = QPushButton(self.left_frame)
        self.login_btn.setText("Login")
        self.login_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setEnabled(False)
        self.login_btn.setShortcut(Qt.Key_Return)

        self.home_btn = QPushButton(self.left_frame)
        self.home_btn.setText('Home')
        self.home_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.home_btn.clicked.connect(lambda: self.display_right(index=1))
        self.home_btn.setEnabled(False)

        self.manage_etf_btn = QPushButton(self.left_frame)
        self.manage_etf_btn.setText('Manage ETFs')
        self.manage_etf_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.manage_etf_btn.clicked.connect(lambda: self.display_right(index=2))
        self.manage_etf_btn.setEnabled(False)

        self.get_hist_btn = QPushButton(self.left_frame)
        self.get_hist_btn.setText('Update Historical Data')
        self.get_hist_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.get_hist_btn.clicked.connect(lambda: self.display_right(index=3))
        self.get_hist_btn.setEnabled(False)

        self.candle_btn = QPushButton(self.left_frame)
        self.candle_btn.setText('Show Candles')
        self.candle_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.candle_btn.clicked.connect(lambda: self.display_right(index=4))
        self.candle_btn.setEnabled(False)

        self.trading_signal_btn = QPushButton(self.left_frame)
        self.trading_signal_btn.setText('Trading Signals')
        self.trading_signal_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.trading_signal_btn.clicked.connect(lambda: self.display_right(index=5))
        self.trading_signal_btn.setEnabled(False)

        self.back_test_btn = QPushButton(self.left_frame)
        self.back_test_btn.setText('Back Test')
        self.back_test_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.back_test_btn.clicked.connect(lambda: self.display_right(index=6))
        self.back_test_btn.setEnabled(False)

        self.core_strategy_btn = QPushButton(self.left_frame)
        self.core_strategy_btn.setText('Core Strategy Table')
        self.core_strategy_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.core_strategy_btn.clicked.connect(lambda: self.display_right(index=7))
        self.core_strategy_btn.setEnabled(False)

        self.position_calculator_btn = QPushButton(self.left_frame)
        self.position_calculator_btn.setText('Position Calculator')
        self.position_calculator_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.position_calculator_btn.clicked.connect(lambda: self.display_right(index=8))
        self.position_calculator_btn.setEnabled(False)

        self.quit_btn = QPushButton(self.left_frame)
        self.quit_btn.setText('Quit')
        self.quit_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.quit_btn.clicked.connect(QCoreApplication.instance().quit)
        self.quit_btn.setEnabled(True)

        # 将上述功能按键添加到当前的垂直布局
        self.left_verticalLayout.addWidget(self.login_btn)
        self.left_verticalLayout.addWidget(self.home_btn)
        self.left_verticalLayout.addWidget(self.manage_etf_btn)
        self.left_verticalLayout.addWidget(self.get_hist_btn)
        self.left_verticalLayout.addWidget(self.candle_btn)
        self.left_verticalLayout.addWidget(self.trading_signal_btn)
        self.left_verticalLayout.addWidget(self.back_test_btn)
        self.left_verticalLayout.addWidget(self.core_strategy_btn)
        self.left_verticalLayout.addWidget(self.position_calculator_btn)
        self.left_verticalLayout.addWidget(self.quit_btn)


        # 右侧布局开始
        # 创建右侧frame
        self.right_frame = QFrame(self)
        self.right_frame.setFrameShape(QFrame.StyledPanel)

        #这里之后会另外进行UI创建的
        self.login_pg = Login()
        self.get_hist_pg = GetHistData()
        # 创建别的页面之前先更新数据
        self.get_hist_pg.get_hist_data()
        self.home_pg = Home()
        self.candle_pg = Candle()
        self.manage_etf_pg = ETFManagement()
        self.trading_signal_pg = TradingSignal()
        self.back_test_pg = BackTest()
        self.core_strategy_pg = CoreStrategy()
        self.position_calculator_pg = PositionCalculator()

        # 在右侧frame创建stack
        self.stack = QStackedLayout(self.right_frame)
        #将上面的页面加入到stack
        self.stack.addWidget(self.login_pg)
        self.stack.addWidget(self.home_pg)
        self.stack.addWidget(self.manage_etf_pg)
        self.stack.addWidget(self.get_hist_pg)
        self.stack.addWidget(self.candle_pg)
        self.stack.addWidget(self.trading_signal_pg)
        self.stack.addWidget(self.back_test_pg)
        self.stack.addWidget(self.core_strategy_pg)
        self.stack.addWidget(self.position_calculator_pg)

        # 用于更新etf列表的信号连接
        self.manage_etf_pg.re_init_signal.connect(self.re_init)

        # 创建splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_frame)
        self.splitter.addWidget(self.right_frame)
        self.splitter.setSizes((200, 800))


        # 将splitter加入到main_layout
        self.main_layout.addWidget(self.splitter)

        self.setLayout(self.main_layout)

        # 窗口最大化
        # self.showMaximized()


    def center(self):
        # 获取桌面尺寸
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口本身的尺寸和位置
        size = self.geometry()
        # 对窗口进行平移
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def display_right(self, index):
        # 在右边frame显示对应的页面
        self.stack.setCurrentIndex(index)

        if index != 2:
            self.get_hist_pg.pgb.setVisible(False)
            self.get_hist_pg.pgb.setValue(0)

    def login(self):
        if LoginForm().exec_() == QDialog.Accepted:
            # 将login按钮设置为不可用
            self.login_btn.setText("Welcome to APIA Quant System")
            self.login_btn.setEnabled(False)
            # 将剩下的按钮全部设为可用，代表登录成功
            self.home_btn.setEnabled(True)
            self.manage_etf_btn.setEnabled(True)
            self.get_hist_btn.setEnabled(True)
            self.candle_btn.setEnabled(True)
            self.trading_signal_btn.setEnabled(True)
            self.back_test_btn.setEnabled(True)
            self.core_strategy_btn.setEnabled(True)
            self.position_calculator_btn.setEnabled(True)
            # 直接跳转至home页面
            self.stack.setCurrentIndex(1)

    def re_init(self):
        # 先终止线程，防止数据对不上
        self.live_price_thread.terminate()
        self.live_price_thread.etfs = ['^FCHI',]#np.load('./Data/etfs.npy').tolist()

        # 重新启动线程
        self.live_price_thread.start()

        self.stack.removeWidget(self.home_pg)
        del self.home_pg
        self.stack.removeWidget(self.manage_etf_pg)
        del self.manage_etf_pg
        self.stack.removeWidget(self.get_hist_pg)
        del self.get_hist_pg
        self.stack.removeWidget(self.candle_pg)
        del self.candle_pg
        self.stack.removeWidget(self.trading_signal_pg)
        del self.trading_signal_pg
        self.stack.removeWidget(self.back_test_pg)
        del self.back_test_pg
        self.stack.removeWidget(self.core_strategy_pg)
        del self.core_strategy_pg
        self.stack.removeWidget(self.position_calculator_pg)
        del self.position_calculator_pg


        # 创建别的页面之前先更新数据
        # self.get_hist_pg.get_hist_data()
        self.home_pg = Home()
        self.manage_etf_pg = ETFManagement()
        self.get_hist_pg = GetHistData()
        self.candle_pg = Candle()
        self.trading_signal_pg = TradingSignal()
        self.back_test_pg = BackTest()
        self.core_strategy_pg = CoreStrategy()
        self.position_calculator_pg = PositionCalculator()

        # 将上面的页面加入到stack
        self.stack.addWidget(self.login_pg)
        self.stack.addWidget(self.home_pg)
        self.stack.addWidget(self.manage_etf_pg)
        self.stack.addWidget(self.get_hist_pg)
        self.stack.addWidget(self.candle_pg)
        self.stack.addWidget(self.trading_signal_pg)
        self.stack.addWidget(self.back_test_pg)
        self.stack.addWidget(self.core_strategy_pg)
        self.stack.addWidget(self.position_calculator_pg)

        self.manage_etf_pg.re_init_signal.connect(window.re_init)

        self.stack.setCurrentIndex(1)

    def update_hist_data(self, sig):
        print(sig)
        self.hist_data_thread.terminate()
        self.live_price_thread.start()
        self.login_btn.setEnabled(True)


    def update_price(self, data):
        self.home_pg.show_live_price(data)
        self.candle_pg.update_price(data)
        self.position_calculator_pg.update_position_table(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainUI()
    app.setWindowIcon(QIcon('./images/apia_logo.png'))
    window.show()
    update_hist = UpdateHistData()
    update_hist.start()
    sys.exit(app.exec_())
