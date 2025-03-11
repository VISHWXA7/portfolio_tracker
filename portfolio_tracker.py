import json
import time
import yfinance as yf
import requests

def calculate_weighted_price(old_price, old_quantity, new_price, new_quantity):
    if old_quantity == 0:
        return new_price
    return ((old_price * old_quantity) + (new_price * new_quantity)) / (old_quantity + new_quantity)

# **1. Fetch ETF Prices**
def fetch_etf_prices():
    etfs = ["VTI", "QQQM", "VXUS", "GOLDBEES.NS", "BTC-USD"]
    etf_holdings = []
    
    # Load existing data
    try:
        with open("portfolio.json", "r") as f:
            existing_data = json.load(f)
            etf_data = {x["Stock"]: x for x in existing_data.get("ETFs", [])}
    except (FileNotFoundError, json.JSONDecodeError):
        etf_data = {}

    # Process ETFs
    for ticker in etfs:
        try:
            etf = yf.Ticker(ticker)
            price = etf.history(period="1d")["Close"].iloc[-1]
            old_quantity = etf_data.get(ticker, {}).get("Quantity", 0)
            old_buy_price = etf_data.get(ticker, {}).get("Buy_Price", 0)
            new_buy_price = calculate_weighted_price(old_buy_price, old_quantity, price, old_quantity)
            total_value = price * old_quantity
            profit_loss = (price - new_buy_price) * old_quantity

            etf_holdings.append({
                "Stock": ticker,
                "Quantity": old_quantity,
                "Buy_Price": round(new_buy_price, 2),
                "Current_Price": round(price, 2),
                "Total_Value": round(total_value, 2),
                "Profit_Loss": round(profit_loss, 2)
            })
        except Exception as e:
            print(f"Error fetching {ticker} data: {e}")

    return etf_holdings

# **2. Fetch Mutual Fund NAV**
def fetch_mutual_fund_nav():
    fund_codes = {
        "INF789F01XA0": "UTI Nifty 50",
        "INF846K01K35": "Axis Smallcap",
        "INF247L01445": "Motilal Oswal Midcap"
    }
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    fund_data = []

    try:
        # Load existing portfolio.json or initialize an empty dict
        try:
            with open("portfolio.json", "r") as f:
                existing_data = json.load(f)
                mf_data = {x["Fund"]: x for x in existing_data.get("MutualFunds", [])}
        except (FileNotFoundError, json.JSONDecodeError):
            mf_data = {}

        response = requests.get(url, timeout=15)
        data = response.text.splitlines()

        for line in data:
            for code, name in fund_codes.items():
                if code in line:
                    fields = line.split(';')
                    if len(fields) >= 6:
                        try:
                            nav = float(fields[4])  # Extract NAV
                            old_quantity = mf_data.get(name, {}).get("Quantity", 0)
                            
                            if old_quantity == 0:
                                print(f"Skipping {name}: Quantity is 0")
                                continue

                            old_buy_price = mf_data.get(name, {}).get("Buy_Price", 0)
                            new_buy_price = calculate_weighted_price(old_buy_price, old_quantity, nav, old_quantity)
                            total_value = nav * old_quantity
                            profit_loss = (nav - new_buy_price) * old_quantity

                            fund_data.append({
                                "Fund": name,
                                "Quantity": old_quantity,
                                "Buy_Price": round(new_buy_price, 2),
                                "Current_NAV": round(nav, 2),
                                "Total_Value": round(total_value, 2),
                                "Profit_Loss": round(profit_loss, 2)
                            })
                        except ValueError:
                            print(f"Error parsing NAV for {name}")

        return fund_data
    except Exception as e:
        print(f"Error fetching mutual fund data: {e}")
        return []

# **3. Save Data to JSON**
def save_to_json():
    etf_holdings = fetch_etf_prices()
    mutual_funds = fetch_mutual_fund_nav()

    total_value = sum(x["Total_Value"] for x in etf_holdings) + sum(x["Total_Value"] for x in mutual_funds)

    portfolio_data = {
        "ETFs": etf_holdings,
        "MutualFunds": mutual_funds,
        "TotalPortfolioValue": round(total_value, 2)
    }

    with open("portfolio.json", "w") as f:
        json.dump(portfolio_data, f, indent=4)

    print(f"Portfolio updated successfully! Total Value: ₹{total_value:.2f}")

if __name__ == "__main__":
    while True:
        save_to_json()
        time.sleep(60)
