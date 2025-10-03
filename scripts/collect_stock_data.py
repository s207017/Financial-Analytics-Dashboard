"""
Collect comprehensive stock data for US stocks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_ingestion.stock_filtering.stock_data_collector import StockDataCollector, StockFilters
from config.config import DATABASE_CONFIG
from sqlalchemy import create_engine
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_and_store_stock_data():
    """Collect stock data and store in database"""
    
    # Initialize collector
    collector = StockDataCollector()
    
    # Create database connection
    engine = create_engine(
        f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@"
        f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['name']}"
    )
    
    try:
        logger.info("Starting stock data collection...")
        
        # Collect data for popular stocks
        logger.info(f"Collecting data for {len(collector.popular_stocks)} stocks...")
        stock_data = collector.collect_multiple_stocks(collector.popular_stocks, delay=0.2)
        
        if stock_data.empty:
            logger.error("No stock data collected")
            return
        
        logger.info(f"Collected data for {len(stock_data)} stocks")
        
        # Rename columns to match database schema
        stock_data = stock_data.rename(columns={
            '52_week_high': 'week_52_high',
            '52_week_low': 'week_52_low'
        })
        
        # Store in database
        stock_data.to_sql('stock_info', engine, if_exists='replace', index=False)
        logger.info("Stock data stored in database successfully")
        
        # Get and display summary
        summary = collector.get_stock_screener_summary(stock_data)
        logger.info("Stock Data Summary:")
        logger.info(f"Total stocks: {summary['total_stocks']}")
        logger.info(f"Market cap distribution: {summary['market_cap_distribution']}")
        logger.info(f"Sector distribution: {summary['sector_distribution']}")
        logger.info(f"Average PE ratio: {summary['avg_pe_ratio']:.2f}")
        logger.info(f"Average dividend yield: {summary['avg_dividend_yield']:.4f}")
        
        # Test filtering
        logger.info("\nTesting stock filtering...")
        
        # Test 1: Large cap stocks
        large_cap_filter = StockFilters(market_cap_categories=['Large Cap'])
        large_cap_stocks = collector.filter_stocks(stock_data, large_cap_filter)
        logger.info(f"Large cap stocks: {len(large_cap_stocks)}")
        
        # Test 2: Technology sector
        tech_filter = StockFilters(sectors=['Technology'])
        tech_stocks = collector.filter_stocks(stock_data, tech_filter)
        logger.info(f"Technology stocks: {len(tech_stocks)}")
        
        # Test 3: High dividend yield
        dividend_filter = StockFilters(dividend_yield_min=0.03)  # 3%+
        dividend_stocks = collector.filter_stocks(stock_data, dividend_filter)
        logger.info(f"High dividend stocks (3%+): {len(dividend_stocks)}")
        
        # Test 4: Low PE ratio
        value_filter = StockFilters(pe_ratio_max=15)
        value_stocks = collector.filter_stocks(stock_data, value_filter)
        logger.info(f"Value stocks (PE < 15): {len(value_stocks)}")
        
        # Test 5: Growth stocks (low PEG)
        growth_filter = StockFilters(peg_ratio_max=1.5)
        growth_stocks = collector.filter_stocks(stock_data, growth_filter)
        logger.info(f"Growth stocks (PEG < 1.5): {len(growth_stocks)}")
        
        # Test 6: Combined filter
        combined_filter = StockFilters(
            market_cap_categories=['Large Cap', 'Mid Cap'],
            sectors=['Technology', 'Healthcare'],
            pe_ratio_max=25,
            dividend_yield_min=0.01
        )
        combined_stocks = collector.filter_stocks(stock_data, combined_filter)
        logger.info(f"Combined filter results: {len(combined_stocks)}")
        
        if not combined_stocks.empty:
            logger.info("Top 5 combined filter results:")
            for _, stock in combined_stocks.head().iterrows():
                logger.info(f"  {stock['symbol']}: {stock['name']} - PE: {stock['pe_ratio']:.2f}, Div: {stock['dividend_yield']:.4f}")
        
    except Exception as e:
        logger.error(f"Error in stock data collection: {str(e)}")
        raise

if __name__ == "__main__":
    collect_and_store_stock_data()
