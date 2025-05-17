from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt

class OrderDetailsDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        from database import get_order_items
        self.setWindowTitle("Содержимое заказа")
        self.setMinimumSize(500, 300)
        layout = QVBoxLayout()
        title = QLabel(f"Заказ №{order_id}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Название", "Автор", "Цена", "Кол-во"])
        layout.addWidget(self.table)

        items = get_order_items(order_id)
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            for col in range(4):
                self.table.setItem(row, col, QTableWidgetItem(str(item[col])))

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)
