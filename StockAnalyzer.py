#!/usr/bin/env python3
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QInputDialog, QAction, QMenu
from PyQt5.QtWidgets import QMainWindow
from Database import DatabaseManager

class StockAnalyzer(QMainWindow):
    #Koordinater för fönstret.
    start_x = 100
    start_y = 100
    end_x = 1200
    end_y = 900

    def __init__(self):
        super().__init__()

        # Initiera self.db här så den är tillgänglig för create_menu_bar
        self.db = DatabaseManager()  # Skapa en instans av DatabaseManager
        self.setWindowTitle("Aktie-app")
        self.setGeometry(self.start_x, self.start_y, self.end_x, self.end_y)
        self.create_menu_bar()

    #Skapar menyn
    def create_menu_bar(self):
        menu_bar_height = 60
        menu_bar = self.menuBar()
        menu_bar.setFixedHeight(menu_bar_height)
        menu_bar.setStyleSheet("""
                QMenuBar {
                    font-size: 35px;
                    padding: 10px;
                }
            """)
        # Aktie-menyn
        stock_menu = menu_bar.addMenu("Aktier")
        stock_menu.setFont(QFont("Arial", 20))
        # Lägg till menyalternativ för alla aktier i databasen
        self.populate_stock_menu(stock_menu)

        # Lägg till alternativ för att lägga till aktie
        add_stock_action = QAction("+ Lägg till en aktie", self)
        add_stock_action.triggered.connect(self.add_stock)
        stock_menu.addAction(add_stock_action)

    def populate_stock_menu(self, stock_menu):
        """Lägger till alla aktier från databasen i menyn."""
        stocks = self.db.get_all_stocks()  # Hämtar alla aktier från databasen
        for stock in stocks:
            stock_name = stock[1]  # Namn på aktien
            stock_price = stock[2]  # Aktiekurs
            stock_action = QAction(f"{stock_name} - {stock_price} SEK", self)
            # Här kan man lägga till funktionalitet för att t.ex. visa aktiens detaljer när man klickar
            stock_menu.addAction(stock_action)

    def add_stock(self):
        """Visar en dialog för att lägga till en aktie."""
        name, ok = QInputDialog.getText(self, 'Ny aktie', 'Ange aktiens namn:')
        if ok and name:
            price, ok = QInputDialog.getDouble(self, 'Ny aktie', 'Ange aktiens pris:')
            if ok:
                self.db.add_stock(name, price)  # Lägg till aktien i databasen
                self.refresh_menu()  # Uppdatera menyn

    def refresh_menu(self):
        """Uppdatera aktie-menyn efter att en ny aktie lagts till."""
        # Ta bort gamla aktie-menyalternativ och lägg till dem på nytt
        stock_menu = self.menuBar().findChild(QMenu, "Aktier")
        stock_menu.clear()  # Rensa menyn
        self.populate_stock_menu(stock_menu)  # Lägg till aktierna på nytt
        # Lägg till alternativet för att lägga till aktie igen
        add_stock_action = QAction("+ Lägg till aktie", self)
        add_stock_action.triggered.connect(self.add_stock)
        stock_menu.addAction(add_stock_action)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockAnalyzer()
    window.show()
    sys.exit(app.exec())
