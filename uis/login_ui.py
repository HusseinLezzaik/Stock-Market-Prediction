from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QLineEdit, QPushButton, QGridLayout,  QMessageBox
import qdarkstyle

class LoginForm(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle('Login')

        self.user_label = QLabel('User')

        self.pwd_label = QLabel('Password')

        self.user_edit = QLineEdit(self)
        self.user_edit.setPlaceholderText('user name')
        self.user_edit.setEchoMode(QLineEdit.Normal)

        self.pwd_edit = QLineEdit(self)
        self.pwd_edit.setPlaceholderText('******')
        self.pwd_edit.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton('Login', self)
        self.login_btn.clicked.connect(self.handle_login)

        self.layout = QGridLayout(self)

        self.layout.addWidget(self.user_label, 0, 0)
        self.layout.addWidget(self.user_edit, 0, 1)
        self.layout.addWidget(self.pwd_label, 1, 0)
        self.layout.addWidget(self.pwd_edit, 1, 1)
        self.layout.addWidget(self.login_btn, 2, 1)

        self.setWindowOpacity(0.9)
        self.layout.setSpacing(10)
        # 设置窗口主题
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())


    def handle_login(self):
        if self.user_edit.text() == '' and self.pwd_edit.text() == '':
            self.accept()  # 关键
        else:
            QMessageBox.warning(
                self, 'Error', 'Bad user or password')

class Login(QWidget):
    def __init__(self):
        QWidget.__init__(self)