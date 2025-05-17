from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout,
    QLineEdit, QPushButton, QMessageBox, QSizePolicy, QLabel
)
from PyQt5.QtCore import Qt
from database import get_user, register_user
from user_window import UserWindow
from admin_window import AdminWindow


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Книжный магазин")
        self.setFixedSize(400, 400)

        # Внутренний контейнер с заголовком и табами
        inner_layout = QVBoxLayout()
        inner_layout.setAlignment(Qt.AlignCenter)
        inner_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        title = QLabel("Авторизация")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.tabs.addTab(self.login_tab(), "Вход")
        self.tabs.addTab(self.register_tab(), "Регистрация")

        inner_layout.addWidget(title)
        inner_layout.addWidget(self.tabs)

        # Центральный контейнер
        center_widget = QWidget()
        center_widget.setLayout(inner_layout)

        # Внешний layout — центрирует всё по окну
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.addWidget(center_widget)

        self.setLayout(outer_layout)

    def login_tab(self):
        outer = QWidget()
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(0, 0, 0, 0)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Введите пароль")

        login_btn = QPushButton("Войти")
        login_btn.setFixedHeight(32)
        login_btn.clicked.connect(self.handle_login)

        form.addRow("Логин", self.login_input)
        form.addRow("Пароль", self.pass_input)
        form.addRow("", login_btn)

        inner_widget = QWidget()
        inner_widget.setLayout(form)
        inner_widget.setFixedWidth(300)
        inner_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        outer_layout.addWidget(inner_widget)
        outer.setLayout(outer_layout)
        return outer

    def register_tab(self):
        outer = QWidget()
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        form = QFormLayout()
        form.setSpacing(10)
        form.setContentsMargins(0, 0, 0, 0)

        self.reg_login_input = QLineEdit()
        self.reg_login_input.setPlaceholderText("Придумайте логин")

        self.reg_pass_input = QLineEdit()
        self.reg_pass_input.setEchoMode(QLineEdit.Password)
        self.reg_pass_input.setPlaceholderText("Придумайте пароль")

        self.reg_name_input = QLineEdit()
        self.reg_name_input.setPlaceholderText("Ваше имя")

        self.reg_phone_input = QLineEdit()
        self.reg_phone_input.setPlaceholderText("Номер телефона")

        reg_btn = QPushButton("Зарегистрироваться")
        reg_btn.setFixedHeight(32)
        reg_btn.clicked.connect(self.handle_register)

        form.addRow("Логин", self.reg_login_input)
        form.addRow("Пароль", self.reg_pass_input)
        form.addRow("Имя", self.reg_name_input)
        form.addRow("Телефон", self.reg_phone_input)
        form.addRow("", reg_btn)

        inner_widget = QWidget()
        inner_widget.setLayout(form)
        inner_widget.setFixedWidth(300)
        inner_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        outer_layout.addWidget(inner_widget)
        outer.setLayout(outer_layout)
        return outer

    def handle_login(self):
        login = self.login_input.text().strip()
        password = self.pass_input.text().strip()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        user = get_user(login, password)
        if user:
            role = user[3]  # поле "role

            self.hide()  # Скрыть окно авторизации

            if role == 'user':
                self.user_window = UserWindow(user, self)
                self.user_window.show()
            elif role == 'admin':
                self.admin_window = AdminWindow(user, self)
                self.admin_window.show()
            else:
                QMessageBox.warning(self, "Ошибка", f"Неизвестная роль: {role}")
                self.show()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")

    def handle_register(self):
        login = self.reg_login_input.text().strip()
        password = self.reg_pass_input.text().strip()
        name = self.reg_name_input.text().strip()
        phone = self.reg_phone_input.text().strip()

        if not all([login, password, name, phone]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if register_user(login, password, name, phone):
            QMessageBox.information(self, "Успех", "Вы успешно зарегистрированы!")
            self.tabs.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
