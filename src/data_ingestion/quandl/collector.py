"""
Quandl data collector for financial and economic data.
"""
import pandas as pd
import quandl
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class QuandlCollector:
    """Collector for Quandl data."""
    
    def __init__(self, api_key: str, data_dir: Optional[Path] = None):
        """
        Initialize Quandl collector.
        
        Args:
            api_key: Quandl API key
            data_dir: Directory to save raw data files
        """
        self.api_key = api_key
        quandl.ApiConfig.api_key = api_key
        self.data_dir = data_dir or Path("data/raw/quandl")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_data(
        self, 
        dataset: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        collapse: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get data from Quandl dataset.
        
        Args:
            dataset: Quandl dataset code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            collapse: Data frequency (daily, weekly, monthly, quarterly, annual)
            
        Returns:
            DataFrame with Quandl data
        """
        try:
            logger.info(f"Collecting Quandl data for dataset {dataset}")
            
            # Get data from Quandl
            data = quandl.get(
                dataset,
                start_date=start_date,
                end_date=end_date,
                collapse=collapse
            )
            
            if data.empty:
                logger.warning(f"No data found for dataset {dataset}")
                return pd.DataFrame()
            
            # Add metadata
            data['dataset'] = dataset
            data['data_source'] = 'quandl'
            data['collected_at'] = datetime.now()
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting Quandl data for dataset {dataset}: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_data(
        self, 
        symbol: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get stock data from Quandl.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with stock data
        """
        dataset = f"WIKI/{symbol}"
        return self.get_data(dataset, start_date, end_date)
    
    def get_economic_data(self) -> Dict[str, pd.DataFrame]:
        """
        Get common economic datasets from Quandl.
        
        Returns:
            Dictionary with economic data
        """
        datasets = {
            'FRED/DGS10': '10-Year Treasury Rate',
            'FRED/UNRATE': 'Unemployment Rate',
            'FRED/CPIAUCSL': 'Consumer Price Index',
            'FRED/GDP': 'Gross Domestic Product',
            'FRED/FEDFUNDS': 'Federal Funds Rate',
            'CBOE/VIX': 'VIX Volatility Index',
            'OPEC/ORB': 'OPEC Oil Price',
            'LBMA/GOLD': 'Gold Price',
            'BUNDESBANK/BBK01_WT5511': 'German 10-Year Bond Yield'
        }
        
        data = {}
        start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        
        for dataset, description in datasets.items():
            try:
                logger.info(f"Collecting {description} ({dataset})")
                df = self.get_data(dataset, start_date=start_date)
                
                if not df.empty:
                    data[dataset] = df
                    
                    # Save to file
                    filename = f"{dataset.replace('/', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
                    filepath = self.data_dir / filename
                    df.to_csv(filepath)
                    logger.info(f"Saved {dataset} data to {filepath}")
                
            except Exception as e:
                logger.error(f"Error collecting {dataset}: {str(e)}")
                continue
        
        return data
    
    def search_datasets(self, query: str, page: int = 1) -> pd.DataFrame:
        """
        Search for Quandl datasets.
        
        Args:
            query: Search query
            page: Page number
            
        Returns:
            DataFrame with search results
        """
        try:
            results = quandl.search(query, page=page)
            return results
        except Exception as e:
            logger.error(f"Error searching Quandl datasets: {str(e)}")
            return pd.DataFrame()
    
    def get_dataset_info(self, dataset: str) -> Dict:
        """
        Get information about a Quandl dataset.
        
        Args:
            dataset: Quandl dataset code
            
        Returns:
            Dictionary with dataset information
        """
        try:
            info = quandl.Dataset(dataset).data()
            return info
        except Exception as e:
            logger.error(f"Error getting dataset info for {dataset}: {str(e)}")
            return {}
    
    def collect_batch_data(
        self, 
        datasets: List[str], 
        save_to_file: bool = True,
        start_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Collect data for multiple datasets.
        
        Args:
            datasets: List of Quandl dataset codes
            save_to_file: Whether to save data to files
            start_date: Start date for data collection
            
        Returns:
            Dictionary with dataset as key and DataFrame as value
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        
        data = {}
        
        for dataset in datasets:
            try:
                df = self.get_data(dataset, start_date=start_date)
                
                if not df.empty:
                    data[dataset] = df
                    
                    # Save to file if requested
                    if save_to_file:
                        filename = f"{dataset.replace('/', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
                        filepath = self.data_dir / filename
                        df.to_csv(filepath)
                        logger.info(f"Saved {dataset} data to {filepath}")
                
            except Exception as e:
                logger.error(f"Error collecting {dataset}: {str(e)}")
                continue
        
        return data
