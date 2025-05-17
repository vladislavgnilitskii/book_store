from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from database import get_cart, remove_from_cart, make_order


class CartDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Корзина")
        self.setMinimumSize(420, 320)
        self.setModal(True)

        layout = QVBoxLayout()
        title = QLabel("Ваша корзина")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Название", "Автор", "Цена", "Кол-во"])
        layout.addWidget(self.table)

        self.load_cart()

        btns = QHBoxLayout()
        remove_btn = QPushButton("Удалить выбранное")
        remove_btn.clicked.connect(self.remove_selected)
        order_btn = QPushButton("Оформить заказ")
        order_btn.clicked.connect(self.make_order_placeholder)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        btns.addWidget(remove_btn)
        btns.addStretch()
        btns.addWidget(order_btn)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

        self.setLayout(layout)

    def load_cart(self):
        cart = get_cart(self.user_id)
        self.table.setRowCount(len(cart))
        for row, item in enumerate(cart):
            for col in range(4):
                self.table.setItem(row, col, QTableWidgetItem(str(item[col])))

    def remove_selected(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для удаления")
            return
        book_title = self.table.item(row, 0).text()
        remove_from_cart(self.user_id, book_title)
        self.load_cart()

    def make_order_placeholder(self):
        # Проверяем, пуста ли корзина
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста")
            return
        success = make_order(self.user_id)
        if success:
            QMessageBox.information(self, "Успех", "Заказ успешно оформлен!")
            self.load_cart()  # обновляем таблицу (станет пустой)
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось оформить заказ")

