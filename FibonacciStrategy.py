import pandas as pd
from matplotlib import pyplot as plt
from Strategy import TradingStrategy

class FibonacciStrategy(TradingStrategy):
    def execute(self, stock_name, stock_data, start_value=10000):
        if not stock_data or len(stock_data) < 2:
            print("För lite data för att beräkna Fibonacci retracement.")
            return

        df = pd.DataFrame(stock_data, columns=["Date", "Price", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        # 🔹 Hitta senaste trendens högsta och lägsta pris
        highest_price = df["Price"].max()
        lowest_price = df["Price"].min()

        # 🔹 Beräkna Fibonacci retracement-nivåer
        fib_levels = {
            "0.0%": highest_price,
            "23.6%": highest_price - (0.236 * (highest_price - lowest_price)),
            "38.2%": highest_price - (0.382 * (highest_price - lowest_price)),
            "50.0%": highest_price - (0.50 * (highest_price - lowest_price)),
            "61.8%": highest_price - (0.618 * (highest_price - lowest_price)),
            "78.6%": highest_price - (0.786 * (highest_price - lowest_price)),
            "100.0%": lowest_price
        }

        buy_signals = []
        sell_signals = []
        holding = False
        entry_price = 0
        total_profit = 0
        num_trades = 0
        shares_held = 0

        # 🔹 Loopar genom data för att hitta köp- och säljsignaler
        for i in range(len(df)):
            price = df.loc[i, "Price"]
            date = df.loc[i, "Date"]

            # Köp om priset når 61.8% eller 78.6% retracement (stöd)
            if price <= fib_levels["61.8%"] and not holding:
                shares_held = start_value // price
                if shares_held > 0:
                    buy_signals.append((date, price, shares_held))
                    holding = True
                    entry_price = price
                    print(f"📈 Köp-signal: {date.strftime('%Y-%m-%d')} - Köp {shares_held} aktier till {price:.2f} SEK")

            # Sälj om priset når 38.2% eller 23.6% retracement (motstånd)
            elif price >= fib_levels["38.2%"] and holding:
                sell_signals.append((date, price, shares_held))
                profit = shares_held * (price - entry_price)
                total_profit += profit
                num_trades += 1
                holding = False
                print(
                    f"📉 Sälj-signal: {date.strftime('%Y-%m-%d')} - Sålt {shares_held} aktier till {price:.2f} SEK - Vinst: {profit:.2f} SEK")
                shares_held = 0

        print(f"\n📊 Totalt antal affärer: {num_trades}")
        print(f"💵 Totalt resultat: {total_profit:.2f} SEK")

        # 🔹 Visualisering
        plt.figure(figsize=(12, 6))
        plt.plot(df["Date"], df["Price"], label="Pris", color="blue")

        for level, value in fib_levels.items():
            plt.axhline(y=value, linestyle="--", label=f"Fib {level}: {value:.2f} SEK", alpha=0.6)

        for date, price, _ in buy_signals:
            plt.scatter(date, price, color="green", marker="^", s=150, edgecolors="black", linewidth=1.5,
                        label="Köp" if "Köp" not in plt.gca().get_legend_handles_labels()[1] else "")

        for date, price, _ in sell_signals:
            plt.scatter(date, price, color="red", marker="v", s=150, edgecolors="black", linewidth=1.5,
                        label="Sälj" if "Sälj" not in plt.gca().get_legend_handles_labels()[1] else "")

        plt.xlabel("Datum")
        plt.ylabel("Pris (SEK)")
        plt.title(f"Fibonacci retracement för {stock_name}")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.xticks(rotation=45)
        plt.show()
