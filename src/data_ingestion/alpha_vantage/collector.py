"""
Alpha Vantage data collector for financial market data.
"""
import pandas as pd
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AlphaVantageCollector:
    """Collector for Alpha Vantage data."""
    
    def __init__(self, api_key: str, data_dir: Optional[Path] = None):
        """
        Initialize Alpha Vantage collector.
        
        Args:
            api_key: Alpha Vantage API key
            data_dir: Directory to save raw data files
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.data_dir = data_dir or Path("data/raw/alpha_vantage")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _make_request(self, params: Dict) -> Dict:
        """
        Make API request to Alpha Vantage.
        
        Args:
            params: Request parameters
            
        Returns:
            API response as dictionary
        """
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                raise Exception(f"API Error: {data['Error Message']}")
            if 'Note' in data:
                raise Exception(f"API Note: {data['Note']}")
            
            return data
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise
    
    def get_daily_adjusted(self, symbol: str, outputsize: str = "compact") -> pd.DataFrame:
        """
        Get daily adjusted stock data.
        
        Args:
            symbol: Stock symbol
            outputsize: compact or full
            
        Returns:
            DataFrame with daily adjusted data
        """
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': outputsize
        }
        
        try:
            data = self._make_request(params)
            time_series = data.get('Time Series (Daily)', {})
            
            if not time_series:
                logger.warning(f"No time series data found for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns
            df.columns = ['open', 'high', 'low', 'close', 'adjusted_close', 'volume', 'dividend_amount', 'split_coefficient']
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Add metadata
            df['symbol'] = symbol
            df['data_source'] = 'alpha_vantage'
            df['collected_at'] = datetime.now()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting daily adjusted data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_company_overview(self, symbol: str) -> Dict:
        """
        Get company overview information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company overview
        """
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        try:
            data = self._make_request(params)
            return data
        except Exception as e:
            logger.error(f"Error getting company overview for {symbol}: {str(e)}")
            return {}
    
    def get_earnings(self, symbol: str) -> Dict:
        """
        Get earnings data for a company.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with earnings data
        """
        params = {
            'function': 'EARNINGS',
            'symbol': symbol
        }
        
        try:
            data = self._make_request(params)
            return data
        except Exception as e:
            logger.error(f"Error getting earnings for {symbol}: {str(e)}")
            return {}
    
    def get_technical_indicators(
        self, 
        symbol: str, 
        function: str = "SMA", 
        interval: str = "daily", 
        time_period: int = 20,
        series_type: str = "close"
    ) -> pd.DataFrame:
        """
        Get technical indicators.
        
        Args:
            symbol: Stock symbol
            function: Technical indicator function (SMA, EMA, RSI, etc.)
            interval: Time interval
            time_period: Time period for calculation
            series_type: Price series type (close, open, high, low)
            
        Returns:
            DataFrame with technical indicator data
        """
        params = {
            'function': function,
            'symbol': symbol,
            'interval': interval,
            'time_period': time_period,
            'series_type': series_type
        }
        
        try:
            data = self._make_request(params)
            key = f"Technical Analysis: {function}"
            time_series = data.get(key, {})
            
            if not time_series:
                logger.warning(f"No technical indicator data found for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Add metadata
            df['symbol'] = symbol
            df['indicator'] = function
            df['data_source'] = 'alpha_vantage'
            df['collected_at'] = datetime.now()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting technical indicators for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def collect_batch_data(
        self, 
        symbols: List[str], 
        save_to_file: bool = True,
        delay: float = 12.0
    ) -> Dict[str, pd.DataFrame]:
        """
        Collect data for multiple symbols with rate limiting.
        
        Args:
            symbols: List of stock symbols
            save_to_file: Whether to save data to files
            delay: Delay between requests (seconds)
            
        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        data = {}
        
        for i, symbol in enumerate(symbols):
            try:
                logger.info(f"Collecting Alpha Vantage data for {symbol} ({i+1}/{len(symbols)})")
                
                # Get daily adjusted data
                df = self.get_daily_adjusted(symbol)
                
                if not df.empty:
                    data[symbol] = df
                    
                    # Save to file if requested
                    if save_to_file:
                        filename = f"{symbol}_daily_adjusted_{datetime.now().strftime('%Y%m%d')}.csv"
                        filepath = self.data_dir / filename
                        df.to_csv(filepath)
                        logger.info(f"Saved data for {symbol} to {filepath}")
                
                # Rate limiting - Alpha Vantage allows 5 calls per minute for free tier
                if i < len(symbols) - 1:  # Don't delay after the last request
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {str(e)}")
                continue
        
        return data
