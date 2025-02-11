import pandas as pd
from matplotlib import pyplot as plt
from Strategy import TradingStrategy

class SMAStrategy(TradingStrategy):
    def execute(self, stock_name, stock_data, start_value=10000, window_size=20):
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

                #  Sälj-signal: Sälj endast om priset är högre än inköpspriset
                #elif prev_price > prev_sma and price < sma and holding and price > entry_price:
                elif prev_price > prev_sma and price < sma and holding:
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

        #  Visualisering
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
