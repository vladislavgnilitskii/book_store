import sys
from PyQt5.QtWidgets import QApplication
from auth_window import AuthWindow
from database import init_db

def load_stylesheet(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)

    # Подключаем QSS стили
    app.setStyleSheet(load_stylesheet("styles.qss"))

    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())
