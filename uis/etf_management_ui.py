import numpy as np
import os
import re
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from data_processing.download_data import download_data


class ETFManagement(QWidget):
    re_init_signal = pyqtSignal(str)
    def __init__(self):
        super(ETFManagement, self).__init__()

        # 确认etfs.npy文件是否存在，如果不存在，则初始化
        try:
            self.etfs = ['^FCHI']#np.load('./Data/etfs.npy').tolist()
        except FileNotFoundError:
            self.etfs = ['^FCHI']#['SPY', 'QQQ', 'TLT', 'GLD', 'IWM', 'EFA', 'HYG', 'XLV']
            np.save('./Data/etfs.npy', np.array(self.etfs))

        # 至此，我们已经正确创建了etfs列表, 开始创建列表
        main_layout = QGridLayout(self)
        self.setFont(QFont('Arial', 12, QFont.Bold))


        # 创建关于add的控件
        add_label = QLabel('Add new ETF')

        self.add_lineedit = QLineEdit()
        self.add_lineedit.setPlaceholderText('SPY; QQQ')

        add_btn = QPushButton('Add')
        add_btn.setShortcut(Qt.Key_Return)
        add_btn.clicked.connect(self.add_new_etf)

        # 将这几个控件加入布局
        main_layout.addWidget(add_label, 0, 0, 1, 1)
        main_layout.addWidget(self.add_lineedit, 0, 1, 1, 2)
        main_layout.addWidget(add_btn,0, 3, 1, 2 )

         # 创建关于remove的控件
        remove_label = QLabel('Remove ETF')
        main_layout.addWidget(remove_label, 1, 0, 1, 1)

        # 建立一个list分别用来存储对于etf的选择
        self.etfs_check_box = []

        for i in range(len(self.etfs)):
            self.etfs_check_box.append(QCheckBox(self.etfs[i]))
            row = i // 4 + 1
            column = i % 4 + 1
            main_layout.addWidget(self.etfs_check_box[i], row, column)

        remove_btn = QPushButton('Remove')
        remove_btn.clicked.connect(self.remove_etf)

        main_layout.addWidget(remove_btn, len(self.etfs) // 4 + 2, 1, 1, 4)

        self.setLayout(main_layout)


    def add_new_etf(self):
        input = self.add_lineedit.text()
        # 去除所有空格
        input = ''.join(input.split())
        # 转化为大写
        input = input.upper()
        # 按分号或者逗号分隔
        input = re.split(',|;|-|_', input)

        # 判断是否有新的ETF加入
        have_new = False

        for new_etf in input:
            if new_etf not in self.etfs:
                self.etfs.append(new_etf)
                have_new = True
        if have_new:
            np.save('./Data/etfs.npy', np.array(self.etfs))

            # 下载数据新添加的etf的历史数据
            download_data(input, ['1d', '1wk', '1mo'])

            # 发送更新所有页面的信号
            self.re_init_signal.emit('re_init')

        # 弹出消息框，提醒添加成功
        QMessageBox.information(self, 'Add new ETF', 'Successfully added new ETF')


    def remove_etf(self):
        list2remove = []
        for i in range(len(self.etfs)):
            if self.etfs_check_box[i].isChecked():
                self.etfs.remove(self.etfs_check_box[i].text())
                print(self.etfs_check_box[i].text())
                list2remove.append(self.etfs_check_box[i].text())

        if len(list2remove) > 0:
            # 的确有etf要被删除
            np.save('./Data/etfs.npy', np.array(self.etfs))

            # 删除所有有关这些etf的文件，包含rawdata和modeldata
            paths= ['./Data/rawdata/', './Data/modeldata/']

            for path in paths:
                files = os.listdir(path)
                for etf in list2remove:
                    for file in files:
                        if file.find(etf) >= 0:
                            os.remove(path+file)

            # 发送更新所有页面的信号
            self.re_init_signal.emit('re_init')

        # 弹出消息框，提醒添加成功
        QMessageBox.information(self, 'Remove ETFs', 'Successfully removed ETFs')








