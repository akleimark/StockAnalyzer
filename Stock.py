#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class TechnicalAnalyzer:
    def apply_moving_average_strategy(self, stock_name, stock_data, window_size=20):
        if not stock_data or len(stock_data) < window_size:
            print("För lite data för att beräkna SMA.")
            return

        # Anpassa dataframe till den nya strukturen
        df = pd.DataFrame(stock_data, columns=["Date", "Price", "Volume"])  # Inkludera volym men ignorera den för SMA
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        df["SMA"] = df["Price"].rolling(window=window_size).mean()

        buy_signals = []
        sell_signals = []
        prev_price, prev_sma = None, None

        for i in range(len(df)):
            if pd.isna(df.loc[i, "SMA"]):
                continue

            price, sma = df.loc[i, "Price"], df.loc[i, "SMA"]

            if prev_price is not None and prev_sma is not None:
                if prev_price < prev_sma and price > sma:
                    buy_signals.append((df.loc[i, "Date"], price))
                elif prev_price > prev_sma and price < sma:
                    sell_signals.append((df.loc[i, "Date"], price))

            prev_price, prev_sma = price, sma

        print(f"\n📈 Köp-signaler för {stock_name}:")
        for date, price in buy_signals:
            print(f"   - {date.strftime('%Y-%m-%d')} till pris {price:.2f} SEK")

        print(f"\n📉 Sälj-signaler för {stock_name}:")
        for date, price in sell_signals:
            print(f"   - {date.strftime('%Y-%m-%d')} till pris {price:.2f} SEK")

        plt.figure(figsize=(12, 6))
        plt.plot(df["Date"], df["Price"], marker="o", linestyle="-", label=f"{stock_name} Pris", color="blue")
        plt.plot(df["Date"], df["SMA"], linestyle="--", label=f"{window_size}-dagars SMA", color="red")

        # Markera köp- och säljsignaler
        for date, price in buy_signals:
            plt.scatter(date, price, color="green", marker="^", s=150, edgecolors="black", linewidth=1.5,
                        label="Köp" if "Köp" not in plt.gca().get_legend_handles_labels()[1] else "")

        for date, price in sell_signals:
            plt.scatter(date, price, color="red", marker="v", s=150, edgecolors="black", linewidth=1.5,
                        label="Sälj" if "Sälj" not in plt.gca().get_legend_handles_labels()[1] else "")

        plt.xlabel("Datum")
        plt.ylabel("Pris (SEK)")
        plt.title(f"Glidande medelvärde ({window_size}-dagar) för {stock_name}")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.xticks(rotation=45)

        plt.show()

    def calculate_ema(self, prices, period=20):
        """Beräknar EMA för en given period."""
        if len(prices) < period:
            print("För få datapunkter för att beräkna EMA.")
            return []

        ema_values = []
        alpha = 2 / (period + 1)

        # Startvärde: SMA för första "period" antal dagar
        sma = np.mean(prices[:period])
        ema_values.append(sma)

        # Beräkna EMA för resterande dagar
        for price in prices[period:]:
            new_ema = alpha * price + (1 - alpha) * ema_values[-1]
            ema_values.append(new_ema)

        return [None] * (period - 1) + ema_values  # Fyll upp första värden med None

    def apply_ema_strategy(self, stock_name, history, period=20):
        """
        Plottar prisutvecklingen och EMA för en aktie med köp- och säljsignaler.
        Skriver även ut signalerna i konsolen i samma format som SMA.
        :param stock_name: Namnet på aktien.
        :param history: Lista av tuples (datum, pris, volym).
        :param period: EMA-period.
        """

        if not history or len(history) < period:
            print("Otillräckligt med data för EMA-beräkning.")
            return

        # Hantera tre kolumner: (datum, pris, volym), men vi använder bara datum och pris
        df = pd.DataFrame(history, columns=["Date", "Price", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        df["EMA"] = self.calculate_ema(df["Price"], period)

        buy_signals = []
        sell_signals = []

        # Identifiera köp- och säljsignaler
        prev_price, prev_ema = None, None
        for i in range(len(df)):
            if pd.isna(df.loc[i, "EMA"]):
                continue  # Hoppa över perioder där EMA ej beräknats

            price, ema = df.loc[i, "Price"], df.loc[i, "EMA"]

            if prev_price is not None and prev_ema is not None:
                if prev_price < prev_ema and price > ema:
                    buy_signals.append((df.loc[i, "Date"], price))  # Köp

                elif prev_price > prev_ema and price < ema:
                    sell_signals.append((df.loc[i, "Date"], price))  # Sälj

            prev_price, prev_ema = price, ema

        # Skriv ut signalerna på samma sätt som i SMA
        print(f"\n📈 Köp-signaler för {stock_name}:")
        for date, price in buy_signals:
            print(f"   - {date.strftime('%Y-%m-%d')} till pris {price:.2f} SEK")

        print(f"\n📉 Sälj-signaler för {stock_name}:")
        for date, price in sell_signals:
            print(f"   - {date.strftime('%Y-%m-%d')} till pris {price:.2f} SEK")

        # Plotta grafen
        plt.figure(figsize=(10, 5))
        plt.plot(df["Date"], df["Price"], marker='o', linestyle='-', color='b', label="Pris")
        plt.plot(df["Date"], df["EMA"], linestyle='-', color='r', label=f"EMA ({period} dagar)")

        # Markera köp- och säljsignaler i grafen
        for date, price in buy_signals:
            plt.scatter(date, price, marker='^', color='g', s=100, edgecolors="black", linewidth=1.5,
                        label="Köp" if "Köp" not in plt.gca().get_legend_handles_labels()[1] else "")

        for date, price in sell_signals:
            plt.scatter(date, price, marker='v', color='r', s=100, edgecolors="black", linewidth=1.5,
                        label="Sälj" if "Sälj" not in plt.gca().get_legend_handles_labels()[1] else "")

        # Anpassa utseendet
        plt.xlabel("Datum")
        plt.ylabel("Pris (SEK)")
        plt.title(f"{stock_name} - EMA ({period} dagar) med köp-/säljsignaler")
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.show()

    def calculate_roc(self, prices, period=14):
        """
        Beräknar Rate of Change (ROC) för en given period.
        :param prices: Lista med prisdata.
        :param period: Antal perioder för att beräkna ROC (default: 14).
        :return: Lista med ROC-värden.
        """
        if len(prices) < period:
            print("Otillräckligt med data för ROC-beräkning.")
            return []

        roc_values = []
        for i in range(period, len(prices)):
            roc = ((prices[i] - prices[i - period]) / prices[i - period]) * 100
            roc_values.append(roc)

        # Fyller början med None för att matcha längden på priserna
        return [None] * period + roc_values

    def apply_roc_strategy(self, stock_name, history, period=14):
        """
        Plottar ROC och identifierar köp-/säljsignaler.
        :param stock_name: Namnet på aktien.
        :param history: Lista av tuples (datum, pris, volym).
        :param period: ROC-period (standard 14 dagar).
        """
        if not history or len(history) < period:
            print("Otillräckligt med data för ROC-beräkning.")
            return

        # Hantera tre kolumner: (datum, pris, volym), men vi använder bara datum och pris
        df = pd.DataFrame(history, columns=["Date", "Price", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        # Beräkna ROC
        df["ROC"] = self.calculate_roc(df["Price"], period)

        # Ta bort det sista värdet från dates och prices för att matcha längd på roc_values
        dates = df["Date"][:len(df["ROC"])]
        prices = df["Price"][:len(df["ROC"])]
        roc_values = df["ROC"]

        buy_signals = []
        sell_signals = []

        # Identifiera köp- och säljsignaler baserat på ROC
        for i in range(len(roc_values)):
            if pd.isna(roc_values[i]):
                continue  # Hoppa över periodens första värden (som är NaN)

            if roc_values[i] < 0:  # Köp när ROC < 0 (pris nedåt)
                buy_signals.append((dates.iloc[i], prices.iloc[i]))

            elif roc_values[i] > 0:  # Sälj när ROC > 0 (pris uppåt)
                sell_signals.append((dates.iloc[i], prices.iloc[i]))

        # Skriv ut köp- och säljsignaler
        if buy_signals:
            print(f"Köp-signaler för {stock_name}:")
            for date, price in buy_signals:
                print(f"  {date.strftime('%Y-%m-%d')}: {price:.2f} SEK")

        if sell_signals:
            print(f"Sälj-signaler för {stock_name}:")
            for date, price in sell_signals:
                print(f"  {date.strftime('%Y-%m-%d')}: {price:.2f} SEK")

        # Plotta ROC och köp-/säljsignaler
        plt.figure(figsize=(10, 6))
        plt.plot(dates, roc_values, label="ROC", color="blue")

        # Markera köp och säljsignaler
        buy_dates, buy_prices = zip(*buy_signals) if buy_signals else ([], [])
        sell_dates, sell_prices = zip(*sell_signals) if sell_signals else ([], [])
        plt.scatter(buy_dates, buy_prices, marker="^", color="green", label="Köp Signal")
        plt.scatter(sell_dates, sell_prices, marker="v", color="red", label="Sälj Signal")

        plt.title(f"ROC för {stock_name}")
        plt.xlabel("Datum")
        plt.ylabel("ROC (%)")
        plt.legend()
        plt.grid(True)
        plt.show()

    def apply_obv_strategy(self, stock_name, history):
        """
        Plottar OBV och identifierar köp-/säljsignaler baserat på OBV-strategi.
        :param stock_name: Namnet på aktien.
        :param history: Lista av tuples (datum, pris, volym).
        """
        if not history or len(history) < 2:
            print("Otillräckligt med data för OBV-beräkning.")
            return

        # Hantera tre kolumner: (datum, pris, volym)
        df = pd.DataFrame(history, columns=["Date", "Price", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        # Beräkna OBV
        df["OBV"] = 0
        for i in range(1, len(df)):
            if df["Price"].iloc[i] > df["Price"].iloc[i - 1]:  # Om priset stiger
                df["OBV"].iloc[i] = df["OBV"].iloc[i - 1] + df["Volume"].iloc[i]
            elif df["Price"].iloc[i] < df["Price"].iloc[i - 1]:  # Om priset faller
                df["OBV"].iloc[i] = df["OBV"].iloc[i - 1] - df["Volume"].iloc[i]
            else:  # Om priset är oförändrat
                df["OBV"].iloc[i] = df["OBV"].iloc[i - 1]

        # Identifiera köp- och säljsignaler baserat på OBV
        buy_signals = []
        sell_signals = []

        for i in range(1, len(df)):
            if df["OBV"].iloc[i] > df["OBV"].iloc[i - 1]:  # OBV ökar, köp-signal
                buy_signals.append((df["Date"].iloc[i], df["Price"].iloc[i]))
            elif df["OBV"].iloc[i] < df["OBV"].iloc[i - 1]:  # OBV minskar, sälj-signal
                sell_signals.append((df["Date"].iloc[i], df["Price"].iloc[i]))

        # Skriv ut köp- och säljsignaler
        if buy_signals:
            print(f"\n📈 Köp-signaler för {stock_name}:")
            for date, price in buy_signals:
                print(f"   - {date.strftime('%Y-%m-%d')} till pris {price:.2f} SEK")

        if sell_signals:
            print(f"\n📉 Sälj-signaler för {stock_name}:")
            for date, price in sell_signals:
                print(f"   - {date.strftime('%Y-%m-%d')} till pris {price:.2f} SEK")

        # Plotta OBV och köp-/säljsignaler
        plt.figure(figsize=(12, 6))
        plt.plot(df["Date"], df["OBV"], label="OBV", color="purple")

        # Markera köp och säljsignaler
        buy_dates, buy_prices = zip(*buy_signals) if buy_signals else ([], [])
        sell_dates, sell_prices = zip(*sell_signals) if sell_signals else ([], [])
        plt.scatter(buy_dates, buy_prices, marker="^", color="green", label="Köp-signal", s=100)
        plt.scatter(sell_dates, sell_prices, marker="v", color="red", label="Sälj-signal", s=100)

        # Anpassa utseendet
        plt.title(f"OBV för {stock_name}")
        plt.xlabel("Datum")
        plt.ylabel("OBV")
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.show()

