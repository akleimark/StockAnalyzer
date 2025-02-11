import pandas as pd
from matplotlib import pyplot as plt
from Strategy import TradingStrategy

class ROCStrategy(TradingStrategy):
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

    def execute(self, stock_name, history, start_value=10000, period=14, roc_threshold=1):
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
                #if price > entry_price:
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