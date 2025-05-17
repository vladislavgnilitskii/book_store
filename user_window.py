from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QWidget as QW, QHBoxLayout as QHL, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt
from database import get_books, add_to_cart, get_genres
from cart_window import CartDialog

class UserWindow(QWidget):
    def __init__(self, user, auth_window):
        super().__init__()
        self.user = user
        self.auth_window = auth_window
        self.setWindowTitle("Книжный магазин")
        self.setMinimumSize(765, 400)

        main_layout = QVBoxLayout()

        # --- ВЕРХНЯЯ ПАНЕЛЬ: название + Выйти справа ---
        header_layout = QHBoxLayout()
        title = QLabel("Каталог книг")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        logout_btn = QPushButton("Выйти")
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        main_layout.addLayout(header_layout)

        # --- Фильтры ---
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или автору")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("Поиск:"))
        filter_layout.addWidget(self.search_input)

        self.genre_combo = QComboBox()
        self.genre_combo.addItem("Все жанры")
        self.genre_combo.addItems(get_genres())
        self.genre_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("Жанр:"))
        filter_layout.addWidget(self.genre_combo)

        self.price_sort = QComboBox()
        self.price_sort.addItems(["Без сортировки", "Сначала дешевые", "Сначала дорогие"])
        self.price_sort.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("Сортировка:"))
        filter_layout.addWidget(self.price_sort)

        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # --- Таблица книг ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["", "Название", "Автор", "Жанр", "Год", "Цена", "В наличии"]
        )
        main_layout.addWidget(self.table)

        # --- Кнопки снизу ---
        buttons = QHBoxLayout()
        add_selected_btn = QPushButton("Добавить выбранные в корзину")
        add_selected_btn.clicked.connect(self.add_selected_to_cart)
        cart_btn = QPushButton("Корзина")
        cart_btn.clicked.connect(self.show_cart)
        buttons.addWidget(add_selected_btn)
        buttons.addWidget(cart_btn)
        buttons.addStretch()
        main_layout.addLayout(buttons)

        self.setLayout(main_layout)
        self.apply_filters()

    def apply_filters(self):
        genre = self.genre_combo.currentText()
        price_sort = self.price_sort.currentText()
        search_text = self.search_input.text().strip().lower()

        query = """
            SELECT title, author, genre, year, price, stock
            FROM books
            WHERE 1=1
        """
        params = []

        # Фильтр по жанру
        if genre != "Все жанры":
            query += " AND genre = ?"
            params.append(genre)

        # Поиск по словам (название и автор)
        if search_text:
            search_words = search_text.split()
            search_conditions = []
            for word in search_words:
                search_conditions.append("(LOWER(title) LIKE ? OR LOWER(author) LIKE ?)")
                params.extend([f"%{word}%", f"%{word}%"])
            query += " AND (" + " AND ".join(search_conditions) + ")"

        # Сортировка по цене
        if price_sort == "Сначала дешевые":
            query += " ORDER BY price ASC"
        elif price_sort == "Сначала дорогие":
            query += " ORDER BY price DESC"

        try:
            import sqlite3
            conn = sqlite3.connect('database.sqlite3')
            books = conn.execute(query, params).fetchall()
            conn.close()
            self.load_books(books)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить фильтры: {str(e)}")

    def load_books(self, books):
        self.table.setRowCount(len(books))
        for row, book in enumerate(books):
            # Чекбокс в первую колонку
            checkbox = QCheckBox()
            widget = QW()
            layout = QHL(widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.table.setCellWidget(row, 0, widget)
            # Остальные данные книги
            self.table.setItem(row, 1, QTableWidgetItem(str(book[0])))  # Название
            self.table.setItem(row, 2, QTableWidgetItem(str(book[1])))  # Автор
            self.table.setItem(row, 3, QTableWidgetItem(str(book[2])))  # Жанр
            self.table.setItem(row, 4, QTableWidgetItem(str(book[3])))  # Год
            self.table.setItem(row, 5, QTableWidgetItem(str(book[4])))  # Цена
            self.table.setItem(row, 6, QTableWidgetItem(str(book[5])))  # В наличии

    def add_selected_to_cart(self):
        added = 0
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if widget and widget.layout().itemAt(0).widget().isChecked():
                book_title = self.table.item(row, 1).text()
                if add_to_cart(self.user[0], book_title):
                    added += 1
        if added:
            QMessageBox.information(self, "Корзина", f"Добавлено книг в корзину: {added}")
        else:
            QMessageBox.information(self, "Корзина", "Не выбрано ни одной книги.")

    def show_cart(self):
        cart_dialog = CartDialog(self.user[0], self)
        cart_dialog.exec_()

    def logout(self):
        self.close()
        self.auth_window.show()
