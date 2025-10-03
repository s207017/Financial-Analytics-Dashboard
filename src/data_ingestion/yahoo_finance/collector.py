"""
Yahoo Finance data collector for stock market data.
"""
import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class YahooFinanceCollector:
    """Collector for Yahoo Finance data."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize Yahoo Finance collector.
        
        Args:
            data_dir: Directory to save raw data files
        """
        self.data_dir = data_dir or Path("data/raw/yahoo_finance")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_data(
        self, 
        symbols: List[str], 
        period: str = "5y", 
        interval: str = "1d",
        save_to_file: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Collect stock data for given symbols.
        
        Args:
            symbols: List of stock symbols
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            save_to_file: Whether to save data to files
            
        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        data = {}
        
        for symbol in symbols:
            try:
                logger.info(f"Collecting data for {symbol}")
                ticker = yf.Ticker(symbol)
                
                # Get historical data
                hist_data = ticker.history(period=period, interval=interval)
                
                if hist_data.empty:
                    logger.warning(f"No data found for {symbol}")
                    continue
                
                # Add metadata
                hist_data['symbol'] = symbol
                hist_data['data_source'] = 'yahoo_finance'
                hist_data['collected_at'] = datetime.now()
                
                data[symbol] = hist_data
                
                # Save to file if requested
                if save_to_file:
                    filename = f"{symbol}_{period}_{interval}_{datetime.now().strftime('%Y%m%d')}.csv"
                    filepath = self.data_dir / filename
                    hist_data.to_csv(filepath)
                    logger.info(f"Saved data for {symbol} to {filepath}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {str(e)}")
                continue
        
        return data
    
    def get_company_info(self, symbol: str) -> Dict:
        """
        Get company information for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info
        except Exception as e:
            logger.error(f"Error getting company info for {symbol}: {str(e)}")
            return {}
    
    def get_dividends(self, symbol: str, period: str = "5y") -> pd.DataFrame:
        """
        Get dividend data for a symbol.
        
        Args:
            symbol: Stock symbol
            period: Data period
            
        Returns:
            DataFrame with dividend data
        """
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends
            return dividends
        except Exception as e:
            logger.error(f"Error getting dividends for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_splits(self, symbol: str) -> pd.DataFrame:
        """
        Get stock split data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            DataFrame with split data
        """
        try:
            ticker = yf.Ticker(symbol)
            splits = ticker.splits
            return splits
        except Exception as e:
            logger.error(f"Error getting splits for {symbol}: {str(e)}")
            return pd.DataFrame()
