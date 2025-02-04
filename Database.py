#!/usr/bin/env python3
import sqlite3
class DatabaseManager:
    def __init__(self, db_name="stocks.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        #Skapar en tabell för aktier om den inte redan finns.
        self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stocks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE, 
                        the_date DATETIME NOT NULL,                       
                        price REAL NOT NULL
                    )
                """)
        self.conn.commit()

    def add_stock(self, name, price):
        """Lägger till en ny aktie i databasen."""
        try:
            self.cursor.execute("INSERT INTO stocks (name, price) VALUES (?, ?, ?)",
                                (name, price))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"Fel: Aktien med symbolen '{name}' finns redan.")

    def get_all_stocks(self):
        """Hämtar alla aktier från databasen."""
        self.cursor.execute("SELECT * FROM stocks")
        return self.cursor.fetchall()

    def update_stock_price(self, name, date, new_price):
        """Uppdaterar aktiens pris baserat på namn och datum."""
        self.cursor.execute(
            "UPDATE stocks SET price = ? WHERE name = ? AND date = ?",
            (new_price, name, date)
        )
        self.conn.commit()

    def delete_stock(self, name):
        """Tar bort en aktie baserat på namn."""
        self.cursor.execute("DELETE FROM stocks WHERE name = ?", (name,))
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()
