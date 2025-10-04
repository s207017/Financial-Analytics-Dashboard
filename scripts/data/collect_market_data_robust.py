"""
Robust market data collection script with better error handling.
"""
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import time

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config.config import DATA_SOURCES
from etl.loaders.database_loader import DatabaseLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_stock_data_robust(symbols=None, days_back=365):
    """
    Collect stock data with robust error handling and retries.
    
    Args:
        symbols: List of stock symbols
        days_back: Number of days of historical data to collect
    """
    if symbols is None:
        symbols = DATA_SOURCES['yahoo_finance']['symbols']
    
    logger.info(f"Starting robust data collection for {len(symbols)} symbols")
    
    try:
        db_loader = DatabaseLoader("postgresql://postgres:password@localhost:5432/quant_finance")
        collected_data = {}
        
        for i, symbol in enumerate(symbols):
            logger.info(f"Collecting data for {symbol} ({i+1}/{len(symbols)})")
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Create ticker object
                    ticker = yf.Ticker(symbol)
                    
                    # Get historical data with shorter period first
                    hist = ticker.history(period="1y", interval="1d")
                    
                    if hist.empty:
                        logger.warning(f"No data found for {symbol} (attempt {attempt + 1})")
                        if attempt < max_retries - 1:
                            time.sleep(2)  # Wait before retry
                            continue
                        else:
                            break
                    
                    # Add metadata
                    hist['symbol'] = symbol
                    hist['data_source'] = 'yahoo_finance'
                    hist['collected_at'] = datetime.now()
                    
                    # Reset index to make date a column
                    hist = hist.reset_index()
                    
                    collected_data[symbol] = hist
                    logger.info(f"Successfully collected {len(hist)} records for {symbol}")
                    break
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(5)  # Wait longer before retry
                    else:
                        logger.error(f"Failed to collect data for {symbol} after {max_retries} attempts")
            
            # Small delay between symbols to avoid rate limiting
            time.sleep(1)
        
        if collected_data:
            # Load data to database
            db_loader.load_stock_data(collected_data)
            logger.info(f"Successfully loaded data for {len(collected_data)} symbols to database")
            
            # Print summary
            for symbol, data in collected_data.items():
                logger.info(f"{symbol}: {len(data)} records from {data['date'].min().date()} to {data['date'].max().date()}")
        else:
            logger.warning("No data collected from any symbols")
            
    except Exception as e:
        logger.error(f"Error in data collection: {str(e)}")
        raise


def create_sample_data():
    """Create sample data for testing when API fails."""
    logger.info("Creating sample data for testing...")
    
    try:
        db_loader = DatabaseLoader("postgresql://postgres:password@localhost:5432/quant_finance")
        
        # Generate sample data
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        
        sample_data = {}
        
        for symbol in symbols:
            # Generate realistic price data
            np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
            
            # Starting price
            start_price = 100 + np.random.uniform(50, 200)
            
            # Generate returns
            returns = np.random.normal(0.0005, 0.02, len(dates))
            
            # Calculate prices
            prices = [start_price]
            for ret in returns[1:]:
                prices.append(prices[-1] * (1 + ret))
            
            # Create DataFrame
            df = pd.DataFrame({
                'date': dates,
                'open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
                'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
                'close': prices,
                'adjusted_close': prices,
                'volume': np.random.randint(1000000, 10000000, len(dates)),
                'symbol': symbol,
                'data_source': 'sample_data',
                'collected_at': datetime.now()
            })
            
            sample_data[symbol] = df
        
        # Load sample data to database
        db_loader.load_stock_data(sample_data)
        logger.info(f"Successfully created and loaded sample data for {len(sample_data)} symbols")
        
        return sample_data
        
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        raise


def verify_data():
    """Verify that data was collected and stored correctly."""
    try:
        db_loader = DatabaseLoader("postgresql://postgres:password@localhost:5432/quant_finance")
        
        # Check stock prices
        query = """
            SELECT symbol, COUNT(*) as record_count, 
                   MIN(date) as earliest_date, 
                   MAX(date) as latest_date,
                   AVG(close) as avg_price
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
                          f"({row['earliest_date']} to {row['latest_date']}) "
                          f"Avg Price: ${row['avg_price']:.2f}")
        else:
            logger.warning("No data found in database")
            
    except Exception as e:
        logger.error(f"Error verifying data: {str(e)}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect market data')
    parser.add_argument('--mode', choices=['real', 'sample', 'create-sample'], default='real',
                       help='Data collection mode: real (from Yahoo Finance), sample (3 symbols), or create-sample (generate test data)')
    parser.add_argument('--verify', action='store_true',
                       help='Verify collected data')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'real':
            # Try to collect real data
            collect_stock_data_robust(['AAPL', 'GOOGL', 'MSFT'], days_back=365)
        elif args.mode == 'sample':
            # Try to collect real data for sample symbols
            collect_stock_data_robust(['AAPL', 'GOOGL', 'MSFT'], days_back=30)
        elif args.mode == 'create-sample':
            # Create sample data for testing
            create_sample_data()
        
        if args.verify:
            verify_data()
            
        logger.info("Data collection completed successfully!")
        
    except Exception as e:
        logger.error(f"Data collection failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
