"""
FRED (Federal Reserve Economic Data) collector for macroeconomic data.
"""
import pandas as pd
from fredapi import Fred
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FREDCollector:
    """Collector for FRED economic data."""
    
    def __init__(self, api_key: str, data_dir: Optional[Path] = None):
        """
        Initialize FRED collector.
        
        Args:
            api_key: FRED API key
            data_dir: Directory to save raw data files
        """
        self.api_key = api_key
        self.fred = Fred(api_key=api_key)
        self.data_dir = data_dir or Path("data/raw/fred")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_series(
        self, 
        series_id: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get economic data series from FRED.
        
        Args:
            series_id: FRED series ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency (d, w, m, q, a)
            
        Returns:
            DataFrame with economic data
        """
        try:
            logger.info(f"Collecting FRED data for series {series_id}")
            
            # Get data from FRED
            data = self.fred.get_series(
                series_id, 
                start=start_date, 
                end=end_date,
                frequency=frequency
            )
            
            if data.empty:
                logger.warning(f"No data found for series {series_id}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[series_id])
            df.index.name = 'date'
            df.reset_index(inplace=True)
            
            # Add metadata
            df['series_id'] = series_id
            df['data_source'] = 'fred'
            df['collected_at'] = datetime.now()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting FRED data for series {series_id}: {str(e)}")
            return pd.DataFrame()
    
    def get_series_info(self, series_id: str) -> Dict:
        """
        Get information about a FRED series.
        
        Args:
            series_id: FRED series ID
            
        Returns:
            Dictionary with series information
        """
        try:
            info = self.fred.get_series_info(series_id)
            return info
        except Exception as e:
            logger.error(f"Error getting series info for {series_id}: {str(e)}")
            return {}
    
    def search_series(self, search_text: str, limit: int = 20) -> pd.DataFrame:
        """
        Search for FRED series.
        
        Args:
            search_text: Search text
            limit: Maximum number of results
            
        Returns:
            DataFrame with search results
        """
        try:
            results = self.fred.search(search_text, limit=limit)
            return results
        except Exception as e:
            logger.error(f"Error searching FRED series: {str(e)}")
            return pd.DataFrame()
    
    def get_economic_indicators(self) -> Dict[str, pd.DataFrame]:
        """
        Get common economic indicators.
        
        Returns:
            Dictionary with economic indicators data
        """
        indicators = {
            'DGS10': '10-Year Treasury Constant Maturity Rate',
            'DGS2': '2-Year Treasury Constant Maturity Rate',
            'UNRATE': 'Unemployment Rate',
            'CPIAUCSL': 'Consumer Price Index for All Urban Consumers',
            'GDP': 'Gross Domestic Product',
            'FEDFUNDS': 'Federal Funds Effective Rate',
            'DEXUSEU': 'U.S. / Euro Foreign Exchange Rate',
            'DEXJPUS': 'Japanese Yen to U.S. Dollar Spot Exchange Rate',
            'VIXCLS': 'CBOE Volatility Index',
            'DCOILWTICO': 'Crude Oil Prices: West Texas Intermediate'
        }
        
        data = {}
        start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        
        for series_id, description in indicators.items():
            try:
                logger.info(f"Collecting {description} ({series_id})")
                df = self.get_series(series_id, start_date=start_date)
                
                if not df.empty:
                    data[series_id] = df
                    
                    # Save to file
                    filename = f"{series_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                    filepath = self.data_dir / filename
                    df.to_csv(filepath, index=False)
                    logger.info(f"Saved {series_id} data to {filepath}")
                
            except Exception as e:
                logger.error(f"Error collecting {series_id}: {str(e)}")
                continue
        
        return data
    
    def get_recession_data(self) -> pd.DataFrame:
        """
        Get US recession data.
        
        Returns:
            DataFrame with recession periods
        """
        try:
            # US recession indicator
            recession_data = self.fred.get_series('USREC', start='1854-12-01')
            
            if recession_data.empty:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(recession_data, columns=['recession'])
            df.index.name = 'date'
            df.reset_index(inplace=True)
            
            # Add metadata
            df['series_id'] = 'USREC'
            df['data_source'] = 'fred'
            df['collected_at'] = datetime.now()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting recession data: {str(e)}")
            return pd.DataFrame()
    
    def collect_macro_data(
        self, 
        series_list: List[str], 
        save_to_file: bool = True,
        start_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Collect multiple economic series.
        
        Args:
            series_list: List of FRED series IDs
            save_to_file: Whether to save data to files
            start_date: Start date for data collection
            
        Returns:
            Dictionary with series_id as key and DataFrame as value
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        
        data = {}
        
        for series_id in series_list:
            try:
                df = self.get_series(series_id, start_date=start_date)
                
                if not df.empty:
                    data[series_id] = df
                    
                    # Save to file if requested
                    if save_to_file:
                        filename = f"{series_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                        filepath = self.data_dir / filename
                        df.to_csv(filepath, index=False)
                        logger.info(f"Saved {series_id} data to {filepath}")
                
            except Exception as e:
                logger.error(f"Error collecting {series_id}: {str(e)}")
                continue
        
        return data
