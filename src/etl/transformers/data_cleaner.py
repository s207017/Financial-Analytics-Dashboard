"""
Data cleaning and preprocessing transformers.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataCleaner:
    """Data cleaning and preprocessing utilities."""
    
    def __init__(self):
        """Initialize data cleaner."""
        pass
    
    def clean_missing_values(
        self, 
        df: pd.DataFrame, 
        method: str = "forward_fill",
        threshold: float = 0.1
    ) -> pd.DataFrame:
        """
        Clean missing values in DataFrame.
        
        Args:
            df: Input DataFrame
            method: Method for handling missing values (forward_fill, backward_fill, interpolate, drop)
            threshold: Maximum fraction of missing values allowed per column
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Check for columns with too many missing values
        missing_ratios = df_clean.isnull().sum() / len(df_clean)
        high_missing_cols = missing_ratios[missing_ratios > threshold].index
        
        if len(high_missing_cols) > 0:
            logger.warning(f"Dropping columns with >{threshold*100}% missing values: {list(high_missing_cols)}")
            df_clean = df_clean.drop(columns=high_missing_cols)
        
        # Handle remaining missing values
        if method == "forward_fill":
            df_clean = df_clean.fillna(method='ffill')
        elif method == "backward_fill":
            df_clean = df_clean.fillna(method='bfill')
        elif method == "interpolate":
            df_clean = df_clean.interpolate(method='linear')
        elif method == "drop":
            df_clean = df_clean.dropna()
        else:
            logger.warning(f"Unknown method {method}, using forward fill")
            df_clean = df_clean.fillna(method='ffill')
        
        # Fill any remaining NaN values with 0 for numeric columns
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
        
        return df_clean
    
    def remove_outliers(
        self, 
        df: pd.DataFrame, 
        columns: List[str],
        method: str = "iqr",
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Remove outliers from specified columns.
        
        Args:
            df: Input DataFrame
            columns: Columns to check for outliers
            method: Method for outlier detection (iqr, zscore)
            threshold: Threshold for outlier detection
            
        Returns:
            DataFrame with outliers removed
        """
        df_clean = df.copy()
        
        for col in columns:
            if col not in df_clean.columns:
                continue
                
            if method == "iqr":
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
                
            elif method == "zscore":
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                outliers = z_scores > threshold
                
            else:
                logger.warning(f"Unknown outlier detection method: {method}")
                continue
            
            outlier_count = outliers.sum()
            if outlier_count > 0:
                logger.info(f"Removing {outlier_count} outliers from column {col}")
                df_clean = df_clean[~outliers]
        
        return df_clean
    
    def standardize_data(
        self, 
        df: pd.DataFrame, 
        columns: List[str],
        method: str = "zscore"
    ) -> pd.DataFrame:
        """
        Standardize data in specified columns.
        
        Args:
            df: Input DataFrame
            columns: Columns to standardize
            method: Standardization method (zscore, minmax, robust)
            
        Returns:
            DataFrame with standardized columns
        """
        df_std = df.copy()
        
        for col in columns:
            if col not in df_std.columns:
                continue
                
            if method == "zscore":
                df_std[col] = (df_std[col] - df_std[col].mean()) / df_std[col].std()
            elif method == "minmax":
                df_std[col] = (df_std[col] - df_std[col].min()) / (df_std[col].max() - df_std[col].min())
            elif method == "robust":
                median = df_std[col].median()
                mad = np.median(np.abs(df_std[col] - median))
                df_std[col] = (df_std[col] - median) / mad
            else:
                logger.warning(f"Unknown standardization method: {method}")
        
        return df_std
    
    def align_time_series(
        self, 
        data_dict: Dict[str, pd.DataFrame],
        frequency: str = "D"
    ) -> Dict[str, pd.DataFrame]:
        """
        Align multiple time series to the same frequency and date range.
        
        Args:
            data_dict: Dictionary with symbol as key and DataFrame as value
            frequency: Target frequency (D, W, M, Q, Y)
            
        Returns:
            Dictionary with aligned time series
        """
        aligned_data = {}
        
        # Get common date range
        all_dates = []
        for symbol, df in data_dict.items():
            if not df.empty and 'date' in df.columns:
                all_dates.extend(df['date'].tolist())
        
        if not all_dates:
            logger.warning("No date columns found in data")
            return data_dict
        
        # Create common date range
        min_date = min(all_dates)
        max_date = max(all_dates)
        common_dates = pd.date_range(start=min_date, end=max_date, freq=frequency)
        
        # Align each time series
        for symbol, df in data_dict.items():
            if df.empty or 'date' not in df.columns:
                continue
                
            df_aligned = df.copy()
            df_aligned['date'] = pd.to_datetime(df_aligned['date'])
            df_aligned = df_aligned.set_index('date')
            
            # Resample to target frequency
            df_aligned = df_aligned.resample(frequency).last()
            
            # Reindex to common date range
            df_aligned = df_aligned.reindex(common_dates)
            
            # Reset index to get date column back
            df_aligned = df_aligned.reset_index()
            df_aligned.rename(columns={'index': 'date'}, inplace=True)
            
            aligned_data[symbol] = df_aligned
        
        return aligned_data


class FinancialDataTransformer:
    """Specialized transformer for financial data."""
    
    def __init__(self):
        """Initialize financial data transformer."""
        self.cleaner = DataCleaner()
    
    def calculate_returns(
        self, 
        df: pd.DataFrame, 
        price_column: str = "close",
        return_type: str = "simple"
    ) -> pd.DataFrame:
        """
        Calculate returns from price data.
        
        Args:
            df: DataFrame with price data
            price_column: Column name containing prices
            return_type: Type of returns (simple, log)
            
        Returns:
            DataFrame with returns added
        """
        df_returns = df.copy()
        
        if return_type == "simple":
            df_returns['returns'] = df_returns[price_column].pct_change()
        elif return_type == "log":
            df_returns['returns'] = np.log(df_returns[price_column] / df_returns[price_column].shift(1))
        else:
            raise ValueError(f"Unknown return type: {return_type}")
        
        return df_returns
    
    def calculate_technical_indicators(
        self, 
        df: pd.DataFrame,
        price_column: str = "close",
        volume_column: str = "volume"
    ) -> pd.DataFrame:
        """
        Calculate technical indicators.
        
        Args:
            df: DataFrame with OHLCV data
            price_column: Column name for price
            volume_column: Column name for volume
            
        Returns:
            DataFrame with technical indicators
        """
        df_indicators = df.copy()
        
        # Moving averages
        df_indicators['sma_20'] = df_indicators[price_column].rolling(window=20).mean()
        df_indicators['sma_50'] = df_indicators[price_column].rolling(window=50).mean()
        df_indicators['ema_12'] = df_indicators[price_column].ewm(span=12).mean()
        df_indicators['ema_26'] = df_indicators[price_column].ewm(span=26).mean()
        
        # MACD
        df_indicators['macd'] = df_indicators['ema_12'] - df_indicators['ema_26']
        df_indicators['macd_signal'] = df_indicators['macd'].ewm(span=9).mean()
        df_indicators['macd_histogram'] = df_indicators['macd'] - df_indicators['macd_signal']
        
        # RSI
        delta = df_indicators[price_column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df_indicators['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df_indicators['bb_middle'] = df_indicators[price_column].rolling(window=20).mean()
        bb_std = df_indicators[price_column].rolling(window=20).std()
        df_indicators['bb_upper'] = df_indicators['bb_middle'] + (bb_std * 2)
        df_indicators['bb_lower'] = df_indicators['bb_middle'] - (bb_std * 2)
        df_indicators['bb_width'] = df_indicators['bb_upper'] - df_indicators['bb_lower']
        
        # Volume indicators
        if volume_column in df_indicators.columns:
            df_indicators['volume_sma'] = df_indicators[volume_column].rolling(window=20).mean()
            df_indicators['volume_ratio'] = df_indicators[volume_column] / df_indicators['volume_sma']
        
        return df_indicators
    
    def calculate_volatility(
        self, 
        df: pd.DataFrame, 
        returns_column: str = "returns",
        window: int = 30
    ) -> pd.DataFrame:
        """
        Calculate volatility measures.
        
        Args:
            df: DataFrame with returns data
            returns_column: Column name for returns
            window: Rolling window for volatility calculation
            
        Returns:
            DataFrame with volatility measures
        """
        df_vol = df.copy()
        
        # Rolling volatility (annualized)
        df_vol['volatility'] = df_vol[returns_column].rolling(window=window).std() * np.sqrt(252)
        
        # GARCH volatility (simplified)
        df_vol['volatility_garch'] = df_vol[returns_column].rolling(window=window).std()
        
        return df_vol
    
    def calculate_correlation_matrix(
        self, 
        data_dict: Dict[str, pd.DataFrame],
        returns_column: str = "returns"
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for multiple assets.
        
        Args:
            data_dict: Dictionary with symbol as key and DataFrame as value
            returns_column: Column name for returns
            
        Returns:
            Correlation matrix DataFrame
        """
        returns_data = {}
        
        for symbol, df in data_dict.items():
            if returns_column in df.columns:
                returns_data[symbol] = df[returns_column]
        
        if not returns_data:
            logger.warning("No returns data found for correlation calculation")
            return pd.DataFrame()
        
        returns_df = pd.DataFrame(returns_data)
        correlation_matrix = returns_df.corr()
        
        return correlation_matrix
