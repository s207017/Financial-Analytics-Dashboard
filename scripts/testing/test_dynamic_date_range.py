#!/usr/bin/env python3
"""
Test script for dynamic date range functionality.
This script demonstrates how the system automatically detects missing date ranges
and fetches only the missing data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_access.stock_data_service import get_stock_data_service
import pandas as pd
from datetime import datetime, timedelta

def test_dynamic_date_range():
    """Test the dynamic date range functionality."""
    print("🧪 Testing Dynamic Date Range Functionality")
    print("=" * 50)
    
    # Get the stock data service
    stock_service = get_stock_data_service()
    
    # Test symbol
    symbol = "AAPL"
    
    # Define a date range that might have gaps
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"📅 Requesting data for {symbol} from {start_date} to {end_date}")
    
    # First, check what data we currently have
    print("\n1️⃣ Checking existing data...")
    existing_data = stock_service.get_stock_data_from_db(symbol)
    if existing_data is not None and not existing_data.empty:
        existing_start = existing_data.index.min().strftime('%Y-%m-%d')
        existing_end = existing_data.index.max().strftime('%Y-%m-%d')
        print(f"   📊 Existing data: {existing_start} to {existing_end} ({len(existing_data)} data points)")
    else:
        print("   📊 No existing data found")
    
    # Now request data with dynamic date range filling
    print("\n2️⃣ Requesting data with dynamic date range filling...")
    data = stock_service.get_stock_data(symbol, start_date, end_date)
    
    if data is not None and not data.empty:
        actual_start = data.index.min().strftime('%Y-%m-%d')
        actual_end = data.index.max().strftime('%Y-%m-%d')
        print(f"   ✅ Retrieved data: {actual_start} to {actual_end} ({len(data)} data points)")
        
        # Show some sample data
        print(f"\n3️⃣ Sample data (first 5 rows):")
        print(data.head())
        
        # Check if we have data for the requested range
        requested_start = pd.to_datetime(start_date)
        requested_end = pd.to_datetime(end_date)
        
        data_in_range = data[(data.index >= requested_start) & (data.index <= requested_end)]
        print(f"\n4️⃣ Data points in requested range: {len(data_in_range)}")
        
        if len(data_in_range) > 0:
            print("   ✅ Successfully retrieved data for the requested date range!")
        else:
            print("   ⚠️  No data found in the requested date range")
            
    else:
        print("   ❌ Failed to retrieve data")
    
    print("\n" + "=" * 50)
    print("🎯 Dynamic Date Range Test Complete!")

if __name__ == "__main__":
    test_dynamic_date_range()
