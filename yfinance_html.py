import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# =========================
# Configuration
# =========================
OUTPUT_DIR = Path(r"C:\Users\arjju\OneDrive\Documents\code\yfinance_html")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TICKERS = {
    "S&P 500": "^GSPC", "Russell 2000": "^RUT", "S&P 50": "XLG", "S&P 10": "MGC",
    "Dow 30": "^DJI", "Nasdaq 100": "^NDX", "Growth": "MGK", "Value": "MGV",
    "Semiconductor": "SOXX", "Information Technology": "XLK", "Communication Services": "XLC",
    "Materials": "XLB", "Healthcare": "XLV", "Financial": "XLF", "Energy": "XLE",
    "Utilities": "XLU", "Real Estate": "XLRE", "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP", "Industrial": "XLI", "Fintech": "FINX",
    "Gold":"GLD", "Silver":"SLV", "Oil":"USO", "BTC-USD":"BTC-USD", "ETH-USD":"ETH-USD",
    "Berkshire Hathaway": "BRK-B"
}

# Added 84 months as requested
MONTH_WINDOWS = [84, 72, 60, 36, 24, 12, 6, 3]
END_DATE = datetime.today()

def calculate_metrics(df_price, window_months):
    """Calculates Annualized Return, Sharpe, and Sortino based on Price."""
    metrics = []
    for column in df_price.columns:
        returns = df_price[column].pct_change().dropna()
        if returns.empty: continue
        
        total_return = (df_price[column].iloc[-1] / df_price[column].iloc[0])
        n_years = window_months / 12
        ann_return = (total_return ** (1/n_years)) - 1
        
        vol = returns.std() * np.sqrt(12)
        sharpe = (returns.mean() * 12) / vol if vol > 0.0001 else 0
        
        downside_returns = returns[returns < 0]
        if len(downside_returns) < 2:
            sortino = 99.9 # Signal for no downside
        else:
            downside_vol = downside_returns.std() * np.sqrt(12)
            sortino = (returns.mean() * 12) / downside_vol if downside_vol > 0 else 0
        
        metrics.append({
            "Asset": column,
            "Ann. Return %": round(ann_return * 100, 2),
            "Sharpe Ratio": round(sharpe, 2),
            "Sortino Ratio": round(sortino, 2)
        })
    return pd.DataFrame(metrics)

def process_time_horizons():
    # 1. Pull Data (Close and Volume)
    max_months = max(MONTH_WINDOWS)
    max_start = END_DATE - relativedelta(months=max_months)
    print(f"Fetching {max_months} months of data from {max_start.strftime('%Y-%m-%d')}...\n")
    
    # Use a dictionary to store DataFrames for each ticker
    ticker_data_dict = {}
    
    for name, ticker in TICKERS.items():
        try:
            # Downloading full data to get Close and Volume
            df = yf.download(ticker, start=max_start, end=END_DATE, progress=False)
            
            if not df.empty:
                # Handle MultiIndex for newer yfinance versions
                if isinstance(df.columns, pd.MultiIndex):
                    # Extract 'Close' and 'Volume' for the specific ticker
                    ticker_df = pd.DataFrame({
                        'Close': df['Close'][ticker].astype(float),
                        'Volume': df['Volume'][ticker].astype(float)
                    })
                else:
                    ticker_df = df[['Close', 'Volume']].astype(float)
                
                ticker_data_dict[name] = ticker_df
                print(f" ✓ {name} downloaded.")
        except Exception as e:
            print(f" ✗ Error downloading {name}: {e}")

    # 2. Process each window
    for months in MONTH_WINDOWS:
        print(f"\n--- Processing {months}-Month Horizon ---")
        window_start = END_DATE - relativedelta(months=months)
        
        combined_price = pd.DataFrame()
        combined_volume = pd.DataFrame()
        
        for name, df in ticker_data_dict.items():
            # Filter for window
            mask = df.index >= window_start
            df_window = df.loc[mask]
            
            if df_window.empty: continue
            
            # Resample: Price (Last), Volume (Sum)
            monthly_price = df_window['Close'].resample('ME').last()
            monthly_volume = df_window['Volume'].resample('ME').sum()
            
            # Normalize Price (First point = 1.0)
            norm_price = (monthly_price / monthly_price.iloc[0]).round(2)
            
            combined_price[name] = norm_price
            combined_volume[name] = monthly_volume

        # 3. Save Files
        combined_price.to_csv(OUTPUT_DIR / f"price_combined_{months}m.csv")
        combined_volume.to_csv(OUTPUT_DIR / f"volume_combined_{months}m.csv")
        
        # Calculate Metrics based on normalized price
        stats_df = calculate_metrics(combined_price, months)
        stats_df.to_csv(OUTPUT_DIR / f"metrics_{months}m.csv", index=False)
        
        # Display
        top_3 = stats_df.sort_values(by="Ann. Return %", ascending=False).head(3)
        print(f"Top 3 Assets ({months}m):")
        print(top_3[["Asset", "Ann. Return %", "Sharpe Ratio"]].to_string(index=False))

    print(f"\n✅ Complete. Check {OUTPUT_DIR} for Price, Volume, and Metrics files.")

if __name__ == "__main__":
    process_time_horizons()