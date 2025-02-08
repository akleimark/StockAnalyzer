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

        df = pd.DataFrame(stock_data, columns=["Date", "Price"])
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
            plt.scatter(date, price, color="green", marker="^", s=150, edgecolors="black", linewidth=1.5, label="Köp" if "Köp" not in plt.gca().get_legend_handles_labels()[1] else "" )

        for date, price in sell_signals:
            plt.scatter(date, price, color="red", marker="v", s=150, edgecolors="black", linewidth=1.5, label="Sälj" if "Sälj" not in plt.gca().get_legend_handles_labels()[1] else "")

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
        :param history: Lista av tuples (datum, pris).
        :param period: EMA-period.
        """

        if not history or len(history) < period:
            print("Otillräckligt med data för EMA-beräkning.")
            return

        dates = [datetime.strptime(date, "%Y-%m-%d").date() for date, _ in history]
        prices = [price for _, price in history]

        ema_values = self.calculate_ema(prices, period)

        buy_signals = []
        sell_signals = []

        # Identifiera köp- och säljsignaler
        for i in range(1, len(prices)):
            if ema_values[i] is None:
                continue  # Hoppa över perioder där EMA ej beräknats

            prev_price = prices[i - 1]
            prev_ema = ema_values[i - 1] if ema_values[i - 1] is not None else prev_price
            curr_price = prices[i]
            curr_ema = ema_values[i]

            if prev_price < prev_ema and curr_price > curr_ema:
                buy_signals.append((dates[i], curr_price))  # Köp

            elif prev_price > prev_ema and curr_price < curr_ema:
                sell_signals.append((dates[i], curr_price))  # Sälj

        # Skriv ut signalerna på samma sätt som i SMA
        print(f"\n📈 Köp-signaler för {stock_name}:")
        for date, price in buy_signals:
            print(f"   - {date.strftime('%Y-%m-%d')} till pris {price:.2f} SEK")

        print(f"\n📉 Sälj-signaler för {stock_name}:")
        for date, price in sell_signals:
            print(f"   - {date.strftime('%Y-%m-%d')} till pris {price:.2f} SEK")

        # Plotta grafen
        plt.figure(figsize=(10, 5))
        plt.plot(dates, prices, marker='o', linestyle='-', color='b', label="Pris")
        plt.plot(dates, ema_values, linestyle='-', color='r', label=f"EMA ({period} dagar)")

        # Markera köp- och säljsignaler i grafen
        buy_dates, buy_prices = zip(*buy_signals) if buy_signals else ([], [])
        sell_dates, sell_prices = zip(*sell_signals) if sell_signals else ([], [])

        plt.scatter(buy_dates, buy_prices, marker='^', color='g', label="Köp", s=100)
        plt.scatter(sell_dates, sell_prices, marker='v', color='r', label="Sälj", s=100)

        # Anpassa utseendet
        plt.xlabel("Datum")
        plt.ylabel("Pris (SEK)")
        plt.title(f"{stock_name} - EMA ({period} dagar) med köp-/säljsignaler")
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.show()