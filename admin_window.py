from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QMessageBox, QTabWidget,
    QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt
from database import (
    get_books, get_all_users, add_book, delete_book_by_title, update_user_role,
    get_all_orders, update_order_status
)
from add_book_dialog import AddBookDialog
from order_details_dialog import OrderDetailsDialog

class AdminWindow(QWidget):
    def __init__(self, admin_user, auth_window):
        super().__init__()
        self.admin_user = admin_user
        self.auth_window = auth_window
        self.setWindowTitle("Панель администратора")
        self.setMinimumSize(680, 500)

        main_layout = QVBoxLayout()

        # --- ВЕРХНЯЯ ПАНЕЛЬ: название + Выйти справа ---
        header_layout = QHBoxLayout()
        title = QLabel("Панель администратора")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        logout_btn = QPushButton("Выйти")
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        main_layout.addLayout(header_layout)

        # --- ТАБЫ ---
        self.tabs = QTabWidget()
        self.books_tab = QWidget()
        self.users_tab = QWidget()
        self.orders_tab = QWidget()
        self.tabs.addTab(self.books_tab, "Книги")
        self.tabs.addTab(self.users_tab, "Пользователи")
        self.tabs.addTab(self.orders_tab, "Заказы")
        main_layout.addWidget(self.tabs)

        # --- КНИГИ ---
        books_layout = QVBoxLayout()
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(6)
        self.books_table.setHorizontalHeaderLabels(["Название", "Автор", "Жанр", "Год", "Цена", "В наличии"])
        books_layout.addWidget(self.books_table)
        self.load_books()
        books_btns = QHBoxLayout()
        add_btn = QPushButton("Добавить книгу")
        add_btn.clicked.connect(self.add_book_dialog)
        delete_btn = QPushButton("Удалить книгу")
        delete_btn.clicked.connect(self.delete_book)
        books_btns.addWidget(add_btn)
        books_btns.addWidget(delete_btn)
        books_btns.addStretch()
        books_layout.addLayout(books_btns)
        self.books_tab.setLayout(books_layout)

        # --- ПОЛЬЗОВАТЕЛИ ---
        users_layout = QVBoxLayout()
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["", "ID", "Логин", "Имя", "Телефон", "Роль"])
        users_layout.addWidget(self.users_table)
        self.load_users()

        # Панель для массовой смены роли
        change_role_layout = QHBoxLayout()
        change_role_layout.addStretch()
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        change_role_layout.addWidget(self.role_combo)
        change_btn = QPushButton("Изменить роль выбранным")
        change_btn.clicked.connect(self.change_roles_for_selected)
        change_role_layout.addWidget(change_btn)
        users_layout.addLayout(change_role_layout)

        self.users_tab.setLayout(users_layout)

        # --- ЗАКАЗЫ ---
        self.setup_orders_tab()

        self.setLayout(main_layout)

    def load_books(self):
        books = get_books()
        self.books_table.setRowCount(len(books))
        for row, book in enumerate(books):
            for col in range(6):
                self.books_table.setItem(row, col, QTableWidgetItem(str(book[col])))

    def add_book_dialog(self):
        dialog = AddBookDialog(self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()
            if not data[0] or not data[1]:
                QMessageBox.warning(self, "Ошибка", "Заполните название и автора!")
                return
            add_book(*data)
            self.load_books()
            QMessageBox.information(self, "Готово", "Книга успешно добавлена!")

    def delete_book(self):
        row = self.books_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для удаления")
            return
        title_item = self.books_table.item(row, 0)
        if not title_item:
            QMessageBox.warning(self, "Ошибка", "Некорректная строка")
            return
        title = title_item.text()
        reply = QMessageBox.question(
            self, "Подтвердите", f"Удалить книгу «{title}»?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            delete_book_by_title(title)
            self.load_books()
            QMessageBox.information(self, "Удалено", "Книга удалена")

    def load_users(self):
        users = get_all_users()
        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            # Чекбокс для выбора
            checkbox = QCheckBox()
            widget = QWidget()
            lay = QHBoxLayout(widget)
            lay.addWidget(checkbox)
            lay.setAlignment(Qt.AlignCenter)
            lay.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(lay)
            self.users_table.setCellWidget(row, 0, widget)

            self.users_table.setItem(row, 1, QTableWidgetItem(str(user[0])))  # ID
            self.users_table.setItem(row, 2, QTableWidgetItem(user[1]))       # Логин
            self.users_table.setItem(row, 3, QTableWidgetItem(user[2]))       # Имя
            self.users_table.setItem(row, 4, QTableWidgetItem(user[3]))       # Телефон
            self.users_table.setItem(row, 5, QTableWidgetItem(user[4]))       # Роль

    def change_roles_for_selected(self):
        new_role = self.role_combo.currentText()
        changed = 0
        skipped = 0
        for row in range(self.users_table.rowCount()):
            widget = self.users_table.cellWidget(row, 0)
            if widget and widget.layout().itemAt(0).widget().isChecked():
                current_role = self.users_table.item(row, 5).text()
                if current_role == new_role:
                    skipped += 1
                    continue
                user_id = int(self.users_table.item(row, 1).text())
                update_user_role(user_id, new_role)
                self.users_table.setItem(row, 5, QTableWidgetItem(new_role))
                changed += 1
        if changed:
            QMessageBox.information(self, "Успешно", f"Роль изменена у {changed} пользователей.")
        if skipped:
            QMessageBox.warning(self, "Внимание", f"У {skipped} пользователей роль уже была «{new_role}» и не была изменена.")
        if not changed and not skipped:
            QMessageBox.information(self, "Нет изменений", "Выберите пользователей для изменения роли.")

    # ==== ЗАКАЗЫ ====
    def setup_orders_tab(self):
        orders_layout = QVBoxLayout()
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels(
            ["ID", "Пользователь", "Дата", "Сумма", "Статус", "Действие"]
        )
        orders_layout.addWidget(self.orders_table)
        self.load_orders()
        self.orders_tab.setLayout(orders_layout)

    def load_orders(self):
        orders = get_all_orders()
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            for col in range(4):
                self.orders_table.setItem(row, col, QTableWidgetItem(str(order[col])))
            # Статус — ComboBox
            status_combo = QComboBox()
            status_combo.addItems(["новый", "выполнен", "отменён"])
            status_combo.setCurrentText(order[4])
            view_btn = QPushButton("Просмотр")
            view_btn.clicked.connect(lambda checked, oid=order[0]: self.show_order_details(oid))
            self.orders_table.setCellWidget(row, 5, view_btn)
            status_combo.order_id = order[0]
            status_combo.currentTextChanged.connect(self.change_order_status)
            self.orders_table.setCellWidget(row, 4, status_combo)
            # Пустая колонка "Действие" (можно убрать)
            self.orders_table.setItem(row, 5, QTableWidgetItem(""))

    def change_order_status(self, new_status):
        combo = self.sender()
        order_id = combo.order_id
        update_order_status(order_id, new_status)
        # Можно добавить цвет или сообщение при смене статуса

    def show_order_details(self, order_id):
        dlg = OrderDetailsDialog(order_id, self)
        dlg.exec_()

    def logout(self):
        self.close()
        self.auth_window.show()
