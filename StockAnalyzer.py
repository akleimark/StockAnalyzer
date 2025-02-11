#!/usr/bin/env python3

import sys
import csv
import numpy as np
from datetime import datetime

import pandas as pd
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QInputDialog, QAction, QMenu, QMainWindow, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog, QLabel, QGridLayout, QSpinBox, QDoubleSpinBox
)
import matplotlib

from EMAStrategy import EMAStrategy
from FibonacciStrategy import FibonacciStrategy
from OBVStrategy import OBVStrategy
from ROCStrategy import ROCStrategy
from SMAStrategy import SMAStrategy

matplotlib.use("Qt5Agg")  # Om du använder en Qt-baserad miljö
import matplotlib.pyplot as plt
from Database import DatabaseManager

class StockAnalyzer(QMainWindow):
    start_x = 100
    start_y = 100
    end_x = 1200
    end_y = 900

    def __init__(self):
        super().__init__()
        self.settings_action = None
        self.misc_menu = None
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
        self.fibonacci_retracement_action = QAction("Fibonacci Retracement", self)
        self.moving_average_action.setEnabled(False)
        self.ema_action.setEnabled(False)
        self.roc_action.setEnabled(False)
        self.obv_action.setEnabled(False)
        self.fibonacci_retracement_action.setEnabled(False)

        self.moving_average_action.triggered.connect(lambda: self.apply_technical_analysis("SMA"))
        self.ema_action.triggered.connect(lambda: self.apply_technical_analysis("EMA"))
        self.roc_action.triggered.connect(lambda: self.apply_technical_analysis("ROC"))
        self.obv_action.triggered.connect(lambda: self.apply_technical_analysis("OBV"))
        self.fibonacci_retracement_action.triggered.connect(lambda: self.apply_technical_analysis("FIBONACCI_RETRACEMENT"))

        self.technical_analysis_menu.addAction(self.moving_average_action)
        self.technical_analysis_menu.addAction(self.ema_action)
        self.technical_analysis_menu.addAction(self.roc_action)
        self.technical_analysis_menu.addAction(self.obv_action)
        self.technical_analysis_menu.addAction(self.fibonacci_retracement_action)

        # Menyn Övrigt
        self.misc_menu = menu_bar.addMenu("Övrigt")
        self.settings_action = QAction("Inställningar", self)
        self.misc_menu.addAction(self.settings_action)
        self.settings_action.triggered.connect(self.settings)

    def populate_stock_menu(self, stock_menu):
        stocks = self.db.get_all_stocks() or []
        unique_stock_names = set(stock[1] for stock in stocks)  # Hämta unika aktienamn

        # Sortera aktienamnen i bokstavsordning
        sorted_stock_names = sorted(unique_stock_names)

        # Lägg till aktier i menyn i ordning
        for stock_name in sorted_stock_names:
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
        self.fibonacci_retracement_action.setEnabled(True)

    def settings(self):
        label_title_font = QFont("Georgia", 16)
        label_title_font.setBold(True)
        label_normal_font = QFont("Georgia", 14)

        central_widget = QWidget(self)
        layout = QGridLayout(central_widget)

        # Etiketter
        label1 = QLabel("Historik (antal månader): ")
        label1.setFont(label_title_font)

        label2 = QLabel("Sharpe ratio (antal månader): ")
        label2.setFont(label_title_font)

        label3 = QLabel("Riskfri avkastning (%) för Sharpe Ratio: ")
        label3.setFont(label_title_font)

        label4 = QLabel("Startkapital för testköp (SEK): ")
        label4.setFont(label_title_font)

        # Ny etikett och QSpinBox för ROC-period
        label5 = QLabel("ROC-period: ")
        label5.setFont(label_title_font)

        roc_period_spinbox = QSpinBox()
        roc_period_spinbox.setFont(label_normal_font)
        roc_period_spinbox.setRange(1, 50)  # Sätt intervallet för ROC-perioden
        roc_period_spinbox.setValue(self.db.get_setting("roc_period") or 14)  # Standard 14

        # Ny etikett och QSpinBox för ROC-threshold
        label6 = QLabel("ROC-threshold (%): ")
        label6.setFont(label_title_font)

        roc_threshold_spinbox = QSpinBox()
        roc_threshold_spinbox.setFont(label_normal_font)
        roc_threshold_spinbox.setRange(-100, 100)  # ROC-threshold kan vara mellan -100 och 100
        roc_threshold_spinbox.setSingleStep(1)
        roc_threshold_spinbox.setValue(self.db.get_setting("roc_threshold") or 0)  # Standard 0

        # QSpinBox för antal månader av historik
        months_history_spinbox = QSpinBox()
        months_history_spinbox.setFont(label_normal_font)
        months_history_spinbox.setRange(1, 24)
        months_history_spinbox.setValue(self.db.get_setting("history") or 6)

        # QSpinBox för antal månader för Sharpe Ratio
        months_sharpe_spinbox = QSpinBox()
        months_sharpe_spinbox.setFont(label_normal_font)
        months_sharpe_spinbox.setRange(1, 24)
        months_sharpe_spinbox.setValue(self.db.get_setting("sharpe_ratio_months") or 6)

        # QSpinBox för riskfri avkastning
        risk_free_rate_spinbox = QSpinBox()
        risk_free_rate_spinbox.setFont(label_normal_font)
        risk_free_rate_spinbox.setRange(0, 100)
        risk_free_rate_spinbox.setSingleStep(1)
        risk_free_rate_spinbox.setValue(self.db.get_setting("risk_free_rate") or 2)

        # QSpinBox för startkapital vid testköp
        start_capital_spinbox = QSpinBox()
        start_capital_spinbox.setFont(label_normal_font)
        start_capital_spinbox.setRange(1000, 1000000)  # Min 1000 SEK, max 1 miljon
        start_capital_spinbox.setSingleStep(500)
        start_capital_spinbox.setValue(self.db.get_setting("start_capital") or 10000)

        # Lägg till widgets i layouten
        layout.addWidget(label1, 0, 0)
        layout.addWidget(months_history_spinbox, 0, 1)

        layout.addWidget(label2, 1, 0)
        layout.addWidget(months_sharpe_spinbox, 1, 1)

        layout.addWidget(label3, 2, 0)
        layout.addWidget(risk_free_rate_spinbox, 2, 1)

        layout.addWidget(label4, 3, 0)  # Ny rad för startkapital
        layout.addWidget(start_capital_spinbox, 3, 1)

        # Lägg till ROC-period och ROC-threshold till layouten
        layout.addWidget(label5, 4, 0)
        layout.addWidget(roc_period_spinbox, 4, 1)

        layout.addWidget(label6, 5, 0)
        layout.addWidget(roc_threshold_spinbox, 5, 1)

        # Funktioner för att spara ändringar i databasen
        months_history_spinbox.valueChanged.connect(lambda value: self.db.set_setting("history", value))
        months_sharpe_spinbox.valueChanged.connect(lambda value: self.db.set_setting("sharpe_ratio_months", value))
        risk_free_rate_spinbox.valueChanged.connect(lambda value: self.db.set_setting("risk_free_rate", value))
        start_capital_spinbox.valueChanged.connect(lambda value: self.db.set_setting("start_capital", value))
        roc_period_spinbox.valueChanged.connect(lambda value: self.db.set_setting("roc_period", value))
        roc_threshold_spinbox.valueChanged.connect(lambda value: self.db.set_setting("roc_threshold", value))

        self.setCentralWidget(central_widget)

    def show_stock_info(self):
        variance = 0.0
        sharpe_ratio = 0
        if not self.selected_stock:
            return

        # Hämta historik enligt inställningarna
        history = self.db.get_stock_history(self.selected_stock, self.db.get_setting("history"))

        if not history:
            stock_info_text = f"Aktie: {self.selected_stock}\n\nIngen data för de senaste X månaderna."
        else:
            # Kontrollera strukturen på 'history' och extrahera priser och volymer korrekt
            try:
                prices = [price for _, price, _ in history]  # Om history är tuples (datum, pris, volym)
                volumes = [volume for _, _, volume in history]  # Om history innehåller volym
            except ValueError:
                # Om history inte har 3 kolumner
                prices = [price for _, price in history]  # Första kolumnen är datum, andra är pris
                volumes = [0] * len(prices)  # Sätt volym till 0 om ingen volym finns i historiken

            # Beräkna variansen
            variance = np.var(prices, ddof=1) if len(prices) > 1 else 0

            # Beräkna den totala volymen för de senaste 6 månaderna
            total_volume = sum(volumes)

            # Beräkna sharpe ratio
            sharpe_ratio = self.calculate_sharpe_ratio_from_price(prices, 0.01 * self.db.get_setting('risk_free_rate'),
                                                                  self.db.get_setting('sharpe_ratio_months'))

            # Formatera texten för att visa både varians och total volym
            stock_info_text = f"Aktie: {self.selected_stock}\n\n"
            stock_info_text += f"Varians (senaste X månaderna): {variance:.2f}\n"
            stock_info_text += f"Total Volym (senaste X månaderna): {total_volume}\n"
            stock_info_text += f"Sharpe Ratio (baserat på pris): {sharpe_ratio:.2f}"

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
        label5 = QLabel("Sharpe ratio:  ")
        label5.setFont(label_title_font)
        label6 = QLabel(str(format(sharpe_ratio, ".2f")))
        label6.setFont(label_normal_font)

        # Lägg till etiketter och värden i grid-layouten
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
            history = self.db.get_stock_history(self.selected_stock, self.db.get_setting('history'))
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
        history = self.db.get_stock_history(self.selected_stock, self.db.get_setting('history'))
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
                    print("Rubrikrad identifierad och hoppas över.")

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

    def calculate_sharpe_ratio_from_price(self, prices, risk_free_rate=0.02, months=6):
        """
        Beräknar Sharpe Ratio baserat på aktiens prisdata för de senaste 'months' månaderna.

        :param prices: Lista med pris (eller tuples med datum och pris).
        :param risk_free_rate: Den riskfria räntan (t.ex. avkastning på statsobligationer). Standard är 0.
        :param months: Antal månader bakåt som används för att beräkna Sharpe Ratio.

        :return: Sharpe Ratio
        """
        # Om prices är en lista av tuples (datum, pris), extrahera priserna och datumen
        if isinstance(prices[0], tuple):
            dates = [datetime.strptime(date, "%Y-%m-%d") for date, _ in prices]
            prices = [price for _, price in prices]
        else:
            dates = [None] * len(prices)  # Om inga datum ges, använd en lista med None

        # Omvandla prislistan till en Pandas DataFrame
        df = pd.DataFrame({"Date": dates, "Price": prices})

        # Om datum inte finns, anta att priserna är i ordning utan specifika datum
        if df["Date"].isnull().all():
            # Om inget datum finns, använd bara de senaste priserna
            df = df.tail(months * 30)  # Ungefärligt 30 dagar per månad

        else:
            # Filtrera ut de senaste 'months' månaderna från datan
            end_date = df["Date"].max()
            start_date = end_date - pd.DateOffset(months=months)
            df = df[df["Date"] >= start_date]

        # Om data inte finns för den angivna tidsramen, returnera None
        if df.empty:
            return None

        # Beräkna daglig avkastning: (pris idag - pris igår) / pris igår
        df["Return"] = df["Price"].pct_change()

        # Ta bort den första raden eftersom avkastningen är NaN där
        df = df.dropna(subset=["Return"])

        # Beräkna genomsnittlig daglig avkastning
        avg_return = df["Return"].mean()

        # Beräkna standardavvikelse (volatilitet) för den dagliga avkastningen
        return_volatility = df["Return"].std()

        # Beräkna Sharpe Ratio
        sharpe_ratio = (avg_return - risk_free_rate) / return_volatility

        return sharpe_ratio

    def apply_technical_analysis(self, technical_analysis_option):
        if not self.selected_stock:
            print("Ingen aktie vald!")
            return
        history = self.db.get_stock_history(self.selected_stock, self.db.get_setting('history'))
        if not history:
            print(f"Ingen historik hittades för {self.selected_stock}.")
            return
        if technical_analysis_option == "SMA":
            strategy = SMAStrategy()
            strategy.execute(self.selected_stock, history, self.db.get_setting('start_capital') or 10000)
        elif technical_analysis_option == "EMA":
            strategy = EMAStrategy()
            strategy.execute(self.selected_stock, history, self.db.get_setting('start_capital') or 10000)
        elif technical_analysis_option == "ROC":
            strategy = ROCStrategy()
            strategy.execute(self.selected_stock, history, self.db.get_setting('start_capital') or 10000, self.db.get_setting('roc_period') or 14, self.db.get_setting('roc_threshold') or 1)
        elif technical_analysis_option == "OBV":
            strategy = OBVStrategy()
            strategy.execute(self.selected_stock, history)
        elif technical_analysis_option == "FIBONACCI_RETRACEMENT":
            strategy = FibonacciStrategy()
            strategy.execute(self.selected_stock, history)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockAnalyzer()
    window.show()
    sys.exit(app.exec())