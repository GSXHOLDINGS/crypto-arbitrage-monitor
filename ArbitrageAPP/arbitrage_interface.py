import streamlit as st
import ccxt

# Binance API credentials
binance_api_key = "ijexv5wv8r3sapJVgnmXMOuTItL1O3QhlrRrhZNpYcZolkc3uMd2qtQL7WhFzVfH"
binance_secret_key = "MCMDVOQnrxyIDE7EgNvGhtcVKFUQ4aN5RVZiTN68YWxzk7YBATTZ63K5r7ES8gUg"

# KuCoin API credentials
kucoin_api_key = "678130113f01990001b50275"
kucoin_secret_key = "45bd9797-b191-4f54-8505-629637d18783"
kucoin_passphrase = "Hublot2013!"

# Initialize exchanges
binance = ccxt.binance({
    'apiKey': binance_api_key,
    'secret': binance_secret_key,
})
kucoin = ccxt.kucoin({
    'apiKey': kucoin_api_key,
    'secret': kucoin_secret_key,
    'password': kucoin_passphrase,
})

# Streamlit interface
st.title("Crypto Arbitrage Monitor")
st.write("Monitoring Binance and KuCoin for arbitrage opportunities (with fees).")

# Dropdown for selecting trading pairs
pairs = st.multiselect(
    "Select Trading Pairs to Monitor",
    ["XRP/USDT", "BTC/USDT", "ETH/USDT", "BNB/USDT"],
    default=["XRP/USDT"]
)

# Define trading fees
trading_fee = 0.001  # 0.1% trading fee per side

# Define withdrawal fees for each exchange and pair
withdrawal_fees = {
    "XRP/USDT": {"binance": 1, "kucoin": 0.5},  # Example: 1 XRP for Binance, 0.5 XRP for KuCoin
    "BTC/USDT": {"binance": 0.0005, "kucoin": 0.0004},
    "ETH/USDT": {"binance": 0.005, "kucoin": 0.004},
    "BNB/USDT": {"binance": 0.001, "kucoin": 0.001},
}

# Fetch and display arbitrage data
if pairs:
    st.subheader("Arbitrage Opportunities")
    for pair in pairs:
        try:
            # Fetch prices from Binance
            binance_ticker = binance.fetch_ticker(pair)
            binance_bid = binance_ticker['bid']
            binance_ask = binance_ticker['ask']

            # Fetch prices from KuCoin
            kucoin_ticker = kucoin.fetch_ticker(pair)
            kucoin_bid = kucoin_ticker['bid']
            kucoin_ask = kucoin_ticker['ask']

            # Calculate raw differences
            buy_binance_sell_kucoin = kucoin_bid - binance_ask
            buy_kucoin_sell_binance = binance_bid - kucoin_ask

            # Add withdrawal fees to calculations
            binance_withdrawal_fee = withdrawal_fees[pair]["binance"]
            kucoin_withdrawal_fee = withdrawal_fees[pair]["kucoin"]

            # Adjust net profits for trading and withdrawal fees
            net_profit_binance_to_kucoin = buy_binance_sell_kucoin - (
                binance_ask * trading_fee + kucoin_bid * trading_fee + binance_withdrawal_fee
            )
            net_profit_kucoin_to_binance = buy_kucoin_sell_binance - (
                kucoin_ask * trading_fee + binance_bid * trading_fee + kucoin_withdrawal_fee
            )

            # Display results for this pair
            st.write(f"### {pair}")
            st.write(f"Binance - Bid: {binance_bid}, Ask: {binance_ask}")
            st.write(f"KuCoin - Bid: {kucoin_bid}, Ask: {kucoin_ask}")
            st.write(f"Buy on Binance, Sell on KuCoin: {buy_binance_sell_kucoin:.6f}")
            st.write(f"Buy on KuCoin, Sell on Binance: {buy_kucoin_sell_binance:.6f}")

            # Highlight profitable trades
            if net_profit_binance_to_kucoin > 0:
                st.success(f"Net Profit (After Fees): {net_profit_binance_to_kucoin:.6f}")
            else:
                st.error(f"Net Profit (After Fees): {net_profit_binance_to_kucoin:.6f}")

            if net_profit_kucoin_to_binance > 0:
                st.success(f"Net Profit (After Fees): {net_profit_kucoin_to_binance:.6f}")
            else:
                st.error(f"Net Profit (After Fees): {net_profit_kucoin_to_binance:.6f}")

        except Exception as e:
            st.error(f"Error fetching data for {pair}: {e}")
            print(f"Error: {e}. CCXT Version: {ccxt.__version__}")
