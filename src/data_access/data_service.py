"""
Data service for providing data to dashboard components.
"""
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from etl.loaders.database_loader import DatabaseLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataService:
    """Service class for accessing financial data from the database."""
    
    def __init__(self, db_url="postgresql://postgres:password@localhost:5432/quant_finance"):
        """Initialize the data service with database connection."""
        self.db_loader = DatabaseLoader(db_url)
        logger.info("DataService initialized")
    
    def get_stock_prices(self, symbols=None, start_date=None, end_date=None):
        """
        Get stock price data.
        
        Args:
            symbols: List of stock symbols (if None, returns all)
            start_date: Start date (if None, returns all)
            end_date: End date (if None, returns all)
        
        Returns:
            DataFrame with stock price data
        """
        try:
            query = "SELECT * FROM stock_prices WHERE 1=1"
            
            if symbols:
                symbol_list = "','".join(symbols)
                query += f" AND symbol IN ('{symbol_list}')"
            
            if start_date:
                query += f" AND date >= '{start_date}'"
            
            if end_date:
                query += f" AND date <= '{end_date}'"
            
            query += " ORDER BY date, symbol"
            
            data = self.db_loader.query_data(query)
            logger.info(f"Retrieved {len(data)} stock price records")
            return data
            
        except Exception as e:
            logger.error(f"Error getting stock prices: {str(e)}")
            return pd.DataFrame()
    
    def get_portfolio_performance(self, portfolio_name="equal_weight_portfolio", start_date=None, end_date=None):
        """
        Get portfolio performance data.
        
        Args:
            portfolio_name: Name of the portfolio
            start_date: Start date (if None, returns all)
            end_date: End date (if None, returns all)
        
        Returns:
            DataFrame with portfolio performance data
        """
        try:
            query = f"""
                SELECT date, symbol, weight, returns, value
                FROM portfolio_data 
                WHERE portfolio_name = '{portfolio_name}'
            """
            
            if start_date:
                query += f" AND date >= '{start_date}'"
            
            if end_date:
                query += f" AND date <= '{end_date}'"
            
            query += " ORDER BY date, symbol"
            
            data = self.db_loader.query_data(query)
            logger.info(f"Retrieved {len(data)} portfolio performance records")
            return data
            
        except Exception as e:
            logger.error(f"Error getting portfolio performance: {str(e)}")
            return pd.DataFrame()
    
    def get_risk_metrics(self, portfolio_name="equal_weight_portfolio"):
        """
        Get risk metrics for a portfolio.
        
        Args:
            portfolio_name: Name of the portfolio
        
        Returns:
            DataFrame with risk metrics
        """
        try:
            query = f"""
                SELECT portfolio_name, date, sharpe_ratio, var_95, var_99, 
                       max_drawdown, volatility, beta
                FROM risk_metrics 
                WHERE portfolio_name = '{portfolio_name}'
                ORDER BY date DESC
                LIMIT 1
            """
            
            data = self.db_loader.query_data(query)
            logger.info(f"Retrieved risk metrics for {portfolio_name}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting risk metrics: {str(e)}")
            return pd.DataFrame()
    
    def get_technical_indicators(self, symbol, start_date=None, end_date=None):
        """
        Get technical indicators for a symbol.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (if None, returns all)
            end_date: End date (if None, returns all)
        
        Returns:
            DataFrame with technical indicators
        """
        try:
            query = f"""
                SELECT date, symbol, sma_20, ema_12, ema_26, macd, 
                       macd_signal, rsi, bb_upper, bb_middle, bb_lower, bb_width
                FROM technical_indicators 
                WHERE symbol = '{symbol}'
            """
            
            if start_date:
                query += f" AND date >= '{start_date}'"
            
            if end_date:
                query += f" AND date <= '{end_date}'"
            
            query += " ORDER BY date"
            
            data = self.db_loader.query_data(query)
            logger.info(f"Retrieved {len(data)} technical indicator records for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting technical indicators: {str(e)}")
            return pd.DataFrame()
    
    def get_portfolio_summary(self, portfolio_name="equal_weight_portfolio"):
        """
        Get portfolio summary statistics.
        
        Args:
            portfolio_name: Name of the portfolio
        
        Returns:
            Dictionary with portfolio summary
        """
        try:
            # Get portfolio data
            portfolio_data = self.get_portfolio_performance(portfolio_name)
            
            if portfolio_data.empty:
                return {}
            
            # Calculate summary statistics
            summary = {
                'total_symbols': portfolio_data['symbol'].nunique(),
                'date_range': {
                    'start': portfolio_data['date'].min(),
                    'end': portfolio_data['date'].max()
                },
                'total_records': len(portfolio_data),
                'avg_daily_return': portfolio_data['returns'].mean(),
                'total_return': portfolio_data.groupby('symbol')['returns'].sum().mean(),
                'volatility': portfolio_data['returns'].std(),
                'symbols': portfolio_data['symbol'].unique().tolist()
            }
            
            # Get risk metrics
            risk_metrics = self.get_risk_metrics(portfolio_name)
            if not risk_metrics.empty:
                summary['risk_metrics'] = risk_metrics.iloc[0].to_dict()
            
            logger.info(f"Generated portfolio summary for {portfolio_name}")
            return summary
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {}
    
    def get_correlation_matrix(self, symbols=None, start_date=None, end_date=None):
        """
        Get correlation matrix for symbols.
        
        Args:
            symbols: List of stock symbols (if None, uses all available)
            start_date: Start date (if None, returns all)
            end_date: End date (if None, returns all)
        
        Returns:
            DataFrame with correlation matrix
        """
        try:
            # Get portfolio data
            portfolio_data = self.get_portfolio_performance(start_date=start_date, end_date=end_date)
            
            if portfolio_data.empty:
                return pd.DataFrame()
            
            # Filter symbols if specified
            if symbols:
                portfolio_data = portfolio_data[portfolio_data['symbol'].isin(symbols)]
            
            # Pivot to get returns by symbol
            returns_pivot = portfolio_data.pivot(index='date', columns='symbol', values='returns')
            
            # Calculate correlation matrix
            correlation_matrix = returns_pivot.corr()
            
            logger.info(f"Generated correlation matrix for {len(correlation_matrix)} symbols")
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"Error getting correlation matrix: {str(e)}")
            return pd.DataFrame()
    
    def get_available_symbols(self):
        """Get list of available symbols in the database."""
        try:
            query = "SELECT DISTINCT symbol FROM stock_prices ORDER BY symbol"
            data = self.db_loader.query_data(query)
            symbols = data['symbol'].tolist()
            logger.info(f"Retrieved {len(symbols)} available symbols")
            return symbols
        except Exception as e:
            logger.error(f"Error getting available symbols: {str(e)}")
            return []
    
    def get_available_portfolios(self):
        """Get list of available portfolios in the database."""
        try:
            query = "SELECT DISTINCT portfolio_name FROM portfolio_data ORDER BY portfolio_name"
            data = self.db_loader.query_data(query)
            portfolios = data['portfolio_name'].tolist()
            logger.info(f"Retrieved {len(portfolios)} available portfolios")
            return portfolios
        except Exception as e:
            logger.error(f"Error getting available portfolios: {str(e)}")
            return []


# Global data service instance
data_service = DataService()
