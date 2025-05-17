from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox, QSpinBox, QTextEdit, QDoubleSpinBox
)

class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить книгу")
        self.setMinimumWidth(350)
        layout = QVBoxLayout()

        # Название
        self.title_input = QLineEdit()
        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.title_input)

        # Автор
        self.author_input = QLineEdit()
        layout.addWidget(QLabel("Автор"))
        layout.addWidget(self.author_input)

        # Жанр
        self.genre_input = QLineEdit()
        layout.addWidget(QLabel("Жанр"))
        layout.addWidget(self.genre_input)

        # Описание
        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(50)
        layout.addWidget(QLabel("Описание"))
        layout.addWidget(self.desc_input)

        # Год
        self.year_input = QSpinBox()
        self.year_input.setRange(1500, 2100)
        self.year_input.setValue(2000)
        layout.addWidget(QLabel("Год издания"))
        layout.addWidget(self.year_input)

        # Цена
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 100000)
        self.price_input.setDecimals(2)
        layout.addWidget(QLabel("Цена"))
        layout.addWidget(self.price_input)

        # В наличии
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 1000)
        layout.addWidget(QLabel("В наличии (шт)"))
        layout.addWidget(self.stock_input)

        # Кнопки
        btns = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(add_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

        self.setLayout(layout)

    def get_data(self):
        return (
            self.title_input.text().strip(),
            self.author_input.text().strip(),
            self.genre_input.text().strip(),
            self.desc_input.toPlainText().strip(),
            self.year_input.value(),
            float(self.price_input.value()),
            self.stock_input.value()
        )
