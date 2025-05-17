import sqlite3

def init_db():
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            name TEXT,
            phone TEXT
        )
    ''')

    # Таблица книг
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            description TEXT,
            year INTEGER,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # Корзина
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TEXT NOT NULL DEFAULT (datetime('now')),
            status TEXT NOT NULL DEFAULT 'новый',
            total REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')

    conn.commit()
    conn.close()

def get_user(username, password):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

def register_user(username, password, name, phone):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, name, phone) VALUES (?, ?, ?, ?)",
                       (username, password, name, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, name, phone, role FROM users")
    result = cursor.fetchall()
    conn.close()
    return result

def update_user_role(user_id, new_role):
    import sqlite3
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    conn.commit()
    conn.close()

def get_books():
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, genre, year, price, stock FROM books")
    result = cursor.fetchall()
    conn.close()
    return result

def add_book(title, author, genre, description, year, price, stock):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO books (title, author, genre, description, year, price, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, author, genre, description, year, price, stock))
    conn.commit()
    conn.close()

def delete_book_by_title(title):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE title=?", (title,))
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT orders.id, users.username, orders.order_date, orders.total, orders.status
        FROM orders
        JOIN users ON orders.user_id = users.id
        ORDER BY orders.order_date DESC
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

def update_order_status(order_id, new_status):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
    conn.commit()
    conn.close()

def get_order_items(order_id):
    import sqlite3
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT books.title, books.author, order_items.price, order_items.quantity
        FROM order_items
        JOIN books ON order_items.book_id = books.id
        WHERE order_items.order_id = ?
    ''', (order_id,))
    result = cursor.fetchall()
    conn.close()
    return result


def make_order(user_id):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    # Получить содержимое корзины
    cursor.execute("""
        SELECT books.id, books.price, cart.quantity
        FROM cart
        JOIN books ON cart.book_id = books.id
        WHERE cart.user_id=?
    """, (user_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        conn.close()
        return False  # Корзина пуста

    total = sum(price * qty for _, price, qty in cart_items)

    # Добавить запись о заказе
    cursor.execute(
        "INSERT INTO orders (user_id, total) VALUES (?, ?)",
        (user_id, total)
    )
    order_id = cursor.lastrowid

    # --- ВАЖНО: Сохраняем книги в заказе! ---
    for book_id, price, qty in cart_items:
        cursor.execute(
            "INSERT INTO order_items (order_id, book_id, quantity, price) VALUES (?, ?, ?, ?)",
            (order_id, book_id, qty, price)
        )

    # Очищаем корзину
    cursor.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return True

def get_cart(user_id):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT books.title, books.author, books.price, cart.quantity
        FROM cart
        JOIN books ON cart.book_id = books.id
        WHERE cart.user_id=?
    """, (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def remove_from_cart(user_id, book_title):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM books WHERE title=?", (book_title,))
    result = cursor.fetchone()
    if result:
        book_id = result[0]
        cursor.execute("DELETE FROM cart WHERE user_id=? AND book_id=?", (user_id, book_id))
        conn.commit()
    conn.close()

def add_to_cart(user_id, book_title):
    import sqlite3
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    # Получаем id книги по названию
    cursor.execute("SELECT id FROM books WHERE title=?", (book_title,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return False
    book_id = result[0]
    # Проверяем, есть ли уже такой товар в корзине
    cursor.execute("SELECT quantity FROM cart WHERE user_id=? AND book_id=?", (user_id, book_id))
    item = cursor.fetchone()
    if item:
        # Если уже есть, увеличиваем количество
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id=? AND book_id=?", (user_id, book_id))
    else:
        # Иначе добавляем новую запись
        cursor.execute("INSERT INTO cart (user_id, book_id, quantity) VALUES (?, ?, 1)", (user_id, book_id))
    conn.commit()
    conn.close()
    return True

def get_genres():
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT genre FROM books ORDER BY genre")
    genres = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return genres


