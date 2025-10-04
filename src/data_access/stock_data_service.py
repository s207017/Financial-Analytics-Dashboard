#!/usr/bin/env python3
"""
Stock Data Service with Redis Caching
Handles fetching, caching, and storing stock data dynamically.
"""

import os
import sys
import json
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import redis
from sqlalchemy import create_engine, text
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class StockDataService:
    """Service for fetching, caching, and storing stock data."""
    
    def __init__(self):
        """Initialize the stock data service with database and Redis connections."""
        self.logger = logging.getLogger(__name__)
        
        # Database connection
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/quant_finance')
        self.engine = create_engine(self.db_url)
        
        # Redis connection
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        
        # API configuration
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.yahoo_finance_enabled = True  # Free API
        
        # Cache settings
        self.cache_ttl = 3600  # 1 hour for stock data
        self.rate_limit_delay = 0.2  # 200ms between API calls
        
    def check_redis_connection(self) -> bool:
        """Check if Redis is available."""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            self.logger.warning(f"Redis not available: {e}")
            return False
    
    def get_cached_data(self, symbol: str, data_type: str = "daily") -> Optional[Dict]:
        """Get cached stock data from Redis."""
        if not self.check_redis_connection():
            return None
            
        try:
            cache_key = f"stock:{symbol}:{data_type}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            self.logger.error(f"Error getting cached data for {symbol}: {e}")
        return None
    
    def cache_data(self, symbol: str, data: Dict, data_type: str = "daily", ttl: int = None) -> bool:
        """Cache stock data in Redis."""
        if not self.check_redis_connection():
            return False
            
        try:
            cache_key = f"stock:{symbol}:{data_type}"
            ttl = ttl or self.cache_ttl
            self.redis_client.setex(cache_key, ttl, json.dumps(data))
            return True
        except Exception as e:
            self.logger.error(f"Error caching data for {symbol}: {e}")
            return False
    
    def get_stock_data_from_db(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Get stock data from PostgreSQL database."""
        try:
            query = "SELECT date, open, high, low, close, volume FROM stock_prices WHERE symbol = :symbol"
            params = {"symbol": symbol}
            
            if start_date:
                query += " AND date >= :start_date"
                params["start_date"] = start_date
            if end_date:
                query += " AND date <= :end_date"
                params["end_date"] = end_date
                
            query += " ORDER BY date"
            
            with self.engine.connect() as conn:
                df = pd.read_sql(text(query), conn, params=params)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                return df
        except Exception as e:
            self.logger.error(f"Error getting stock data from DB for {symbol}: {e}")
            return None
    
    def fetch_from_alpha_vantage(self, symbol: str) -> Optional[Dict]:
        """Fetch stock data from Alpha Vantage API."""
        if not self.alpha_vantage_key:
            self.logger.warning("Alpha Vantage API key not configured")
            return None
            
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key,
                'outputsize': 'full'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'Error Message' in data:
                self.logger.error(f"Alpha Vantage error for {symbol}: {data['Error Message']}")
                return None
                
            if 'Note' in data:
                self.logger.warning(f"Alpha Vantage rate limit for {symbol}: {data['Note']}")
                return None
                
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                self.logger.warning(f"No time series data for {symbol}")
                return None
                
            # Convert to our format
            stock_data = []
            for date_str, values in time_series.items():
                stock_data.append({
                    'date': date_str,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            
            return {
                'symbol': symbol,
                'data': stock_data,
                'source': 'alpha_vantage',
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching from Alpha Vantage for {symbol}: {e}")
            return None
    
    def fetch_from_yahoo_finance(self, symbol: str) -> Optional[Dict]:
        """Fetch stock data from Yahoo Finance (using yfinance library)."""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="max")
            
            if hist.empty:
                self.logger.warning(f"No data from Yahoo Finance for {symbol}")
                return None
            
            # Convert to our format
            stock_data = []
            for date, row in hist.iterrows():
                stock_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            return {
                'symbol': symbol,
                'data': stock_data,
                'source': 'yahoo_finance',
                'fetched_at': datetime.now().isoformat()
            }
            
        except ImportError:
            self.logger.warning("yfinance not installed, skipping Yahoo Finance")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching from Yahoo Finance for {symbol}: {e}")
            return None
    
    def store_stock_data(self, symbol: str, stock_data: List[Dict]) -> bool:
        """Store stock data in PostgreSQL database."""
        try:
            with self.engine.connect() as conn:
                # Create table if it doesn't exist
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    date DATE NOT NULL,
                    open DECIMAL(10,2),
                    high DECIMAL(10,2),
                    low DECIMAL(10,2),
                    close DECIMAL(10,2),
                    volume BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                );
                CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON stock_prices(symbol, date);
                """
                conn.execute(text(create_table_sql))
                conn.commit()
                
                # Insert data (upsert)
                insert_sql = """
                INSERT INTO stock_prices (symbol, date, open, high, low, close, volume)
                VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
                ON CONFLICT (symbol, date) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume
                """
                
                for data_point in stock_data:
                    conn.execute(text(insert_sql), {
                        'symbol': symbol,
                        'date': data_point['date'],
                        'open': data_point['open'],
                        'high': data_point['high'],
                        'low': data_point['low'],
                        'close': data_point['close'],
                        'volume': data_point['volume']
                    })
                
                conn.commit()
                self.logger.info(f"Stored {len(stock_data)} data points for {symbol}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing stock data for {symbol}: {e}")
            return False
    
    def fetch_and_store_stock_data(self, symbol: str, force_refresh: bool = False) -> bool:
        """Fetch stock data and store it in database with Redis caching."""
        symbol = symbol.upper()
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = self.get_cached_data(symbol)
            if cached_data:
                self.logger.info(f"Using cached data for {symbol}")
                return True
        
        # Check if we already have recent data in database
        if not force_refresh:
            recent_data = self.get_stock_data_from_db(
                symbol, 
                start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            )
            if recent_data is not None and not recent_data.empty:
                self.logger.info(f"Recent data already exists for {symbol}")
                # Cache the metadata
                self.cache_data(symbol, {
                    'symbol': symbol,
                    'last_updated': datetime.now().isoformat(),
                    'data_points': len(recent_data)
                })
                return True
        
        # Fetch from APIs
        stock_data = None
        
        # Try Yahoo Finance first (free)
        if self.yahoo_finance_enabled:
            self.logger.info(f"Fetching {symbol} from Yahoo Finance...")
            stock_data = self.fetch_from_yahoo_finance(symbol)
            time.sleep(self.rate_limit_delay)
        
        # Fallback to Alpha Vantage if Yahoo Finance fails
        if not stock_data and self.alpha_vantage_key:
            self.logger.info(f"Fetching {symbol} from Alpha Vantage...")
            stock_data = self.fetch_from_alpha_vantage(symbol)
            time.sleep(self.rate_limit_delay)
        
        if not stock_data or not stock_data.get('data'):
            self.logger.error(f"Failed to fetch data for {symbol}")
            return False
        
        # Store in database
        success = self.store_stock_data(symbol, stock_data['data'])
        
        if success:
            # Cache the metadata
            self.cache_data(symbol, {
                'symbol': symbol,
                'last_updated': stock_data['fetched_at'],
                'data_points': len(stock_data['data']),
                'source': stock_data['source']
            })
            self.logger.info(f"Successfully fetched and stored data for {symbol}")
        
        return success
    
    def ensure_stock_data_available(self, symbols: List[str]) -> Dict[str, bool]:
        """Ensure stock data is available for all symbols."""
        results = {}
        
        for symbol in symbols:
            symbol = symbol.upper()
            try:
                success = self.fetch_and_store_stock_data(symbol)
                results[symbol] = success
            except Exception as e:
                self.logger.error(f"Error ensuring data for {symbol}: {e}")
                results[symbol] = False
        
        return results
    
    def get_available_symbols(self) -> List[str]:
        """Get list of symbols that have data in the database."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT DISTINCT symbol FROM stock_prices ORDER BY symbol"))
                return [row[0] for row in result]
        except Exception as e:
            self.logger.error(f"Error getting available symbols: {e}")
            return []
    
    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Get stock data (from cache, database, or fetch if needed)."""
        symbol = symbol.upper()
        
        # Try database first
        df = self.get_stock_data_from_db(symbol, start_date, end_date)
        
        # If no data or data is too old, try to fetch
        if df is None or df.empty:
            self.logger.info(f"No data found for {symbol}, attempting to fetch...")
            if self.fetch_and_store_stock_data(symbol):
                df = self.get_stock_data_from_db(symbol, start_date, end_date)
        
        return df

# Global instance
STOCK_DATA_SERVICE = None

def get_stock_data_service() -> StockDataService:
    """Get the global stock data service instance."""
    global STOCK_DATA_SERVICE
    if STOCK_DATA_SERVICE is None:
        STOCK_DATA_SERVICE = StockDataService()
    return STOCK_DATA_SERVICE

if __name__ == "__main__":
    # Test the service
    service = StockDataService()
    
    # Test with a few symbols
    test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    results = service.ensure_stock_data_available(test_symbols)
    
    print("Stock Data Fetching Results:")
    for symbol, success in results.items():
        print(f"  {symbol}: {'✅' if success else '❌'}")
    
    # Show available symbols
    available = service.get_available_symbols()
    print(f"\nAvailable symbols in database: {len(available)}")
    print(f"First 10: {available[:10]}")
