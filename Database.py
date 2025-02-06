import sqlite3

class DatabaseManager:
    def __init__(self, db_name="stocks.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, 
                the_date TEXT NOT NULL,                       
                price REAL NOT NULL,
                UNIQUE(name, the_date)
            )
        """)
        self.conn.commit()

    def add_stock(self, name, date, price):
        print (name)
        print (date)
        print (price)
        self.cursor.execute("INSERT INTO stocks (name, the_date, price) VALUES (?, ?, ?)", (name, date, price))
        self.conn.commit()

        """
        try:
            self.cursor.execute("INSERT INTO stocks (name, the_date, price) VALUES (?, ?, ?)", (name, date, price))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # Om aktien redan finns, uppdatera istället för att ge fel
            self.update_stock_price(name, date, price)
        """
    def stock_exists(self, name):
        self.cursor.execute("SELECT COUNT(*) FROM stocks WHERE name = ?", (name,))
        return self.cursor.fetchone()[0] > 0

    def update_stock_price(self, name, date, new_price):
        self.cursor.execute("UPDATE stocks SET price = ? WHERE name = ? AND the_date = ?", (new_price, name, date))
        updated_rows = self.cursor.rowcount  # Antal rader som faktiskt uppdaterades
        self.conn.commit()

        if updated_rows > 0:
            print(f"✅ Uppdaterade {name} {date} med nytt pris {new_price}")
        else:
            print(f"⚠ Ingen rad uppdaterades för {name} {date}. Kontrollera att aktien existerar i databasen!")

    def stock_exists_for_date(self, name, date):
        self.cursor.execute("SELECT COUNT(*) FROM stocks WHERE name = ? AND the_date = ?", (name, date))
        return self.cursor.fetchone()[0] > 0

    def get_all_stocks(self):
        self.cursor.execute("SELECT * FROM stocks ORDER BY name, the_date")
        stocks = self.cursor.fetchall()
        return stocks
        #return [Stock(name, date, price) for name, date, price in stocks]

    def get_stock_history(self, stock_name):
        self.cursor.execute("SELECT the_date, price FROM stocks WHERE name = ? ORDER BY the_date", (stock_name,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
