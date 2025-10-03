"""
Database loader for storing financial data in PostgreSQL.
"""
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from typing import Dict, List, Optional
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseLoader:
    """Database loader for financial data."""
    
    def __init__(self, database_url: str):
        """
        Initialize database loader.
        
        Args:
            database_url: PostgreSQL database URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            with self.engine.connect() as conn:
                # Stock prices table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS stock_prices (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(10) NOT NULL,
                        date DATE NOT NULL,
                        open DECIMAL(10,4),
                        high DECIMAL(10,4),
                        low DECIMAL(10,4),
                        close DECIMAL(10,4),
                        adjusted_close DECIMAL(10,4),
                        volume BIGINT,
                        data_source VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, date, data_source)
                    )
                """))
                
                # Economic indicators table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS economic_indicators (
                        id SERIAL PRIMARY KEY,
                        series_id VARCHAR(50) NOT NULL,
                        date DATE NOT NULL,
                        value DECIMAL(15,6),
                        data_source VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(series_id, date, data_source)
                    )
                """))
                
                # Portfolio data table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS portfolio_data (
                        id SERIAL PRIMARY KEY,
                        portfolio_name VARCHAR(100) NOT NULL,
                        date DATE NOT NULL,
                        symbol VARCHAR(10) NOT NULL,
                        weight DECIMAL(8,6),
                        returns DECIMAL(10,6),
                        value DECIMAL(15,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(portfolio_name, date, symbol)
                    )
                """))
                
                # Risk metrics table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS risk_metrics (
                        id SERIAL PRIMARY KEY,
                        portfolio_name VARCHAR(100) NOT NULL,
                        date DATE NOT NULL,
                        sharpe_ratio DECIMAL(10,6),
                        var_95 DECIMAL(10,6),
                        var_99 DECIMAL(10,6),
                        max_drawdown DECIMAL(10,6),
                        volatility DECIMAL(10,6),
                        beta DECIMAL(10,6),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(portfolio_name, date)
                    )
                """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON stock_prices(symbol, date)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_economic_indicators_series_date ON economic_indicators(series_id, date)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_portfolio_data_name_date ON portfolio_data(portfolio_name, date)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_risk_metrics_name_date ON risk_metrics(portfolio_name, date)"))
                
                conn.commit()
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    def load_stock_data(self, data_dict: Dict[str, pd.DataFrame], table_name: str = "stock_prices"):
        """
        Load stock data to database.
        
        Args:
            data_dict: Dictionary with symbol as key and DataFrame as value
            table_name: Target table name
        """
        try:
            for symbol, df in data_dict.items():
                if df.empty:
                    continue
                
                # Prepare data for database
                df_db = df.copy()
                df_db['symbol'] = symbol
                
                # Ensure date column is datetime
                if 'date' in df_db.columns:
                    df_db['date'] = pd.to_datetime(df_db['date']).dt.date
                elif df_db.index.name == 'date' or isinstance(df_db.index, pd.DatetimeIndex):
                    df_db = df_db.reset_index()
                    df_db['date'] = pd.to_datetime(df_db['date']).dt.date
                
                # Select relevant columns
                columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'adjusted_close', 'volume', 'data_source']
                available_columns = [col for col in columns if col in df_db.columns]
                df_db = df_db[available_columns]
                
                # Load to database
                df_db.to_sql(
                    table_name, 
                    self.engine, 
                    if_exists='append', 
                    index=False,
                    method='multi'
                )
                
                logger.info(f"Loaded {len(df_db)} records for {symbol} to {table_name}")
                
        except Exception as e:
            logger.error(f"Error loading stock data: {str(e)}")
            raise
    
    def load_economic_data(self, data_dict: Dict[str, pd.DataFrame], table_name: str = "economic_indicators"):
        """
        Load economic data to database.
        
        Args:
            data_dict: Dictionary with series_id as key and DataFrame as value
            table_name: Target table name
        """
        try:
            for series_id, df in data_dict.items():
                if df.empty:
                    continue
                
                # Prepare data for database
                df_db = df.copy()
                df_db['series_id'] = series_id
                
                # Ensure date column is datetime
                if 'date' in df_db.columns:
                    df_db['date'] = pd.to_datetime(df_db['date']).dt.date
                elif df_db.index.name == 'date' or isinstance(df_db.index, pd.DatetimeIndex):
                    df_db = df_db.reset_index()
                    df_db['date'] = pd.to_datetime(df_db['date']).dt.date
                
                # Select relevant columns
                columns = ['series_id', 'date', 'value', 'data_source']
                available_columns = [col for col in columns if col in df_db.columns]
                df_db = df_db[available_columns]
                
                # Load to database
                df_db.to_sql(
                    table_name, 
                    self.engine, 
                    if_exists='append', 
                    index=False,
                    method='multi'
                )
                
                logger.info(f"Loaded {len(df_db)} records for {series_id} to {table_name}")
                
        except Exception as e:
            logger.error(f"Error loading economic data: {str(e)}")
            raise
    
    def load_portfolio_data(self, portfolio_name: str, df: pd.DataFrame, table_name: str = "portfolio_data"):
        """
        Load portfolio data to database.
        
        Args:
            portfolio_name: Name of the portfolio
            df: Portfolio DataFrame
            table_name: Target table name
        """
        try:
            if df.empty:
                return
            
            # Prepare data for database
            df_db = df.copy()
            df_db['portfolio_name'] = portfolio_name
            
            # Ensure date column is datetime
            if 'date' in df_db.columns:
                df_db['date'] = pd.to_datetime(df_db['date']).dt.date
            elif df_db.index.name == 'date' or isinstance(df_db.index, pd.DatetimeIndex):
                df_db = df_db.reset_index()
                df_db['date'] = pd.to_datetime(df_db['date']).dt.date
            
            # Load to database
            df_db.to_sql(
                table_name, 
                self.engine, 
                if_exists='append', 
                index=False,
                method='multi'
            )
            
            logger.info(f"Loaded {len(df_db)} portfolio records for {portfolio_name}")
            
        except Exception as e:
            logger.error(f"Error loading portfolio data: {str(e)}")
            raise
    
    def load_risk_metrics(self, portfolio_name: str, df: pd.DataFrame, table_name: str = "risk_metrics"):
        """
        Load risk metrics to database.
        
        Args:
            portfolio_name: Name of the portfolio
            df: Risk metrics DataFrame
            table_name: Target table name
        """
        try:
            if df.empty:
                return
            
            # Prepare data for database
            df_db = df.copy()
            df_db['portfolio_name'] = portfolio_name
            
            # Ensure date column is datetime
            if 'date' in df_db.columns:
                df_db['date'] = pd.to_datetime(df_db['date']).dt.date
            elif df_db.index.name == 'date' or isinstance(df_db.index, pd.DatetimeIndex):
                df_db = df_db.reset_index()
                df_db['date'] = pd.to_datetime(df_db['date']).dt.date
            
            # Load to database
            df_db.to_sql(
                table_name, 
                self.engine, 
                if_exists='append', 
                index=False,
                method='multi'
            )
            
            logger.info(f"Loaded {len(df_db)} risk metrics records for {portfolio_name}")
            
        except Exception as e:
            logger.error(f"Error loading risk metrics: {str(e)}")
            raise
    
    def query_data(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            params: Optional list of parameters for the query
            
        Returns:
            Query results as DataFrame
        """
        try:
            with self.engine.connect() as conn:
                if params:
                    result = pd.read_sql(query, conn, params=params)
                else:
                    result = pd.read_sql(query, conn)
                return result
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def get_latest_data(self, table_name: str, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Get latest data from a table.
        
        Args:
            table_name: Table name
            symbol: Optional symbol filter
            
        Returns:
            Latest data as DataFrame
        """
        try:
            if symbol:
                query = f"""
                    SELECT * FROM {table_name} 
                    WHERE symbol = '{symbol}' 
                    ORDER BY date DESC 
                    LIMIT 100
                """
            else:
                query = f"""
                    SELECT * FROM {table_name} 
                    ORDER BY date DESC 
                    LIMIT 100
                """
            
            return self.query_data(query)
            
        except Exception as e:
            logger.error(f"Error getting latest data: {str(e)}")
            return pd.DataFrame()
