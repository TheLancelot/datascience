from supabase import create_client
import requests
import os
from datetime import datetime

# Initialize Supabase client
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_btc_price(price):
    """
    Stores the Bitcoin price in Supabase database
    """
    try:
        # Insert price data into the 'bitcoin_prices' table
        data = {
            'price': price,
            'timestamp': datetime.utcnow().isoformat()
        }
        result = supabase.table('bitcoin_prices').insert(data).execute()
        print("Price stored successfully in database")
        return True
    except Exception as e:
        print(f"Error storing price in database: {str(e)}")
        return False

def get_btc_price():
    """
    Fetches the current Bitcoin price in USD using the CoinGecko API
    """
    try:
        # CoinGecko API endpoint for Bitcoin price
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        
        # Make the GET request
        response = requests.get(url)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            btc_price = data['bitcoin']['usd']
            print(f"Current Bitcoin price: ${btc_price:,.2f} USD")
            
            # Store the price in Supabase
            store_btc_price(btc_price)
            return btc_price
        else:
            print(f"Error: Unable to fetch price. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

# Test the function
if __name__ == "__main__":
    get_btc_price()
 