#!/usr/bin/env python3
"""
Test script for the Stock Data Service
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.data_access.stock_data_service import get_stock_data_service

def test_stock_data_service():
    """Test the stock data service functionality."""
    print("🧪 Testing Stock Data Service...")
    print("=" * 50)
    
    # Get service instance
    service = get_stock_data_service()
    
    # Test Redis connection
    print("1. Testing Redis connection...")
    redis_available = service.check_redis_connection()
    print(f"   Redis available: {'✅' if redis_available else '❌'}")
    
    # Test symbols
    test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    
    print(f"\n2. Testing stock data fetching for: {test_symbols}")
    print("-" * 30)
    
    # Test fetching data for each symbol
    for symbol in test_symbols:
        print(f"\n   Testing {symbol}...")
        
        # Check if data exists in database
        existing_data = service.get_stock_data_from_db(symbol)
        if existing_data is not None and not existing_data.empty:
            print(f"     ✅ Data exists in DB: {len(existing_data)} records")
            print(f"     📅 Date range: {existing_data.index.min()} to {existing_data.index.max()}")
        else:
            print(f"     ❌ No data in DB")
        
        # Try to fetch and store data
        print(f"     🔄 Fetching data...")
        success = service.fetch_and_store_stock_data(symbol)
        print(f"     {'✅' if success else '❌'} Fetch result: {success}")
        
        # Check cache
        cached_data = service.get_cached_data(symbol)
        if cached_data:
            print(f"     📦 Cached data: {cached_data.get('data_points', 'N/A')} points")
        else:
            print(f"     📦 No cached data")
    
    print(f"\n3. Testing portfolio data availability...")
    print("-" * 30)
    
    # Test ensuring data for a portfolio
    portfolio_symbols = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'META']
    results = service.ensure_stock_data_available(portfolio_symbols)
    
    print("   Portfolio symbols results:")
    for symbol, success in results.items():
        print(f"     {symbol}: {'✅' if success else '❌'}")
    
    print(f"\n4. Getting available symbols...")
    print("-" * 30)
    
    available_symbols = service.get_available_symbols()
    print(f"   Total symbols in database: {len(available_symbols)}")
    print(f"   First 10: {available_symbols[:10]}")
    
    print(f"\n5. Testing data retrieval...")
    print("-" * 30)
    
    # Test getting data for a specific symbol
    test_symbol = 'AAPL'
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    df = service.get_stock_data(test_symbol, start_date, end_date)
    if df is not None and not df.empty:
        print(f"   ✅ Retrieved {len(df)} records for {test_symbol}")
        print(f"   📊 Latest close price: ${df['close'].iloc[-1]:.2f}")
        print(f"   📈 30-day return: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
    else:
        print(f"   ❌ No data retrieved for {test_symbol}")
    
    print("\n" + "=" * 50)
    print("🎉 Stock Data Service test completed!")

if __name__ == "__main__":
    test_stock_data_service()
