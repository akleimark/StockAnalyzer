#!/usr/bin/env python3

import sys
import csv
import numpy as np
from datetime import datetime
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QInputDialog, QAction, QMenu, QMainWindow, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog, QLabel, QGridLayout
)
import matplotlib
matplotlib.use("Qt5Agg")  # Om du använder en Qt-baserad miljö
import matplotlib.pyplot as plt
from Database import DatabaseManager
from Stock import TechnicalAnalyzer

class StockAnalyzer(QMainWindow):
    start_x = 100
    start_y = 100
    end_x = 1200
    end_y = 900

    def __init__(self):
        super().__init__()
        self.obv_action = None
        self.roc_action = None
        self.ema_action = None
        self.import_csv_action = None
        self.graph_action = None
        self.moving_average_action = None
        self.technical_analysis_menu = None
        self.table_action = None
        self.add_stock_data_action = None
        self.show_stock_info_action = None
        self.tools_menu = None
        self.db = DatabaseManager()
        self.analyzer = TechnicalAnalyzer()
        self.selected_stock = None
        self.setWindowTitle("Aktie-app")
        self.setGeometry(self.start_x, self.start_y, self.end_x, self.end_y)
        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setFixedHeight(60)
        menu_bar.setStyleSheet("""
                QMenuBar {
                    font-size: 35px;
                    padding: 10px;
                }
            """)

        # Aktie-menyn
        stock_menu = menu_bar.addMenu("Aktier")
        stock_menu.setObjectName("Aktier")
        self.populate_stock_menu(stock_menu)

        add_stock_action = QAction("+ Lägg till en aktie", self)
        add_stock_action.triggered.connect(self.add_stock)
        stock_menu.addAction(add_stock_action)

        # Verktygsmeny
        self.tools_menu = menu_bar.addMenu("Verktyg")
        self.show_stock_info_action = QAction("Visa information", self)
        self.add_stock_data_action = QAction("Lägg till data", self)
        self.table_action = QAction("Tabell", self)
        self.graph_action = QAction("Graf", self)
        self.import_csv_action = QAction("Importera CSV", self)

        self.show_stock_info_action.setEnabled(False)
        self.add_stock_data_action.setEnabled(False)
        self.table_action.setEnabled(False)
        self.graph_action.setEnabled(False)
        self.import_csv_action.setEnabled(False)

        self.show_stock_info_action.triggered.connect(self.show_stock_info)
        self.add_stock_data_action.triggered.connect(self.add_stock_data)
        self.table_action.triggered.connect(self.show_table)
        self.graph_action.triggered.connect(self.show_graph)
        self.import_csv_action.triggered.connect(self.import_stock_data)

        self.tools_menu.addAction(self.show_stock_info_action)
        self.tools_menu.addAction(self.add_stock_data_action)
        self.tools_menu.addAction(self.table_action)
        self.tools_menu.addAction(self.graph_action)
        self.tools_menu.addAction(self.import_csv_action)

        # Teknisk analys-menyn
        self.technical_analysis_menu = menu_bar.addMenu("Teknisk analys")
        self.moving_average_action = QAction("SMA", self)
        self.ema_action = QAction("EMA", self)
        self.roc_action = QAction("ROC", self)
        self.obv_action = QAction("OBV", self)
        self.moving_average_action.setEnabled(False)
        self.ema_action.setEnabled(False)
        self.roc_action.setEnabled(False)
        self.obv_action.setEnabled(False)

        self.moving_average_action.triggered.connect(lambda: self.apply_technical_analysis("SMA"))
        self.ema_action.triggered.connect(lambda: self.apply_technical_analysis("EMA"))
        self.roc_action.triggered.connect(lambda: self.apply_technical_analysis("ROC"))
        self.obv_action.triggered.connect(lambda: self.apply_technical_analysis("OBV"))

        self.technical_analysis_menu.addAction(self.moving_average_action)
        self.technical_analysis_menu.addAction(self.ema_action)
        self.technical_analysis_menu.addAction(self.roc_action)
        self.technical_analysis_menu.addAction(self.obv_action)

    def populate_stock_menu(self, stock_menu):
        stocks = self.db.get_all_stocks() or []
        unique_stock_names = set(stock[1] for stock in stocks)

        for stock_name in unique_stock_names:
            stock_action = QAction(stock_name, self)
            stock_action.triggered.connect(lambda checked, name=stock_name: self.select_stock(name))
            stock_menu.addAction(stock_action)

    def select_stock(self, stock_name):
        self.selected_stock = stock_name
        self.show_stock_info_action.setEnabled(True)
        self.table_action.setEnabled(True)
        self.graph_action.setEnabled(True)
        self.import_csv_action.setEnabled(True)
        self.moving_average_action.setEnabled(True)
        self.ema_action.setEnabled(True)
        self.roc_action.setEnabled(True)
        self.add_stock_data_action.setEnabled(True)
        self.obv_action.setEnabled(True)

    def show_stock_info(self):
        variance = 0.0
        total_volume = 0
        if not self.selected_stock:
            return

        # Hämta historik för de senaste 6 månaderna
        history = self.db.get_stock_history(self.selected_stock, 6)
        if not history:
            stock_info_text = f"Aktie: {self.selected_stock}\n\nIngen data för de senaste 6 månaderna."
        else:
            # Extrahera priser och volymer
            prices = [price for _, price, _ in history]
            volumes = [volume for _, _, volume in history]

            # Beräkna variansen
            variance = np.var(prices, ddof=1) if len(prices) > 1 else 0

            # Beräkna den totala volymen för de senaste 6 månaderna
            total_volume = sum(volumes)

            # Formatera texten för att visa både varians och total volym
            stock_info_text = f"Aktie: {self.selected_stock}\n\n"
            stock_info_text += f"Varians (senaste 6 månaderna): {variance:.2f}\n"
            stock_info_text += f"Total Volym (senaste 6 månaderna): {total_volume}"

        label_title_font = QFont("Georgia", 16)
        label_title_font.setBold(True)
        label_normal_font = QFont("Georgia", 14)
        central_widget = QWidget(self)
        layout = QGridLayout(central_widget)

        # Lägg till etiketter och värden i layouten
        label1 = QLabel("Namn: ")
        label1.setFont(label_title_font)
        label2 = QLabel(self.selected_stock)
        label2.setFont(label_normal_font)
        label3 = QLabel("Varians: ")
        label3.setFont(label_title_font)
        label4 = QLabel(str(format(variance, ".2f")))
        label4.setFont(label_normal_font)
        label5 = QLabel("Total Volym: ")
        label5.setFont(label_title_font)
        label6 = QLabel(str(format(total_volume, ".0f")))
        label6.setFont(label_normal_font)

        # Lägg till etiketter och värden i gridlayouten
        layout.addWidget(label1, 0, 0)
        layout.addWidget(label2, 0, 1)
        layout.addWidget(label3, 1, 0)
        layout.addWidget(label4, 1, 1)
        layout.addWidget(label5, 2, 0)
        layout.addWidget(label6, 2, 1)

        self.setCentralWidget(central_widget)

    def add_stock_data(self):
        date, ok = QInputDialog.getText(self, self.selected_stock, 'Ange datum (YYYY-MM-DD):')
        if ok and date:
            price, ok = QInputDialog.getDouble(self, self.selected_stock, 'Ange aktiens pris:')
            if ok:
                volume, ok = QInputDialog.getInt(self, self.selected_stock, 'Ange handelsvolym:')
                if ok:
                    # Kontrollera om datumet finns för den valda aktien
                    if self.db.stock_exists_for_date(self.selected_stock, date):
                        print(
                            f"Aktien {self.selected_stock} finns och datumet {date} finns, uppdaterar pris och volym.")
                        self.db.update_stock_price(self.selected_stock, date, price,
                                                   volume)  # Uppdatera om datumet finns
                    else:
                        print(f"Aktien {self.selected_stock} finns, men datumet {date} saknas, lägg till nytt datum.")
                        self.db.add_stock(self.selected_stock, date, price, volume)  # Lägg till om datumet saknas

        self.refresh_menu()

    def add_stock(self):
        name, ok = QInputDialog.getText(self, 'Ny aktie', 'Ange aktiens namn:')
        if ok and name:
            date, ok = QInputDialog.getText(self, 'Ny aktie', 'Ange datum (YYYY-MM-DD):')
            if ok and date:
                price, ok = QInputDialog.getDouble(self, 'Ny aktie', 'Ange aktiens pris:')
                if ok:
                    volume, ok = QInputDialog.getInt(self, 'Ny aktie', 'Ange handelsvolym:')
                    if ok:
                        self.db.add_stock(name, date, price, volume)
                        self.refresh_menu()

    def refresh_menu(self):
        stock_menu = self.menuBar().findChild(QMenu, "Aktier")
        if stock_menu:
            stock_menu.clear()
            self.populate_stock_menu(stock_menu)
            add_stock_action = QAction("+ Lägg till aktie", self)
            add_stock_action.triggered.connect(self.add_stock)
            stock_menu.addAction(add_stock_action)
        else:
            print("Kunde inte hitta menyn 'Aktier'!")

    def show_table(self):
        if self.selected_stock:
            history = self.db.get_stock_history(self.selected_stock)
            if not history:
                print(f"Ingen historik hittades för {self.selected_stock}.")
                return

            table = QTableWidget()
            table.setRowCount(len(history))
            table.setColumnCount(3)  # Uppdaterad för att inkludera volym
            table.setHorizontalHeaderLabels(["Datum", "Pris (SEK)", "Volym"])

            for row_idx, (date, price, volume) in enumerate(history):
                table.setItem(row_idx, 0, QTableWidgetItem(str(date)))
                table.setItem(row_idx, 1, QTableWidgetItem(f"{price:.2f}"))
                table.setItem(row_idx, 2, QTableWidgetItem(str(volume)))  # Lägg till volym

            central_widget = QWidget(self)
            layout = QVBoxLayout(central_widget)
            layout.addWidget(table)
            self.setCentralWidget(central_widget)

    def show_graph(self):
        if not self.selected_stock:
            print("Ingen aktie vald!")
            return

        # Hämta aktiens historik från databasen
        history = self.db.get_stock_history(self.selected_stock)
        if not history:
            print(f"Ingen historik hittades för {self.selected_stock}.")
            return

        # Dela upp data i datum, pris och volym
        dates = [datetime.strptime(date, "%Y-%m-%d").date() for date, _, _ in history]
        prices = [price for _, price, _ in history]
        volumes = [volume for _, _, volume in history]

        # Skapa en figur med två subplots
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plotta pris på den första axeln
        ax1.set_xlabel("Datum")
        ax1.set_ylabel("Pris (SEK)", color="blue")
        ax1.plot(dates, prices, marker='o', linestyle='-', color="blue", label=f"{self.selected_stock} Pris")
        ax1.tick_params(axis="y", labelcolor="blue")

        # Skapa en andra axel för volymen
        ax2 = ax1.twinx()
        ax2.set_ylabel("Volym", color="green")
        ax2.bar(dates, volumes, width=0.8, color="green", alpha=0.3, label="Volym")
        ax2.tick_params(axis="y", labelcolor="green")

        # Anpassa utseendet
        plt.title(f"Pris och Volym för {self.selected_stock}")
        plt.xticks(rotation=45)

        # Visa grafen
        fig.tight_layout()  # Justera layout för att undvika överlappning
        plt.show()

    def import_stock_data(self):
        """Importerar aktievärden och volym från en CSV-fil och uppdaterar databasen."""
        if not self.selected_stock:
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Välj CSV-fil", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)

        if not file_path:
            return

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')  # Använder semikolon som separator

                # Läs in rubrikraden och avgör om den behöver hoppas över
                header = next(reader)
                if header[0].lower() == "date" and header[1].lower() == "price" and header[2].lower() == "volume":
                    print("Rubrikrad identifierad och hoppad över.")

                for row in reader:
                    if len(row) != 3:
                        print(f"Felaktig rad: {row}")
                        continue

                    date, price_str, volume_str = row
                    price_str = price_str.replace(',', '.')  # Byt ut ',' mot '.' i priset
                    volume_str = volume_str.replace(',', '.')  # Hantera decimaler i volymen också

                    try:
                        price = float(price_str)
                        volume = float(volume_str)
                    except ValueError:
                        print(f"Ogiltigt pris- eller volymformat: {row}")
                        continue

                    # Kontrollera om aktien finns
                    if not self.db.stock_exists(self.selected_stock):
                        print(f"Fel vid import:")
                        return

                    # Kontrollera om datumet finns för den valda aktien
                    if self.db.stock_exists_for_date(self.selected_stock, date):
                        print(
                            f"Aktien {self.selected_stock} finns och datumet {date} finns, uppdaterar pris och volym.")
                        self.db.update_stock_price(self.selected_stock, date, price, volume)  # Uppdatera
                    else:
                        print(f"Aktien {self.selected_stock} finns, men datumet {date} saknas, lägg till nytt datum.")
                        self.db.add_stock(self.selected_stock, date, price, volume)  # Lägg till ny data

            print(f"Importen av {self.selected_stock} från {file_path} slutförd.")

        except Exception as e:
            print(f"Fel vid import: {e}")

    def apply_technical_analysis(self, technical_analysis_option):

        if not self.selected_stock:
            print("Ingen aktie vald!")
            return

        history = self.db.get_stock_history(self.selected_stock)
        if not history:
            print(f"Ingen historik hittades för {self.selected_stock}.")
            return
        if technical_analysis_option == "SMA":
            self.analyzer.apply_moving_average_strategy(self.selected_stock, history)
        elif technical_analysis_option == "EMA":
            self.analyzer.apply_ema_strategy(self.selected_stock, history)
        elif technical_analysis_option == "ROC":
            self.analyzer.apply_roc_strategy(self.selected_stock, history)
        elif technical_analysis_option == "OBV":
            self.analyzer.apply_obv_strategy(self.selected_stock, history)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockAnalyzer()
    window.show()
    sys.exit(app.exec())