import yfinance as yf
import requests
import gspread
from gspread_formatting import *
from oauth2client.service_account import ServiceAccountCredentials

# **Google Sheets Setup**
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client_gs = gspread.authorize(creds)

# Open Google Sheet
sheet = client_gs.open("portfolio_tracker").sheet1  # Change to your sheet name

def calculate_weighted_price(old_price, old_quantity, new_price, new_quantity):
    if old_quantity == 0:
        return new_price
    return ((old_price * old_quantity) + (new_price * new_quantity)) / (old_quantity + new_quantity)


def fetch_etf_prices():
    etfs = ["VTI", "QQQM", "VXUS", "GOLDBEES.NS", "BTC-USD"]
    etf_holdings = []
    
    try:
        sheet_data = sheet.get_all_values()
        quantity_map, buy_price_map = {}, {}

        for row in sheet_data:
            if row:
                asset_name = row[1]
                try:
                    quantity_map[asset_name] = float(row[2])
                    buy_price_map[asset_name] = float(row[3])
                except ValueError:
                    pass
        
        # Process ETFs
        for ticker in etfs:
            try:
                etf = yf.Ticker(ticker)
                price = etf.history(period="1d")["Close"].iloc[-1]
                old_quantity = quantity_map.get(ticker, 0)
                old_buy_price = buy_price_map.get(ticker, 0)
                new_buy_price = calculate_weighted_price(old_buy_price, old_quantity, price, old_quantity)
                total_value = price * old_quantity
                profit_loss = (price - new_buy_price) * old_quantity
                etf_holdings.append(("ETF", ticker, old_quantity, new_buy_price, price, total_value, profit_loss))
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
                        old_buy_price = buy_price_map.get(name, 0)
                        new_buy_price = calculate_weighted_price(old_buy_price, old_quantity, nav, old_quantity)
                        total_value = nav * old_quantity
                        profit_loss = (nav - new_buy_price) * old_quantity
                        fund_data[name] = {"nav": nav, "quantity": old_quantity, "buy_price": new_buy_price, "total_value": total_value, "profit_loss": profit_loss}
        
        return fund_data
    except Exception as e:
        print(f"Error fetching mutual fund data: {e}")
        return {}

def display_portfolio():
    etf_holdings = fetch_etf_prices()
    mutual_fund_data = fetch_mutual_fund_nav()
    
    total_value = sum(v[4] for v in etf_holdings) + sum(data["total_value"] for data in mutual_fund_data.values())
    
    print(f"Total Portfolio Value: ₹{total_value:.2f}")

if __name__ == "__main__":
    display_portfolio()
