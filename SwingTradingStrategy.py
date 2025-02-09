import pandas as pd
import matplotlib.pyplot as plt


class SwingTradingStrategy:
    def __init__(self, history, short_sma=20, long_sma=50, rsi_period=14, start_capital=10000, stop_loss_pct=20, take_profit_pct=20):
        self.df = pd.DataFrame(history, columns=["Date", "Price", "Volume"])
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df = self.df.sort_values("Date")
        self.short_sma = short_sma
        self.long_sma = long_sma
        self.rsi_period = rsi_period
        self.start_capital = start_capital
        self.stop_loss_pct = stop_loss_pct  # Stop-loss som en procentandel
        self.take_profit_pct = take_profit_pct  # Take-profit som en procentandel
        self.trades = []

    def calculate_indicators(self):
        # SMA
        self.df["SMA_short"] = self.df["Price"].rolling(self.short_sma).mean()
        self.df["SMA_long"] = self.df["Price"].rolling(self.long_sma).mean()

        # RSI
        delta = self.df["Price"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
        rs = gain / loss
        self.df["RSI"] = 100 - (100 / (1 + rs))

    def apply_strategy(self):
        holding = None
        total_profit = 0
        num_trades = 0

        for i in range(len(self.df)):
            row = self.df.iloc[i]

            # Köp-signal (Swing Entry) - Kontrollera om vi redan har ett innehav
            if holding is None and (row["SMA_short"] > row["SMA_long"] and row["RSI"] < 50):
                num_shares = self.start_capital // row["Price"]
                holding = (row["Date"], row["Price"], num_shares)  # Starta en ny position
                self.trades.append(
                    f"📈 Köp-signal: {row['Date'].strftime('%Y-%m-%d')} - Köp {num_shares:.1f} aktier till {row['Price']:.2f} SEK")

            # Kontrollera om stop-loss eller take-profit ska triggas
            elif holding is not None:
                buy_date, buy_price, num_shares = holding
                stop_loss_price = buy_price * (1 - self.stop_loss_pct / 100)
                take_profit_price = buy_price * (1 + self.take_profit_pct / 100)

                if row["Price"] <= stop_loss_price:  # Stop-loss triggas
                    profit = (row["Price"] - buy_price) * num_shares
                    total_profit += profit
                    num_trades += 1
                    self.trades.append(
                        f"📉 Stop-loss: {row['Date'].strftime('%Y-%m-%d')} - Sålt {num_shares:.1f} aktier till {row['Price']:.2f} SEK - Förlust: {profit:.2f} SEK")
                    holding = None  # Nollställ innehavet efter försäljning

                elif row["Price"] >= take_profit_price:  # Take-profit triggas
                    profit = (row["Price"] - buy_price) * num_shares
                    total_profit += profit
                    num_trades += 1
                    self.trades.append(
                        f"📈 Take-profit: {row['Date'].strftime('%Y-%m-%d')} - Sålt {num_shares:.1f} aktier till {row['Price']:.2f} SEK - Vinst: {profit:.2f} SEK")
                    holding = None  # Nollställ innehavet efter försäljning

            # Sälj-signal (Swing Exit) utan stop-loss eller take-profit
            if holding is not None and (row["SMA_short"] < row["SMA_long"] or row["RSI"] > 70):
                buy_date, buy_price, num_shares = holding
                if row["Price"] > buy_price:  # Sälj endast om vi är i vinst
                    profit = (row["Price"] - buy_price) * num_shares
                    total_profit += profit
                    num_trades += 1
                    self.trades.append(
                        f"📉 Sälj-signal: {row['Date'].strftime('%Y-%m-%d')} - Sålt {num_shares:.1f} aktier till {row['Price']:.2f} SEK - Vinst: {profit:.2f} SEK")
                    holding = None  # Nollställ innehavet efter försäljning
                else:
                    self.trades.append(f"❌ Sälj-signal: {row['Date'].strftime('%Y-%m-%d')} - Ingen försäljning eftersom vi är i förlust.")
                    # Håll kvar positionen om vi är i förlust

        # Summera resultat
        total_percentage_profit = (total_profit / self.start_capital) * 100
        self.trades.append(f"\n📊 Totalt antal affärer: {num_trades}")
        self.trades.append(f"💵 Totalt resultat: {total_profit:.2f} SEK")
        self.trades.append(f"📈 Total procentuell avkastning: {total_percentage_profit:.2f}%")

    def plot_results(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.df["Date"], self.df["Price"], label="Pris", color="blue")
        plt.plot(self.df["Date"], self.df["SMA_short"], label=f"SMA {self.short_sma}", color="green")
        plt.plot(self.df["Date"], self.df["SMA_long"], label=f"SMA {self.long_sma}", color="red")
        plt.legend()
        plt.title("Swing Trading Strategi med Stop-Loss och Take-Profit")
        plt.xlabel("Datum")
        plt.ylabel("Pris")
        plt.grid()
        plt.xticks(rotation=45)
        plt.show()

    def run(self):
        self.calculate_indicators()
        self.apply_strategy()
        self.plot_results()
        for trade in self.trades:
            print(trade)

# Exempelanrop:
# strategy = SwingTradingStrategy(history_data)
# strategy.run()
