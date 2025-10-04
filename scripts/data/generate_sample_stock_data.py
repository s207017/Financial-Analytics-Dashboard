"""
Generate sample stock data for demonstration purposes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from config.config import DATABASE_CONFIG
from sqlalchemy import create_engine
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_sample_stock_data():
    """Generate comprehensive sample stock data"""
    
    # Sample stock symbols and basic info
    stock_data = [
        # Technology - Large Cap
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Content & Information"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "industry": "Internet Retail"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Social Media"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary", "industry": "Auto Manufacturers"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
        {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Technology", "industry": "Entertainment"},
        
        # Healthcare - Large Cap
        {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharmaceuticals"},
        {"symbol": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare", "industry": "Pharmaceuticals"},
        {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare", "industry": "Managed Health Care"},
        {"symbol": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare", "industry": "Pharmaceuticals"},
        {"symbol": "MRK", "name": "Merck & Co Inc.", "sector": "Healthcare", "industry": "Pharmaceuticals"},
        
        # Financial - Large Cap
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services", "industry": "Banks"},
        {"symbol": "BAC", "name": "Bank of America Corp.", "sector": "Financial Services", "industry": "Banks"},
        {"symbol": "WFC", "name": "Wells Fargo & Co.", "sector": "Financial Services", "industry": "Banks"},
        {"symbol": "GS", "name": "Goldman Sachs Group Inc.", "sector": "Financial Services", "industry": "Investment Banking"},
        {"symbol": "MS", "name": "Morgan Stanley", "sector": "Financial Services", "industry": "Investment Banking"},
        
        # Consumer - Large Cap
        {"symbol": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Staples", "industry": "Household Products"},
        {"symbol": "KO", "name": "Coca-Cola Co.", "sector": "Consumer Staples", "industry": "Beverages"},
        {"symbol": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer Staples", "industry": "Beverages"},
        {"symbol": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples", "industry": "Discount Stores"},
        {"symbol": "HD", "name": "Home Depot Inc.", "sector": "Consumer Discretionary", "industry": "Home Improvement Retail"},
        {"symbol": "MCD", "name": "McDonald's Corp.", "sector": "Consumer Discretionary", "industry": "Restaurants"},
        {"symbol": "NKE", "name": "Nike Inc.", "sector": "Consumer Discretionary", "industry": "Footwear & Accessories"},
        
        # Industrial - Large Cap
        {"symbol": "BA", "name": "Boeing Co.", "sector": "Industrials", "industry": "Aerospace & Defense"},
        {"symbol": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials", "industry": "Construction & Mining Equipment"},
        {"symbol": "GE", "name": "General Electric Co.", "sector": "Industrials", "industry": "Industrial Conglomerates"},
        {"symbol": "MMM", "name": "3M Co.", "sector": "Industrials", "industry": "Industrial Conglomerates"},
        {"symbol": "HON", "name": "Honeywell International Inc.", "sector": "Industrials", "industry": "Industrial Conglomerates"},
        
        # Energy - Large Cap
        {"symbol": "XOM", "name": "Exxon Mobil Corp.", "sector": "Energy", "industry": "Oil & Gas Integrated"},
        {"symbol": "CVX", "name": "Chevron Corp.", "sector": "Energy", "industry": "Oil & Gas Integrated"},
        {"symbol": "COP", "name": "ConocoPhillips", "sector": "Energy", "industry": "Oil & Gas E&P"},
        {"symbol": "EOG", "name": "EOG Resources Inc.", "sector": "Energy", "industry": "Oil & Gas E&P"},
        
        # Utilities - Large Cap
        {"symbol": "NEE", "name": "NextEra Energy Inc.", "sector": "Utilities", "industry": "Electric Utilities"},
        {"symbol": "DUK", "name": "Duke Energy Corp.", "sector": "Utilities", "industry": "Electric Utilities"},
        {"symbol": "SO", "name": "Southern Co.", "sector": "Utilities", "industry": "Electric Utilities"},
        {"symbol": "D", "name": "Dominion Energy Inc.", "sector": "Utilities", "industry": "Electric Utilities"},
        
        # Real Estate - Large Cap
        {"symbol": "AMT", "name": "American Tower Corp.", "sector": "Real Estate", "industry": "REITs"},
        {"symbol": "PLD", "name": "Prologis Inc.", "sector": "Real Estate", "industry": "REITs"},
        {"symbol": "CCI", "name": "Crown Castle Inc.", "sector": "Real Estate", "industry": "REITs"},
        {"symbol": "EQIX", "name": "Equinix Inc.", "sector": "Real Estate", "industry": "REITs"},
        
        # Materials - Large Cap
        {"symbol": "LIN", "name": "Linde plc", "sector": "Materials", "industry": "Specialty Chemicals"},
        {"symbol": "APD", "name": "Air Products and Chemicals Inc.", "sector": "Materials", "industry": "Specialty Chemicals"},
        {"symbol": "SHW", "name": "Sherwin-Williams Co.", "sector": "Materials", "industry": "Specialty Chemicals"},
        {"symbol": "ECL", "name": "Ecolab Inc.", "sector": "Materials", "industry": "Specialty Chemicals"},
        
        # Communication - Large Cap
        {"symbol": "VZ", "name": "Verizon Communications Inc.", "sector": "Communication Services", "industry": "Telecom Services"},
        {"symbol": "T", "name": "AT&T Inc.", "sector": "Communication Services", "industry": "Telecom Services"},
        {"symbol": "CMCSA", "name": "Comcast Corp.", "sector": "Communication Services", "industry": "Cable & Satellite"},
        {"symbol": "DIS", "name": "Walt Disney Co.", "sector": "Communication Services", "industry": "Entertainment"},
        
        # Mid Cap Examples
        {"symbol": "AMD", "name": "Advanced Micro Devices Inc.", "sector": "Technology", "industry": "Semiconductors"},
        {"symbol": "INTC", "name": "Intel Corp.", "sector": "Technology", "industry": "Semiconductors"},
        {"symbol": "CRM", "name": "Salesforce Inc.", "sector": "Technology", "industry": "Software"},
        {"symbol": "ADBE", "name": "Adobe Inc.", "sector": "Technology", "industry": "Software"},
        {"symbol": "ORCL", "name": "Oracle Corp.", "sector": "Technology", "industry": "Software"},
        {"symbol": "IBM", "name": "International Business Machines Corp.", "sector": "Technology", "industry": "IT Services"},
        {"symbol": "CSCO", "name": "Cisco Systems Inc.", "sector": "Technology", "industry": "Networking Equipment"},
        {"symbol": "QCOM", "name": "QUALCOMM Inc.", "sector": "Technology", "industry": "Semiconductors"},
        
        # Small Cap Examples
        {"symbol": "SNAP", "name": "Snap Inc.", "sector": "Technology", "industry": "Social Media"},
        {"symbol": "TWTR", "name": "Twitter Inc.", "sector": "Technology", "industry": "Social Media"},
        {"symbol": "UBER", "name": "Uber Technologies Inc.", "sector": "Technology", "industry": "Software"},
        {"symbol": "LYFT", "name": "Lyft Inc.", "sector": "Technology", "industry": "Software"},
        {"symbol": "SQ", "name": "Block Inc.", "sector": "Technology", "industry": "Software"},
        {"symbol": "PYPL", "name": "PayPal Holdings Inc.", "sector": "Technology", "industry": "Software"},
        {"symbol": "ZM", "name": "Zoom Video Communications Inc.", "sector": "Technology", "industry": "Software"},
        {"symbol": "DOCU", "name": "DocuSign Inc.", "sector": "Technology", "industry": "Software"},
    ]
    
    # Convert to DataFrame
    df = pd.DataFrame(stock_data)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate realistic financial metrics
    n_stocks = len(df)
    
    # Market Cap (in billions) - with some mega cap stocks
    market_caps = np.random.lognormal(mean=2, sigma=1.5, size=n_stocks) * 1e9
    
    # Add some mega cap stocks (Apple, Microsoft, Google, Amazon, Tesla)
    mega_cap_indices = [0, 1, 2, 3, 5]  # AAPL, MSFT, GOOGL, AMZN, TSLA
    for idx in mega_cap_indices:
        if idx < len(market_caps):
            market_caps[idx] = np.random.uniform(100_000_000_000, 500_000_000_000)  # $100B-$500B
    
    df['market_cap'] = market_caps
    
    # Market Cap Categories
    def get_market_cap_category(market_cap):
        if market_cap >= 100_000_000_000:
            return 'Mega Cap ($100B+)'
        elif market_cap >= 10_000_000_000:
            return 'Large Cap ($10B+)'
        elif market_cap >= 2_000_000_000:
            return 'Mid Cap ($2B+)'
        elif market_cap >= 300_000_000:
            return 'Small Cap ($300M+)'
        elif market_cap >= 50_000_000:
            return 'Micro Cap ($50M+)'
        else:
            return 'Nano Cap ($10M+)'
    
    df['market_cap_category'] = df['market_cap'].apply(get_market_cap_category)
    
    # Current Price
    df['current_price'] = np.random.lognormal(mean=3, sigma=1, size=n_stocks)
    
    # Previous Close (slightly different from current price)
    df['previous_close'] = df['current_price'] * (1 + np.random.normal(0, 0.02, n_stocks))
    
    # Day Change
    df['day_change'] = df['current_price'] - df['previous_close']
    df['day_change_percent'] = (df['day_change'] / df['previous_close']) * 100
    
    # Volume (in millions)
    df['volume'] = np.random.lognormal(mean=6, sigma=1, size=n_stocks).astype(int)
    df['avg_volume'] = df['volume'] * (1 + np.random.normal(0, 0.3, n_stocks)).astype(int)
    
    # PE Ratio (with some realistic distribution)
    pe_ratios = np.random.lognormal(mean=2.5, sigma=0.8, size=n_stocks)
    pe_ratios = np.clip(pe_ratios, 5, 100)  # Reasonable PE range
    df['pe_ratio'] = pe_ratios
    
    # Forward PE (slightly different)
    df['forward_pe'] = df['pe_ratio'] * (1 + np.random.normal(0, 0.1, n_stocks))
    
    # PEG Ratio
    df['peg_ratio'] = np.random.lognormal(mean=0.5, sigma=0.5, size=n_stocks)
    df['peg_ratio'] = np.clip(df['peg_ratio'], 0.1, 5)
    
    # Price to Book
    df['price_to_book'] = np.random.lognormal(mean=1.5, sigma=0.8, size=n_stocks)
    df['price_to_book'] = np.clip(df['price_to_book'], 0.5, 20)
    
    # Price to Sales
    df['price_to_sales'] = np.random.lognormal(mean=2, sigma=1, size=n_stocks)
    df['price_to_sales'] = np.clip(df['price_to_sales'], 0.5, 30)
    
    # Dividend Yield (higher for certain sectors)
    dividend_yields = np.random.exponential(0.02, size=n_stocks)
    # Make utilities and consumer staples have higher dividends
    high_dividend_mask = df['sector'].isin(['Utilities', 'Consumer Staples', 'Real Estate'])
    dividend_yields[high_dividend_mask] = np.random.exponential(0.04, size=high_dividend_mask.sum())
    dividend_yields = np.clip(dividend_yields, 0, 0.15)  # Max 15%
    df['dividend_yield'] = dividend_yields
    
    # Dividend Rate
    df['dividend_rate'] = df['current_price'] * df['dividend_yield']
    
    # Beta (market sensitivity)
    df['beta'] = np.random.normal(1, 0.5, size=n_stocks)
    df['beta'] = np.clip(df['beta'], 0.2, 2.5)
    
    # Debt to Equity
    df['debt_to_equity'] = np.random.exponential(0.5, size=n_stocks)
    df['debt_to_equity'] = np.clip(df['debt_to_equity'], 0, 3)
    
    # Return on Equity
    df['return_on_equity'] = np.random.normal(0.15, 0.1, size=n_stocks)
    df['return_on_equity'] = np.clip(df['return_on_equity'], -0.2, 0.5)
    
    # Profit Margins
    df['profit_margins'] = np.random.normal(0.1, 0.08, size=n_stocks)
    df['profit_margins'] = np.clip(df['profit_margins'], -0.1, 0.4)
    
    # Revenue Growth
    df['revenue_growth'] = np.random.normal(0.05, 0.15, size=n_stocks)
    df['revenue_growth'] = np.clip(df['revenue_growth'], -0.3, 0.5)
    
    # Earnings Growth
    df['earnings_growth'] = np.random.normal(0.08, 0.2, size=n_stocks)
    df['earnings_growth'] = np.clip(df['earnings_growth'], -0.5, 0.8)
    
    # 52 Week High/Low
    df['week_52_high'] = df['current_price'] * (1 + np.random.uniform(0.1, 0.5, n_stocks))
    df['week_52_low'] = df['current_price'] * (1 - np.random.uniform(0.1, 0.4, n_stocks))
    
    # Enterprise Value
    df['enterprise_value'] = df['market_cap'] * (1 + np.random.normal(0, 0.2, n_stocks))
    
    # Shares Outstanding
    df['shares_outstanding'] = (df['market_cap'] / df['current_price']).astype(int)
    df['float_shares'] = df['shares_outstanding'] * np.random.uniform(0.8, 1.0, n_stocks)
    
    # Short Ratio
    df['short_ratio'] = np.random.exponential(2, size=n_stocks)
    df['short_ratio'] = np.clip(df['short_ratio'], 0.1, 20)
    
    # Short Percent
    df['short_percent'] = np.random.exponential(0.05, size=n_stocks)
    df['short_percent'] = np.clip(df['short_percent'], 0, 0.5)
    
    # Institutional Ownership
    df['institutional_ownership'] = np.random.uniform(0.3, 0.9, size=n_stocks)
    
    # Insider Ownership
    df['insider_ownership'] = np.random.exponential(0.1, size=n_stocks)
    df['insider_ownership'] = np.clip(df['insider_ownership'], 0, 0.5)
    
    # Analyst Recommendation (1-5 scale)
    df['analyst_recommendation'] = np.random.normal(3, 0.5, size=n_stocks)
    df['analyst_recommendation'] = np.clip(df['analyst_recommendation'], 1, 5)
    
    # Target Price
    df['target_price'] = df['current_price'] * (1 + np.random.normal(0.1, 0.2, n_stocks))
    
    # Additional fields
    df['currency'] = 'USD'
    df['exchange'] = 'NASDAQ'
    df['country'] = 'US'
    df['website'] = 'https://example.com'
    df['business_summary'] = 'Sample business description for ' + df['name']
    df['employees'] = np.random.lognormal(mean=8, sigma=1, size=n_stocks).astype(int)
    df['founded_year'] = np.random.randint(1800, 2020, size=n_stocks)
    df['last_updated'] = datetime.now().isoformat()
    df['created_at'] = datetime.now().isoformat()
    
    return df

def store_sample_data():
    """Generate and store sample stock data"""
    
    # Create database connection
    engine = create_engine(
        f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@"
        f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['name']}"
    )
    
    try:
        logger.info("Generating sample stock data...")
        
        # Generate sample data
        sample_data = generate_sample_stock_data()
        
        logger.info(f"Generated data for {len(sample_data)} stocks")
        
        # Store in database
        sample_data.to_sql('stock_info', engine, if_exists='replace', index=False)
        logger.info("Sample stock data stored in database successfully")
        
        # Display summary
        logger.info("\nSample Data Summary:")
        logger.info(f"Total stocks: {len(sample_data)}")
        logger.info(f"Market cap distribution: {sample_data['market_cap_category'].value_counts().to_dict()}")
        logger.info(f"Sector distribution: {sample_data['sector'].value_counts().to_dict()}")
        logger.info(f"Average PE ratio: {sample_data['pe_ratio'].mean():.2f}")
        logger.info(f"Average dividend yield: {sample_data['dividend_yield'].mean():.4f}")
        logger.info(f"Average beta: {sample_data['beta'].mean():.2f}")
        
        # Show some examples
        logger.info("\nSample stocks:")
        sample_display = sample_data[['symbol', 'name', 'sector', 'market_cap_category', 'current_price', 'pe_ratio', 'dividend_yield']].head(10)
        for _, row in sample_display.iterrows():
            logger.info(f"  {row['symbol']}: {row['name']} - {row['sector']} - {row['market_cap_category']} - ${row['current_price']:.2f} - PE: {row['pe_ratio']:.2f} - Div: {row['dividend_yield']:.4f}")
        
    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}")
        raise

if __name__ == "__main__":
    store_sample_data()

