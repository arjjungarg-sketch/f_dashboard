import requests

API_KEY = 'LY7I9WQE9RD43EVK'
url = f'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={API_KEY}'
response = requests.get(url)
data = response.json()

# Helper function to print the top 5 from any category
def print_top_5(category_name, data_list):
    print(f"--- {category_name.upper()} ---")
    # Slice the list to get only the first 5 items
    for i, stock in enumerate(data_list[:5], 1):
        ticker = stock['ticker']
        change = stock['change_percentage']
        price = float(stock['price'])
        volume = int(stock['volume'])
        
        # Calculate dollar volume traded
        volume_dollar_traded = price * volume
        
        # Format large numbers for readability
        if volume_dollar_traded >= 1_000_000_000:
            volume_str = f"${volume_dollar_traded/1_000_000_000:.2f}B"
        elif volume_dollar_traded >= 1_000_000:
            volume_str = f"${volume_dollar_traded/1_000_000:.2f}M"
        else:
            volume_str = f"${volume_dollar_traded:,.2f}"
        
        print(f"{i}. {ticker}: {change} (Price: ${price}, Volume $: {volume_str})")
    print("\n")

# Check if data was returned correctly
if 'top_gainers' in data:
    print_top_5("Top Gainers", data['top_gainers'])
    print_top_5("Top Losers", data['top_losers'])
    print_top_5("Most Actively Traded", data['most_actively_traded'])
else:
    print("Error or API limit reached:", data)
