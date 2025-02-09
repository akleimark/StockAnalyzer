#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class TechnicalAnalyzer:
    def apply_moving_average_strategy(self, stock_name, stock_data, start_value=10000, window_size=20):
        if not stock_data or len(stock_data) < window_size:
            print("För lite data för att beräkna SMA.")
            return

        df = pd.DataFrame(stock_data, columns=["Date", "Price", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        df["SMA"] = df["Price"].rolling(window=window_size).mean()

        buy_signals = []
        sell_signals = []
        prev_price, prev_sma = None, None

        shares_held = 0  # Antal aktier vi äger
        total_profit = 0
        total_percentage_profit = 0
        num_trades = 0
        holding = False
        entry_price = 0

        # Gå igenom alla rader för att hitta köp- och säljsignaler
        for i in range(len(df)):
            if pd.isna(df.loc[i, "SMA"]):
                continue

            price, sma = df.loc[i, "Price"], df.loc[i, "SMA"]

            # Kontrollera köp- och säljsignaler
            if prev_price is not None and prev_sma is not None:
                # 🔹 Köp-signal: Investera hela start_value
                if prev_price < prev_sma and price > sma and not holding:
                    shares_held = start_value // price  # Beräkna antal aktier
                    if shares_held > 0:
                        buy_signals.append((df.loc[i, "Date"], price, shares_held))
                        holding = True
                        entry_price = price
                        print(
                            f"📈 Köp-signal: {df.loc[i, 'Date'].strftime('%Y-%m-%d')} - Köp {shares_held} aktier till {price:.2f} SEK")

                # 🔹 Sälj-signal: Sälj endast om priset är högre än inköpspriset
                elif prev_price > prev_sma and price < sma and holding and price > entry_price:
                    sell_signals.append((df.loc[i, "Date"], price, shares_held))
                    profit = shares_held * (price - entry_price)
                    percentage_profit = (profit / (shares_held * entry_price)) * 100

                    total_profit += profit
                    total_percentage_profit += percentage_profit
                    num_trades += 1  # Räkna en affär (köp + försäljning som en affär)
                    holding = False
                    print(
                        f"📉 Sälj-signal: {df.loc[i, 'Date'].strftime('%Y-%m-%d')} - Sålt {shares_held} aktier till {price:.2f} SEK - Vinst: {profit:.2f} SEK")

                    shares_held = 0  # Säljer alla aktier, återställ till 0

            prev_price, prev_sma = price, sma

        print(f"\n📊 Totalt antal affärer: {num_trades}")
        print(f"💵 Totalt resultat: {total_profit:.2f} SEK")
        print(f"📈 Total procentuell avkastning: {total_percentage_profit:.2f}%")

        # 🔹 Visualisering
        plt.figure(figsize=(12, 6))
        plt.plot(df["Date"], df["Price"], marker="o", linestyle="-", label=f"{stock_name} Pris", color="blue")
        plt.plot(df["Date"], df["SMA"], linestyle="--", label=f"{window_size}-dagars SMA", color="red")

        for date, price, shares in buy_signals:
            plt.scatter(date, price, color="green", marker="^", s=150, edgecolors="black", linewidth=1.5,
                        label="Köp" if "Köp" not in plt.gca().get_legend_handles_labels()[1] else "")

        for date, price, shares in sell_signals:
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

    def apply_ema_strategy(self, stock_name, history, start_value=10000, period=20):
        """
        Plottar prisutvecklingen och EMA för en aktie med köp- och säljsignaler.
        Skriver även ut signalerna i konsolen i samma format som SMA.
        :param stock_name: Namnet på aktien.
        :param history: Lista av tuples (datum, pris, volym).
        :param period: EMA-period.
        :param start_value: Startvärde för investering.
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

        shares_held = 0  # Antal aktier vi äger
        total_profit = 0
        total_percentage_profit = 0
        num_trades = 0
        holding = False
        entry_price = 0

        prev_price, prev_ema = None, None
        for i in range(len(df)):
            if pd.isna(df.loc[i, "EMA"]):
                continue  # Hoppa över perioder där EMA ej beräknats

            price, ema = df.loc[i, "Price"], df.loc[i, "EMA"]

            if prev_price is not None and prev_ema is not None:
                # 🔹 Köp-signal: Investera hela start_value
                if prev_price < prev_ema and price > ema and not holding:
                    shares_held = start_value // price  # Beräkna antal aktier
                    if shares_held > 0:
                        buy_signals.append((df.loc[i, "Date"], price, shares_held))
                        holding = True
                        entry_price = price
                        print(
                            f"📈 Köp-signal: {df.loc[i, 'Date'].strftime('%Y-%m-%d')} - Köp {shares_held} aktier till {price:.2f} SEK")

                # 🔹 Sälj-signal: Sälj endast om priset är högre än inköpspriset
                elif prev_price > prev_ema and price < ema and holding and price > entry_price:
                    sell_signals.append((df.loc[i, "Date"], price, shares_held))
                    profit = shares_held * (price - entry_price)
                    percentage_profit = (profit / (shares_held * entry_price)) * 100

                    total_profit += profit
                    total_percentage_profit += percentage_profit
                    num_trades += 1  # Räkna en affär (köp + försäljning som en affär)
                    holding = False
                    print(
                        f"📉 Sälj-signal: {df.loc[i, 'Date'].strftime('%Y-%m-%d')} - Sålt {shares_held} aktier till {price:.2f} SEK - Vinst: {profit:.2f} SEK")

                    shares_held = 0  # Säljer alla aktier, återställ till 0

            prev_price, prev_ema = price, ema

        print(f"\n📊 Totalt antal affärer: {num_trades}")
        print(f"💵 Totalt resultat: {total_profit:.2f} SEK")
        print(f"📈 Total procentuell avkastning: {total_percentage_profit:.2f}%")

        # Plotta grafen
        plt.figure(figsize=(10, 5))
        plt.plot(df["Date"], df["Price"], marker='o', linestyle='-', color='b', label="Pris")
        plt.plot(df["Date"], df["EMA"], linestyle='-', color='r', label=f"EMA ({period} dagar)")

        # Markera köp- och säljsignaler i grafen
        for date, price, shares in buy_signals:
            plt.scatter(date, price, marker='^', color='g', s=100, edgecolors="black", linewidth=1.5,
                        label="Köp" if "Köp" not in plt.gca().get_legend_handles_labels()[1] else "")

        for date, price, shares in sell_signals:
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

    def apply_roc_strategy(self, stock_name, history, start_value=10000, period=14, roc_threshold=1):
        """
        Plottar ROC och identifierar köp-/säljsignaler baserat på ROC och gör testköp samt beräknar vinst.
        :param stock_name: Namnet på aktien.
        :param history: Lista av tuples (datum, pris, volym).
        :param period: ROC-period (standard 14 dagar).
        :param start_value: Startvärde för investering.
        :param roc_threshold: Tröskelvärde för ROC (standard 5).
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

        shares_held = 0  # Antal aktier vi äger
        total_profit = 0
        total_percentage_profit = 0
        num_trades = 0
        holding = False
        entry_price = 0

        # Identifiera köp- och säljsignaler baserat på ROC och tröskelvärde
        for i in range(1, len(roc_values)):
            if pd.isna(roc_values[i]):
                continue  # Hoppa över periodens första värden (som är NaN)

            price = prices.iloc[i]
            roc = roc_values[i]

            # 🔹 Köp-signal: När ROC är under -roc_threshold och vi inte redan har aktier
            if roc < -roc_threshold and not holding:
                shares_held = start_value // price  # Beräkna antal aktier
                if shares_held > 0:
                    buy_signals.append((dates.iloc[i], price, shares_held))
                    holding = True
                    entry_price = price
                    print(
                        f"📈 Köp-signal: {dates.iloc[i].strftime('%Y-%m-%d')} - Köp {shares_held} aktier till {price:.2f} SEK")

            # 🔹 Sälj-signal: När ROC är över roc_threshold och vi håller aktier
            elif roc > roc_threshold and holding:
                # Sälj endast om priset är högre än inköpspriset (vinstdiskriminering)
                if price > entry_price:
                    sell_signals.append((dates.iloc[i], price, shares_held))
                    profit = shares_held * (price - entry_price)
                    percentage_profit = (profit / (shares_held * entry_price)) * 100

                    total_profit += profit
                    total_percentage_profit += percentage_profit
                    num_trades += 1  # Räkna en affär (köp + försäljning som en affär)
                    holding = False
                    print(
                        f"📉 Sälj-signal: {dates.iloc[i].strftime('%Y-%m-%d')} - Sålt {shares_held} aktier till {price:.2f} SEK - Vinst: {profit:.2f} SEK")

                    shares_held = 0  # Säljer alla aktier, återställ till 0

        print(f"\n📊 Totalt antal affärer: {num_trades}")
        print(f"💵 Totalt resultat: {total_profit:.2f} SEK")
        print(f"📈 Total procentuell avkastning: {total_percentage_profit:.2f}%")

        # Plotta ROC och köp-/säljsignaler
        plt.figure(figsize=(10, 6))
        plt.plot(dates, roc_values, label="ROC", color="blue")

        # Markera köp och säljsignaler
        buy_dates, buy_prices = zip(*[(d, p) for d, p, _ in buy_signals]) if buy_signals else ([], [])
        sell_dates, sell_prices = zip(*[(d, p) for d, p, _ in sell_signals]) if sell_signals else ([], [])
        plt.scatter(buy_dates, buy_prices, marker="^", color="green", label="Köp Signal")
        plt.scatter(sell_dates, sell_prices, marker="v", color="red", label="Sälj Signal")

        plt.title(f"ROC för {stock_name}")
        plt.xlabel("Datum")
        plt.ylabel("ROC (%)")
        plt.legend()
        plt.grid(True)
        plt.show()

    def apply_obv_strategy(self, stock_name, history, obv_ema_period=20, start_capital=10000):
        if not history or len(history) < obv_ema_period:
            print("Otillräckligt med data för OBV-beräkning.")
            return

        df = pd.DataFrame(history, columns=["Date", "Price", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        df["OBV_Change"] = df["Volume"] * df["Price"].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        df["OBV"] = df["OBV_Change"].cumsum().fillna(0)
        df["OBV_EMA"] = df["OBV"].ewm(span=obv_ema_period, adjust=False).mean()

        df["Signal"] = 0
        df.loc[df["OBV"] > df["OBV_EMA"], "Signal"] = 1
        df.loc[df["OBV"] < df["OBV_EMA"], "Signal"] = -1
        df["Signal_Change"] = df["Signal"].diff()

        buy_signals = df[df["Signal_Change"] == 2][["Date", "Price"]].to_numpy().tolist()
        sell_signals = df[df["Signal_Change"] == -2][["Date", "Price"]].to_numpy().tolist()

        num_trades = 0
        total_profit = 0
        trade_logs = []
        holding = None

        buy_index = 0
        sell_index = 0

        while buy_index < len(buy_signals) and sell_index < len(sell_signals):
            buy_date, buy_price = buy_signals[buy_index]
            sell_date, sell_price = sell_signals[sell_index]

            # Om en sälj-signal kommer före första köp-signalen, ignorera den
            if sell_date < buy_date:
                sell_index += 1
                continue

            # Genomför köp om vi inte redan har en position
            if holding is None:
                num_shares = start_capital // buy_price
                holding = (buy_date, buy_price, num_shares)
                trade_logs.append(
                    f"📈 Köp-signal: {buy_date.strftime('%Y-%m-%d')} - Köp {num_shares:.1f} aktier till {buy_price:.2f} SEK")
                buy_index += 1  # Flytta till nästa köp-signal
            else:
                _, entry_price, num_shares = holding
                profit = (sell_price - entry_price) * num_shares

                # Sälj endast om vi gör vinst
                if profit > 0:
                    total_profit += profit
                    num_trades += 1
                    trade_logs.append(
                        f"📉 Sälj-signal: {sell_date.strftime('%Y-%m-%d')} - Sålt {num_shares:.1f} aktier till {sell_price:.2f} SEK - Vinst: {profit:.2f} SEK")
                    holding = None  # Nollställ innehavet
                    sell_index += 1  # Flytta till nästa sälj-signal
                else:
                    # Om säljpriset inte ger vinst, gå vidare till nästa sälj-signal
                    sell_index += 1

            # Säkerställ att vi går vidare i loopen
            if buy_index >= len(buy_signals) or sell_index >= len(sell_signals):
                break

        for log in trade_logs:
            print(log)

        # Plotta pris och köp-/säljsignaler
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(df["Date"], df["Price"], label="Pris", color="blue", linewidth=2)
        ax1.scatter(*zip(*buy_signals) if buy_signals else ([], []), marker="^", color="green", label="Köp-signal",
                    s=100)
        ax1.scatter(*zip(*sell_signals) if sell_signals else ([], []), marker="v", color="red", label="Sälj-signal",
                    s=100)

        ax1.set_xlabel("Datum")
        ax1.set_ylabel("Pris (SEK)")
        ax1.legend()
        ax1.grid()

        ax2 = ax1.twinx()
        ax2.plot(df["Date"], df["OBV"], label="OBV", color="purple", alpha=0.6, linestyle="dashed")
        ax2.plot(df["Date"], df["OBV_EMA"], label=f"OBV EMA {obv_ema_period}", color="orange", linestyle="solid")
        ax2.set_ylabel("OBV")
        ax2.legend(loc="upper left")

        plt.title(f"OBV-strategi för {stock_name}")
        plt.xticks(rotation=45)
        plt.show()

        total_percentage_profit = (total_profit / start_capital) * 100 if start_capital else 0

        print(f"\n📊 Totalt antal affärer: {num_trades}")
        print(f"💵 Totalt resultat: {total_profit:.2f} SEK")
        print(f"📈 Total procentuell avkastning: {total_percentage_profit:.2f}%\n")