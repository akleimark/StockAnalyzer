import matplotlib.pyplot as plt
import pandas as pd

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
