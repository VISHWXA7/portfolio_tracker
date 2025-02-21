import os
import yfinance as yf
import requests
import gspread
from dotenv import load_dotenv
from gspread_formatting import *
from oauth2client.service_account import ServiceAccountCredentials
from binance.client import Client

# **SECURITY: Load Binance API keys from ENV variables**
load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# **Google Sheets Setup**
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client_gs = gspread.authorize(creds)

# Open Google Sheet
sheet = client_gs.open("portfolio_tracker").sheet1  # Change to your sheet name

# **Binance API Client**
def get_binance_client():
    if not api_key or not api_secret:
        raise ValueError("Missing Binance API keys. Set them as environment variables.")
    return Client(api_key, api_secret)

client = get_binance_client()

def calculate_weighted_price(old_price, old_quantity, new_price, new_quantity):
    if old_quantity == 0:
        return new_price
    return ((old_price * old_quantity) + (new_price * new_quantity)) / (old_quantity + new_quantity)

def fetch_crypto_holdings():
    try:
        balances = client.get_account()["balances"]
        prices = {p["symbol"]: float(p["price"]) for p in client.get_all_tickers()}
        
        crypto_data = []
        sheet_data = sheet.get_all_values()
        quantity_map, buy_price_map = {}, {}

        for row in sheet_data:
            if row and row[0] == "Crypto":
                asset = row[1]
                try:
                    quantity_map[asset] = float(row[2])
                    buy_price_map[asset] = float(row[3])
                except ValueError:
                    pass
        
        for b in balances:
            asset = b["asset"]
            quantity = float(b["free"])
            symbol = asset + "USDT" if asset + "USDT" in prices else asset + "BUSD"
            if quantity > 0 and symbol in prices:
                current_price = prices[symbol]
                old_quantity = quantity_map.get(asset, 0)
                old_buy_price = buy_price_map.get(asset, 0)
                new_buy_price = calculate_weighted_price(old_buy_price, old_quantity, current_price, quantity - old_quantity)
                total_value = quantity * current_price
                profit_loss = (current_price - new_buy_price) * quantity
                crypto_data.append((asset, quantity, new_buy_price, current_price, total_value, profit_loss))
        return crypto_data
    except Exception as e:
        print(f"Error fetching crypto holdings: {e}")
        return []

def fetch_etf_prices():
    etfs = ["VTI", "QQQM", "VXUS", "GOLDBEES.NS"]
    etf_holdings = []
    
    try:
        sheet_data = sheet.get_all_values()
        quantity_map, buy_price_map = {}, {}

        for row in sheet_data:
            if row and row[0] == "ETF":
                etf_name = row[1]
                try:
                    quantity_map[etf_name] = float(row[2])
                    buy_price_map[etf_name] = float(row[3])
                except ValueError:
                    pass
        
        for ticker in etfs:
            try:
                etf = yf.Ticker(ticker)
                price = etf.history(period="1d")["Close"].iloc[-1]
                old_quantity = quantity_map.get(ticker, 0)
                new_quantity = old_quantity
                old_buy_price = buy_price_map.get(ticker, 0)
                new_buy_price = calculate_weighted_price(old_buy_price, old_quantity, price, new_quantity - old_quantity)
                total_value = price * new_quantity
                profit_loss = (price - new_buy_price) * new_quantity
                etf_holdings.append((ticker, new_quantity, new_buy_price, price, total_value, profit_loss))
            except Exception as e:
                print(f"Error fetching {ticker} data: {e}")
    
    except Exception as e:
        print(f"Error reading ETF data from Google Sheets: {e}")
    
    return etf_holdings

def fetch_mutual_fund_nav():
    fund_codes = {"INF789F01XA0": "UTI Nifty 50", "INF846K01K35": "Axis Smallcap", "INF247L01445": "Motilal Oswal Midcap"}
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    
    try:
        sheet_data = sheet.get_all_values()
        quantity_map, buy_price_map = {}, {}

        for row in sheet_data:
            if row and row[0] == "Mutual Fund":
                fund_name = row[1]
                try:
                    quantity_map[fund_name] = float(row[2])
                    buy_price_map[fund_name] = float(row[3])
                except ValueError:
                    pass
        
        response = requests.get(url, timeout=15)
        data = response.text.splitlines()
        fund_data = {}

        for line in data:
            for code, name in fund_codes.items():
                if code in line:
                    fields = line.split(';')
                    if len(fields) >= 6:
                        nav = float(fields[4])
                        old_quantity = quantity_map.get(name, 0)
                        new_quantity = old_quantity
                        old_buy_price = buy_price_map.get(name, 0)
                        new_buy_price = calculate_weighted_price(old_buy_price, old_quantity, nav, new_quantity - old_quantity)
                        total_value = nav * new_quantity
                        profit_loss = (nav - new_buy_price) * new_quantity
                        fund_data[name] = {"nav": nav, "quantity": new_quantity, "buy_price": new_buy_price, "total_value": total_value, "profit_loss": profit_loss}
        
        return fund_data
    except Exception as e:
        print(f"Error fetching mutual fund data: {e}")
        return {}

def update_google_sheets(crypto, etfs, mutual_funds):
    try:
        sheet.clear()
        sheet.append_row(["Category", "Asset", "Quantity", "Buy_price", "Price (₹/$)", "Total Value (₹/$)", "P&L (₹/$)"])

        for data in crypto:
            sheet.append_row([
                "Crypto", 
                data[0], 
                data[1],
                data[2],
                data[3],  # Keeping price unrounded
                data[4], 
                data[5]
            ])

        for data in etfs:
            sheet.append_row([
                "ETF", 
                data[0], 
                round(data[1], 2), 
                round(data[2], 2), 
                round(data[3], 2), 
                round(data[4], 2), 
                round(data[5], 2)
            ])

        for fund, data in mutual_funds.items():
           quantity = data.get("quantity", 0)
           buy_price = data.get("buy_price", 0)
           sheet.append_row([
                "Mutual Fund", 
                fund, 
                round(quantity, 2), 
                round(buy_price, 2), 
                round(data["nav"], 2), 
                round(data["total_value"], 2), 
                round(data["profit_loss"], 2)
            ])

        print("Google Sheet updated successfully!")
    except Exception as e:
        print(f"Error updating sheet: {e}")
        
        
def display_portfolio():
    crypto_holdings = fetch_crypto_holdings()
    etf_holdings = fetch_etf_prices()
    mutual_fund_data = fetch_mutual_fund_nav()
    update_google_sheets(crypto_holdings, etf_holdings, mutual_fund_data)

    total_value = sum(v[4] for v in crypto_holdings + etf_holdings) + sum(data["total_value"] for data in mutual_fund_data.values())
    print(f"Total Portfolio Value: ₹{total_value:.2f}")

if __name__ == "__main__":
    display_portfolio()
