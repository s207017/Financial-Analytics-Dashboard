"""
Stock Data Collector for US Stocks with Comprehensive Financial Metrics
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import time
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class StockFilters:
    """Stock filtering criteria"""
    market_cap_categories: List[str] = None  # ['Large Cap', 'Mid Cap', 'Small Cap', 'Micro Cap']
    industries: List[str] = None
    sectors: List[str] = None
    pe_ratio_min: Optional[float] = None
    pe_ratio_max: Optional[float] = None
    peg_ratio_min: Optional[float] = None
    peg_ratio_max: Optional[float] = None
    dividend_yield_min: Optional[float] = None
    dividend_yield_max: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    volume_min: Optional[int] = None
    beta_min: Optional[float] = None
    beta_max: Optional[float] = None
    debt_to_equity_max: Optional[float] = None
    return_on_equity_min: Optional[float] = None
    profit_margin_min: Optional[float] = None

class StockDataCollector:
    """Collects comprehensive financial data for US stocks"""
    
    def __init__(self):
        self.market_cap_categories = {
            'Large Cap': (10_000_000_000, float('inf')),      # $10B+
            'Mid Cap': (2_000_000_000, 10_000_000_000),       # $2B - $10B
            'Small Cap': (300_000_000, 2_000_000_000),        # $300M - $2B
            'Micro Cap': (0, 300_000_000),                    # < $300M
            'Mega Cap ($100B+)': (100_000_000_000, float('inf')),  # $100B+
            'Large Cap ($10B+)': (10_000_000_000, float('inf')),   # $10B+
            'Mid Cap ($2B+)': (2_000_000_000, float('inf')),       # $2B+
            'Small Cap ($300M+)': (300_000_000, float('inf')),     # $300M+
            'Micro Cap ($50M+)': (50_000_000, float('inf')),       # $50M+
            'Nano Cap ($10M+)': (10_000_000, float('inf'))         # $10M+
        }
        
        # Popular US stock symbols across different sectors
        self.popular_stocks = [
            # Technology
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'CRM',
            # Healthcare
            'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN',
            # Financial
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SPGI', 'CB',
            # Consumer
            'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'COST',
            # Industrial
            'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'FDX', 'LMT', 'RTX', 'DE',
            # Energy
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PXD', 'MPC', 'VLO', 'PSX', 'KMI',
            # Utilities
            'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'PEG', 'WEC',
            # Real Estate
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'EXR', 'AVB', 'EQR', 'MAA', 'UDR',
            # Materials
            'LIN', 'APD', 'SHW', 'ECL', 'DD', 'DOW', 'FCX', 'NEM', 'PPG', 'VMC',
            # Communication
            'VZ', 'T', 'CMCSA', 'DIS', 'NFLX', 'CHTR', 'TMUS', 'DISH', 'SIRI', 'LUMN'
        ]
    
    def get_market_cap_category(self, market_cap: float) -> str:
        """Determine market cap category based on market cap value"""
        if pd.isna(market_cap) or market_cap <= 0:
            return 'Unknown'
        
        for category, (min_cap, max_cap) in self.market_cap_categories.items():
            if min_cap <= market_cap <= max_cap:
                return category
        
        return 'Unknown'
    
    def collect_stock_info(self, symbol: str) -> Optional[Dict]:
        """Collect comprehensive financial information for a single stock"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Basic information
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'market_cap_category': self.get_market_cap_category(info.get('marketCap', 0)),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'previous_close': info.get('previousClose', 0),
                'day_change': info.get('regularMarketChange', 0),
                'day_change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'dividend_rate': info.get('dividendRate', 0),
                'beta': info.get('beta', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'profit_margins': info.get('profitMargins', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float_shares': info.get('floatShares', 0),
                'short_ratio': info.get('shortRatio', 0),
                'short_percent': info.get('shortPercentOfFloat', 0),
                'institutional_ownership': info.get('institutionOwnership', 0),
                'insider_ownership': info.get('insiderOwnership', 0),
                'analyst_recommendation': info.get('recommendationMean', 0),
                'target_price': info.get('targetMeanPrice', 0),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', ''),
                'country': info.get('country', ''),
                'website': info.get('website', ''),
                'business_summary': info.get('longBusinessSummary', ''),
                'employees': info.get('fullTimeEmployees', 0),
                'founded_year': info.get('founded', 0),
                'last_updated': datetime.now().isoformat()
            }
            
            # Clean up None values
            for key, value in stock_data.items():
                if value is None:
                    stock_data[key] = 0 if isinstance(value, (int, float)) else ''
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error collecting data for {symbol}: {str(e)}")
            return None
    
    def collect_multiple_stocks(self, symbols: List[str], delay: float = 0.1) -> pd.DataFrame:
        """Collect data for multiple stocks with rate limiting"""
        all_data = []
        
        for i, symbol in enumerate(symbols):
            logger.info(f"Collecting data for {symbol} ({i+1}/{len(symbols)})")
            
            stock_data = self.collect_stock_info(symbol)
            if stock_data:
                all_data.append(stock_data)
            
            # Rate limiting to avoid API limits
            if i < len(symbols) - 1:
                time.sleep(delay)
        
        return pd.DataFrame(all_data)
    
    def get_available_filters(self, df: pd.DataFrame) -> Dict:
        """Get available filter options from the collected data"""
        if df.empty:
            return {}
        
        filters = {
            'market_cap_categories': sorted(df['market_cap_category'].unique().tolist()),
            'sectors': sorted(df['sector'].unique().tolist()),
            'industries': sorted(df['industry'].unique().tolist()),
            'pe_ratio_range': {
                'min': float(df['pe_ratio'].min()) if not df['pe_ratio'].isna().all() else 0,
                'max': float(df['pe_ratio'].max()) if not df['pe_ratio'].isna().all() else 100
            },
            'peg_ratio_range': {
                'min': float(df['peg_ratio'].min()) if not df['peg_ratio'].isna().all() else 0,
                'max': float(df['peg_ratio'].max()) if not df['peg_ratio'].isna().all() else 5
            },
            'dividend_yield_range': {
                'min': float(df['dividend_yield'].min()) if not df['dividend_yield'].isna().all() else 0,
                'max': float(df['dividend_yield'].max()) if not df['dividend_yield'].isna().all() else 0.1
            },
            'price_range': {
                'min': float(df['current_price'].min()) if not df['current_price'].isna().all() else 0,
                'max': float(df['current_price'].max()) if not df['current_price'].isna().all() else 1000
            },
            'beta_range': {
                'min': float(df['beta'].min()) if not df['beta'].isna().all() else 0,
                'max': float(df['beta'].max()) if not df['beta'].isna().all() else 3
            }
        }
        
        return filters
    
    def filter_stocks(self, df: pd.DataFrame, filters: StockFilters) -> pd.DataFrame:
        """Apply filters to the stock data"""
        if df.empty:
            return df
        
        filtered_df = df.copy()
        
        # Market cap categories
        if filters.market_cap_categories:
            filtered_df = filtered_df[filtered_df['market_cap_category'].isin(filters.market_cap_categories)]
        
        # Industries
        if filters.industries:
            filtered_df = filtered_df[filtered_df['industry'].isin(filters.industries)]
        
        # Sectors
        if filters.sectors:
            filtered_df = filtered_df[filtered_df['sector'].isin(filters.sectors)]
        
        # PE Ratio
        if filters.pe_ratio_min is not None:
            filtered_df = filtered_df[filtered_df['pe_ratio'] >= filters.pe_ratio_min]
        if filters.pe_ratio_max is not None:
            filtered_df = filtered_df[filtered_df['pe_ratio'] <= filters.pe_ratio_max]
        
        # PEG Ratio
        if filters.peg_ratio_min is not None:
            filtered_df = filtered_df[filtered_df['peg_ratio'] >= filters.peg_ratio_min]
        if filters.peg_ratio_max is not None:
            filtered_df = filtered_df[filtered_df['peg_ratio'] <= filters.peg_ratio_max]
        
        # Dividend Yield
        if filters.dividend_yield_min is not None:
            filtered_df = filtered_df[filtered_df['dividend_yield'] >= filters.dividend_yield_min]
        if filters.dividend_yield_max is not None:
            filtered_df = filtered_df[filtered_df['dividend_yield'] <= filters.dividend_yield_max]
        
        # Price
        if filters.price_min is not None:
            filtered_df = filtered_df[filtered_df['current_price'] >= filters.price_min]
        if filters.price_max is not None:
            filtered_df = filtered_df[filtered_df['current_price'] <= filters.price_max]
        
        # Volume
        if filters.volume_min is not None:
            filtered_df = filtered_df[filtered_df['volume'] >= filters.volume_min]
        
        # Beta
        if filters.beta_min is not None:
            filtered_df = filtered_df[filtered_df['beta'] >= filters.beta_min]
        if filters.beta_max is not None:
            filtered_df = filtered_df[filtered_df['beta'] <= filters.beta_max]
        
        # Debt to Equity
        if filters.debt_to_equity_max is not None:
            filtered_df = filtered_df[filtered_df['debt_to_equity'] <= filters.debt_to_equity_max]
        
        # Return on Equity
        if filters.return_on_equity_min is not None:
            filtered_df = filtered_df[filtered_df['return_on_equity'] >= filters.return_on_equity_min]
        
        # Profit Margin
        if filters.profit_margin_min is not None:
            filtered_df = filtered_df[filtered_df['profit_margins'] >= filters.profit_margin_min]
        
        return filtered_df
    
    def get_top_stocks_by_metric(self, df: pd.DataFrame, metric: str, top_n: int = 10) -> pd.DataFrame:
        """Get top N stocks by a specific metric"""
        if df.empty or metric not in df.columns:
            return pd.DataFrame()
        
        # Remove NaN values and sort
        valid_df = df.dropna(subset=[metric])
        return valid_df.nlargest(top_n, metric)
    
    def get_stock_screener_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary statistics for stock screening"""
        if df.empty:
            return {}
        
        summary = {
            'total_stocks': len(df),
            'market_cap_distribution': df['market_cap_category'].value_counts().to_dict(),
            'sector_distribution': df['sector'].value_counts().to_dict(),
            'industry_distribution': df['industry'].value_counts().to_dict(),
            'avg_pe_ratio': float(df['pe_ratio'].mean()) if not df['pe_ratio'].isna().all() else 0,
            'avg_dividend_yield': float(df['dividend_yield'].mean()) if not df['dividend_yield'].isna().all() else 0,
            'avg_beta': float(df['beta'].mean()) if not df['beta'].isna().all() else 0,
            'price_range': {
                'min': float(df['current_price'].min()) if not df['current_price'].isna().all() else 0,
                'max': float(df['current_price'].max()) if not df['current_price'].isna().all() else 0,
                'avg': float(df['current_price'].mean()) if not df['current_price'].isna().all() else 0
            }
        }
        
        return summary

