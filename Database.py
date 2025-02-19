#!/usr/bin/env python3
import sqlite3

class DatabaseManager:
    def __init__(self, db_name="stocks.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Skapa tabellen för aktier om den inte finns
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, 
                the_date TEXT NOT NULL,                       
                price REAL NOT NULL,
                volume INTEGER NOT NULL DEFAULT 0,  -- Ny kolumn för volym
                UNIQUE(name, the_date)
            )
        """)

        # Skapa tabellen för inställningar (settings) om den inte finns
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_type TEXT NOT NULL,  -- Typ av inställning (t.ex. Sharpe Ratio)
                setting_value TEXT NOT NULL, -- Värdet för inställningen (kan vara sträng, t.ex. "0.02")
                UNIQUE(setting_type)
            )
        """)

        self.conn.commit()

    def add_stock(self, name, date, price, volume):
        print (name)
        print (date)
        print (price)
        self.cursor.execute("INSERT INTO stocks (name, the_date, price, volume) VALUES (?, ?, ?, ?)", (name, date, price, volume))
        self.conn.commit()

        """
        try:
            self.cursor.execute("INSERT INTO stocks (name, the_date, price, volume) VALUES (?, ?, ?)", (name, date, price, volume))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # Om aktien redan finns, uppdatera istället för att ge fel
            self.update_stock_price(name, date, price)
        """
    def stock_exists(self, name):
        self.cursor.execute("SELECT COUNT(*) FROM stocks WHERE name = ?", (name,))
        return self.cursor.fetchone()[0] > 0

    def update_stock_price(self, name, date, new_price, volume):
        self.cursor.execute(
            "UPDATE stocks SET price = ?, volume = ? WHERE name = ? AND the_date = ?",
            (new_price, volume, name, date)
        )
        updated_rows = self.cursor.rowcount  # Antal rader som faktiskt uppdaterades
        self.conn.commit()

        if updated_rows > 0:
            print(f"✅ Uppdaterade {name} {date} med nytt pris {new_price} och volym {volume}")
        else:
            print(f"⚠ Ingen rad uppdaterades för {name} {date}. Kontrollera att aktien existerar i databasen!")

    def stock_exists_for_date(self, name, date):
        self.cursor.execute("SELECT COUNT(*) FROM stocks WHERE name = ? AND the_date = ?", (name, date))
        return self.cursor.fetchone()[0] > 0

    def get_all_stocks(self):
        self.cursor.execute("SELECT * FROM stocks ORDER BY name, the_date")
        stocks = self.cursor.fetchall()
        return stocks

    def get_stock_prices(self, stock_name):
        self.cursor.execute("""
                    SELECT price FROM stocks 
                    WHERE name = ? ORDER BY the_date ASC
                """, (stock_name,))  # Lägg till kommatecken för att skapa en tuple

        return self.cursor.fetchall()

    def get_stock_history(self, stock_name, months=6):
        """Hämtar aktiens historik inklusive datum, pris och volym för de senaste månaderna."""
        self.cursor.execute("""
            SELECT the_date, price, volume FROM stocks 
            WHERE name = ? AND the_date >= DATE('now', ? || ' months') 
            ORDER BY the_date ASC
        """, (stock_name, f'-{months}'))

        return self.cursor.fetchall()  # Returnerar en lista av tuples (datum, pris, volym)

    def set_setting(self, setting_type, setting_value):
        self.cursor.execute("""
            INSERT OR REPLACE INTO settings (setting_type, setting_value)
            VALUES (?, ?)
        """, (setting_type, str(setting_value)))  # Förvandla värdet till sträng
        self.conn.commit()

    def get_setting(self, setting_type):
        self.cursor.execute("""
            SELECT setting_value FROM settings WHERE setting_type = ?
        """, (setting_type,))
        result = self.cursor.fetchone()
        return int(result[0]) if result else None  # Om inställning finns, returnera som int

    def close(self):
        self.conn.close()
