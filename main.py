# main.py
import requests

API_URL = "http://cdn.tsetmc.com/api/ClosingPrice/GetMarketMap?market=0&size=1360&sector=0&typeSelected=1"

def fetch_market_map(url: str = API_URL):
    """Fetch full market map list from TSETMC CDN API."""
    resp = requests.get(url)
    resp.raise_for_status()  # Ensure successful response
    return resp.json()

def get_stock_info(symbol: str):
    """Fetch detailed info for a stock symbol."""
    # This function will be expanded later based on the exact format of data we need
    # For now, we simply return mock data for testing
    market_data = fetch_market_map()
    for stock in market_data:
        if stock['lVal18AFC'] == symbol:
            return stock  # Simplified logic for demo purposes
    return None  # Return None if stock not found

# Testing
if __name__ == "__main__":
    print(get_stock_info("فملی"))  # Example symbol
