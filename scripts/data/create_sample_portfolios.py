#!/usr/bin/env python3
"""
Script to create sample portfolios in the database for testing and demonstration.
Automatically fetches fresh stock data from Yahoo Finance for all portfolio symbols.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.data_access.portfolio_management_service import PortfolioManagementService
from src.data_access.stock_data_service import get_stock_data_service
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_stock_data_for_symbols(symbols, stock_service):
    """Fetch stock data for all symbols in the portfolio."""
    print(f"📊 Fetching stock data for {len(symbols)} symbols...")
    
    fetched_count = 0
    failed_count = 0
    
    # Fetch data for the last 2 years to ensure we have enough data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
    
    for symbol in symbols:
        try:
            print(f"   📈 Fetching {symbol}...")
            success = stock_service.fetch_and_store_stock_data(symbol, start_date=start_date, end_date=end_date)
            
            if success:
                # Verify data was actually stored
                data = stock_service.get_stock_data(symbol)
                if data is not None and not data.empty:
                    print(f"      ✅ {symbol}: {len(data)} data points stored")
                    fetched_count += 1
                else:
                    print(f"      ❌ {symbol}: No data available after fetching")
                    failed_count += 1
            else:
                print(f"      ❌ {symbol}: Failed to fetch data")
                failed_count += 1
                
        except Exception as e:
            print(f"      ❌ {symbol}: Error - {e}")
            failed_count += 1
    
    print(f"\n📊 Stock Data Fetching Results:")
    print(f"   ✅ Successfully fetched: {fetched_count}/{len(symbols)} symbols")
    print(f"   ❌ Failed to fetch: {failed_count} symbols")
    
    return fetched_count, failed_count

def create_sample_portfolios():
    """Create sample portfolios for demonstration and fetch fresh stock data."""
    
    print("🚀 Creating sample portfolios with fresh stock data...")
    
    try:
        portfolio_service = PortfolioManagementService()
        stock_service = get_stock_data_service()
        
        # All 5 current sample portfolios with different strategies and asset allocations
        sample_portfolios = [
            {
                "name": "Tech Growth Portfolio",
                "description": "High-growth technology stocks with strong fundamentals",
                "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
                "weights": [0.25, 0.20, 0.20, 0.20, 0.15],
                "strategy": "Growth"
            },
            {
                "name": "Conservative Income",
                "description": "Stable dividend-paying stocks for income generation",
                "symbols": ["JNJ", "PG", "KO", "PEP", "WMT"],
                "weights": [0.20, 0.20, 0.20, 0.20, 0.20],
                "strategy": "Income"
            },
            {
                "name": "Balanced Portfolio",
                "description": "Mix of growth and value stocks for balanced returns",
                "symbols": ["SPY", "QQQ", "VTI", "BND", "GLD"],
                "weights": [0.30, 0.25, 0.20, 0.15, 0.10],
                "strategy": "Balanced"
            },
            {
                "name": "Dividend Growth Portfolio",
                "description": "Focus on dividend-paying stocks with growth potential",
                "symbols": ["JPM", "BAC", "WFC", "T", "VZ", "KO", "PEP", "PG"],
                "weights": [0.15, 0.15, 0.10, 0.15, 0.10, 0.15, 0.10, 0.10],
                "strategy": "dividend_growth"
            },
            {
                "name": "Emerging Tech Portfolio",
                "description": "High-growth technology and innovation companies",
                "symbols": ["NVDA", "AMD", "CRM", "ADBE", "NFLX", "PYPL", "SQ", "ZM"],
                "weights": [0.20, 0.15, 0.15, 0.15, 0.10, 0.10, 0.10, 0.05],
                "strategy": "growth"
            }
        ]
        
        # Collect all unique symbols from all portfolios
        all_symbols = set()
        for portfolio in sample_portfolios:
            all_symbols.update(portfolio["symbols"])
        
        print(f"📋 Found {len(all_symbols)} unique symbols across {len(sample_portfolios)} portfolios")
        print(f"Symbols: {', '.join(sorted(all_symbols))}")
        
        # Fetch stock data for all symbols first
        print("\n" + "="*60)
        print("FETCHING STOCK DATA FROM YAHOO FINANCE")
        print("="*60)
        
        fetched_count, failed_count = fetch_stock_data_for_symbols(list(all_symbols), stock_service)
        
        if failed_count > 0:
            print(f"\n⚠️  Warning: {failed_count} symbols failed to fetch data.")
            print("The portfolios will still be created, but some charts may not display properly.")
        
        # Create portfolios
        print("\n" + "="*60)
        print("CREATING PORTFOLIOS")
        print("="*60)
        
        created_count = 0
        for portfolio_data in sample_portfolios:
            try:
                # Check if portfolio already exists
                existing_portfolios = portfolio_service.get_all_portfolios()
                existing_names = [p["name"] for p in existing_portfolios]
                
                if portfolio_data["name"] not in existing_names:
                    result = portfolio_service.create_portfolio(
                        name=portfolio_data["name"],
                        description=portfolio_data["description"],
                        symbols=portfolio_data["symbols"],
                        weights=portfolio_data["weights"],
                        strategy=portfolio_data["strategy"]
                    )
                    logger.info(f"✅ Created portfolio: {portfolio_data['name']} with ID {result.get('id', 'unknown')}")
                    created_count += 1
                else:
                    logger.info(f"⏭️  Portfolio '{portfolio_data['name']}' already exists, skipping...")
                    
            except Exception as e:
                logger.error(f"❌ Error creating portfolio '{portfolio_data['name']}': {e}")
        
        logger.info(f"Successfully created {created_count} new sample portfolios")
        
        # Display all portfolios
        all_portfolios = portfolio_service.get_all_portfolios()
        logger.info(f"Total portfolios in database: {len(all_portfolios)}")
        
        print("\n" + "="*80)
        print("SAMPLE PORTFOLIOS CREATED SUCCESSFULLY")
        print("="*80)
        for portfolio in all_portfolios:
            print(f"ID: {portfolio['id']}")
            print(f"Name: {portfolio['name']}")
            print(f"Strategy: {portfolio['strategy']}")
            print(f"Assets: {', '.join(portfolio['symbols'])}")
            print(f"Created: {portfolio['created_at']}")
            print("-" * 40)
        
        print(f"\n🎉 Setup Complete!")
        print(f"   📊 Stock data fetched for {fetched_count} symbols")
        print(f"   📋 {len(all_portfolios)} portfolios available")
        print(f"   🚀 Ready to use the Portfolio Management dashboard!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample portfolios: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up sample portfolios with fresh stock data...")
    print("This will fetch the latest data from Yahoo Finance for all portfolio symbols.")
    print("This may take a few minutes depending on the number of symbols...\n")
    
    success = create_sample_portfolios()
    
    if success:
        print("\n✅ Sample portfolios setup completed successfully!")
        print("You can now view them in the Portfolio Management tab.")
        print("All stock data has been fetched and is ready for analysis.")
    else:
        print("\n❌ Failed to setup sample portfolios.")
        sys.exit(1)