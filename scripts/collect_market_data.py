"""
Market data collection script for the quantitative finance pipeline.
"""
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config.config import DATA_SOURCES
from data_ingestion.yahoo_finance.collector import YahooFinanceCollector
from etl.loaders.database_loader import DatabaseLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_stock_data(symbols=None, days_back=365):
    """
    Collect stock data from Yahoo Finance and store in database.
    
    Args:
        symbols: List of stock symbols (if None, uses default from config)
        days_back: Number of days of historical data to collect
    """
    if symbols is None:
        symbols = DATA_SOURCES['yahoo_finance']['symbols']
    
    logger.info(f"Starting data collection for {len(symbols)} symbols")
    
    try:
        # Initialize collectors
        yahoo_collector = YahooFinanceCollector()
        db_loader = DatabaseLoader("postgresql://postgres:password@localhost:5432/quant_finance")
        
        # Collect data from Yahoo Finance
        logger.info("Collecting Yahoo Finance data...")
        yahoo_data = yahoo_collector.collect_data(
            symbols=symbols,
            period="5y",  # 5 years of data
            interval="1d"  # Daily data
        )
        
        if yahoo_data:
            # Load data to database
            db_loader.load_stock_data(yahoo_data)
            logger.info(f"Successfully loaded data for {len(yahoo_data)} symbols to database")
            
            # Print summary
            for symbol, data in yahoo_data.items():
                logger.info(f"{symbol}: {len(data)} records from {data.index[0].date()} to {data.index[-1].date()}")
        else:
            logger.warning("No data collected from Yahoo Finance")
            
    except Exception as e:
        logger.error(f"Error collecting stock data: {str(e)}")
        raise


def collect_sample_data():
    """Collect a small sample of data for testing."""
    sample_symbols = ['AAPL', 'GOOGL', 'MSFT']
    logger.info(f"Collecting sample data for: {sample_symbols}")
    collect_stock_data(symbols=sample_symbols, days_back=30)


def collect_full_data():
    """Collect full dataset."""
    symbols = DATA_SOURCES['yahoo_finance']['symbols']
    logger.info(f"Collecting full dataset for: {symbols}")
    collect_stock_data(symbols=symbols, days_back=365*5)  # 5 years


def verify_data():
    """Verify that data was collected and stored correctly."""
    try:
        db_loader = DatabaseLoader("postgresql://postgres:password@localhost:5432/quant_finance")
        
        # Check stock prices
        query = """
            SELECT symbol, COUNT(*) as record_count, 
                   MIN(date) as earliest_date, 
                   MAX(date) as latest_date
            FROM stock_prices 
            GROUP BY symbol 
            ORDER BY symbol
        """
        
        result = db_loader.query_data(query)
        
        if not result.empty:
            logger.info("Data verification successful:")
            logger.info(f"Total symbols: {len(result)}")
            for _, row in result.iterrows():
                logger.info(f"  {row['symbol']}: {row['record_count']} records "
                          f"({row['earliest_date']} to {row['latest_date']})")
        else:
            logger.warning("No data found in database")
            
    except Exception as e:
        logger.error(f"Error verifying data: {str(e)}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect market data')
    parser.add_argument('--mode', choices=['sample', 'full'], default='sample',
                       help='Data collection mode: sample (3 symbols, 30 days) or full (all symbols, 5 years)')
    parser.add_argument('--verify', action='store_true',
                       help='Verify collected data')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'sample':
            collect_sample_data()
        else:
            collect_full_data()
        
        if args.verify:
            verify_data()
            
        logger.info("Data collection completed successfully!")
        
    except Exception as e:
        logger.error(f"Data collection failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
