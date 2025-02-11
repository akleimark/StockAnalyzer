import pandas as pd
from matplotlib import pyplot as plt
from Strategy import TradingStrategy

class OBVStrategy(TradingStrategy):
    def execute(self, stock_name, history, obv_ema_period=20, start_capital=10000):
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
                #if profit > 0:
                total_profit += profit
                num_trades += 1
                trade_logs.append(
                    f"📉 Sälj-signal: {sell_date.strftime('%Y-%m-%d')} - Sålt {num_shares:.1f} aktier till {sell_price:.2f} SEK - Vinst: {profit:.2f} SEK")
                holding = None  # Nollställ innehavet
                sell_index += 1  # Flytta till nästa sälj-signal
                #else:
                    # Om säljpriset inte ger vinst, gå vidare till nästa sälj-signal
                    #sell_index += 1

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
