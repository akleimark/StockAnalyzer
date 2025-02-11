import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from Strategy import TradingStrategy

class EMAStrategy(TradingStrategy):
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
    def execute(self, stock_name, history, start_value=10000, period=20):
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
                #elif prev_price > prev_ema and price < ema and holding and price > entry_price:
                elif prev_price > prev_ema and price < ema and holding:
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