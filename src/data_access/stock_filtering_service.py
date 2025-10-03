"""
Stock Filtering Service for database operations
"""

import pandas as pd
import json
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, text
import logging
from config.config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class StockFilteringService:
    """Service for stock filtering operations"""
    
    def __init__(self):
        self.engine = create_engine(
            f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@"
            f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['name']}"
        )
    
    def get_all_stocks(self) -> pd.DataFrame:
        """Get all stocks from database"""
        try:
            query = "SELECT * FROM stock_info ORDER BY market_cap DESC"
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Error getting all stocks: {str(e)}")
            return pd.DataFrame()
    
    def get_stocks_by_filters(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Get stocks based on filter criteria"""
        try:
            base_query = "SELECT * FROM stock_info WHERE 1=1"
            params = []
            
            # Market cap categories
            if filters.get('market_cap_categories'):
                categories = "','".join(filters['market_cap_categories'])
                base_query += f" AND market_cap_category IN ('{categories}')"
            
            # Sectors
            if filters.get('sectors'):
                sectors = "','".join(filters['sectors'])
                base_query += f" AND sector IN ('{sectors}')"
            
            # Industries
            if filters.get('industries'):
                industries = "','".join(filters['industries'])
                base_query += f" AND industry IN ('{industries}')"
            
            # PE Ratio
            if filters.get('pe_ratio_min') is not None:
                base_query += f" AND pe_ratio >= {filters['pe_ratio_min']}"
            if filters.get('pe_ratio_max') is not None:
                base_query += f" AND pe_ratio <= {filters['pe_ratio_max']}"
            
            # PEG Ratio
            if filters.get('peg_ratio_min') is not None:
                base_query += f" AND peg_ratio >= {filters['peg_ratio_min']}"
            if filters.get('peg_ratio_max') is not None:
                base_query += f" AND peg_ratio <= {filters['peg_ratio_max']}"
            
            # Dividend Yield
            if filters.get('dividend_yield_min') is not None:
                base_query += f" AND dividend_yield >= {filters['dividend_yield_min']}"
            if filters.get('dividend_yield_max') is not None:
                base_query += f" AND dividend_yield <= {filters['dividend_yield_max']}"
            
            # Price
            if filters.get('price_min') is not None:
                base_query += f" AND current_price >= {filters['price_min']}"
            if filters.get('price_max') is not None:
                base_query += f" AND current_price <= {filters['price_max']}"
            
            # Volume
            if filters.get('volume_min') is not None:
                base_query += f" AND volume >= {filters['volume_min']}"
            
            # Beta
            if filters.get('beta_min') is not None:
                base_query += f" AND beta >= {filters['beta_min']}"
            if filters.get('beta_max') is not None:
                base_query += f" AND beta <= {filters['beta_max']}"
            
            # Debt to Equity
            if filters.get('debt_to_equity_max') is not None:
                base_query += f" AND debt_to_equity <= {filters['debt_to_equity_max']}"
            
            # Return on Equity
            if filters.get('return_on_equity_min') is not None:
                base_query += f" AND return_on_equity >= {filters['return_on_equity_min']}"
            
            # Profit Margin
            if filters.get('profit_margin_min') is not None:
                base_query += f" AND profit_margins >= {filters['profit_margin_min']}"
            
            # Order by market cap
            base_query += " ORDER BY market_cap DESC"
            
            return pd.read_sql(base_query, self.engine)
            
        except Exception as e:
            logger.error(f"Error filtering stocks: {str(e)}")
            return pd.DataFrame()
    
    def get_available_filters(self) -> Dict[str, Any]:
        """Get available filter options"""
        try:
            # Get unique values for categorical filters
            sectors_query = "SELECT DISTINCT sector FROM stock_info WHERE sector IS NOT NULL ORDER BY sector"
            industries_query = "SELECT DISTINCT industry FROM stock_info WHERE industry IS NOT NULL ORDER BY industry"
            categories_query = "SELECT DISTINCT market_cap_category FROM stock_info WHERE market_cap_category IS NOT NULL ORDER BY market_cap_category"
            
            sectors = pd.read_sql(sectors_query, self.engine)['sector'].tolist()
            industries = pd.read_sql(industries_query, self.engine)['industry'].tolist()
            categories = pd.read_sql(categories_query, self.engine)['market_cap_category'].tolist()
            
            # Get ranges for numerical filters
            ranges_query = """
                SELECT 
                    MIN(pe_ratio) as pe_min, MAX(pe_ratio) as pe_max,
                    MIN(peg_ratio) as peg_min, MAX(peg_ratio) as peg_max,
                    MIN(dividend_yield) as div_min, MAX(dividend_yield) as div_max,
                    MIN(current_price) as price_min, MAX(current_price) as price_max,
                    MIN(beta) as beta_min, MAX(beta) as beta_max
                FROM stock_info 
                WHERE pe_ratio IS NOT NULL AND peg_ratio IS NOT NULL 
                AND dividend_yield IS NOT NULL AND current_price IS NOT NULL 
                AND beta IS NOT NULL
            """
            
            ranges_df = pd.read_sql(ranges_query, self.engine)
            if not ranges_df.empty:
                ranges = ranges_df.iloc[0]
            else:
                # Default ranges if no data
                ranges = pd.Series({
                    'pe_min': 0, 'pe_max': 100,
                    'peg_min': 0, 'peg_max': 5,
                    'div_min': 0, 'div_max': 0.1,
                    'price_min': 0, 'price_max': 1000,
                    'beta_min': 0, 'beta_max': 3
                })
            
            return {
                'market_cap_categories': categories,
                'sectors': sectors,
                'industries': industries,
                'pe_ratio_range': {'min': float(ranges['pe_min']), 'max': float(ranges['pe_max'])},
                'peg_ratio_range': {'min': float(ranges['peg_min']), 'max': float(ranges['peg_max'])},
                'dividend_yield_range': {'min': float(ranges['div_min']), 'max': float(ranges['div_max'])},
                'price_range': {'min': float(ranges['price_min']), 'max': float(ranges['price_min'])},
                'beta_range': {'min': float(ranges['beta_min']), 'max': float(ranges['beta_max'])}
            }
            
        except Exception as e:
            logger.error(f"Error getting available filters: {str(e)}")
            return {}
    
    def get_stock_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all stocks"""
        try:
            summary_query = """
                SELECT 
                    COUNT(*) as total_stocks,
                    COUNT(DISTINCT sector) as total_sectors,
                    COUNT(DISTINCT industry) as total_industries,
                    AVG(pe_ratio) as avg_pe_ratio,
                    AVG(dividend_yield) as avg_dividend_yield,
                    AVG(beta) as avg_beta,
                    AVG(current_price) as avg_price,
                    SUM(market_cap) as total_market_cap
                FROM stock_info
            """
            
            summary = pd.read_sql(summary_query, self.engine).iloc[0]
            
            # Get distribution data
            cap_dist_query = "SELECT market_cap_category, COUNT(*) as count FROM stock_info GROUP BY market_cap_category"
            cap_dist = pd.read_sql(cap_dist_query, self.engine)
            
            sector_dist_query = "SELECT sector, COUNT(*) as count FROM stock_info GROUP BY sector ORDER BY count DESC"
            sector_dist = pd.read_sql(sector_dist_query, self.engine)
            
            return {
                'total_stocks': int(summary['total_stocks']),
                'total_sectors': int(summary['total_sectors']),
                'total_industries': int(summary['total_industries']),
                'avg_pe_ratio': float(summary['avg_pe_ratio']) if summary['avg_pe_ratio'] else 0,
                'avg_dividend_yield': float(summary['avg_dividend_yield']) if summary['avg_dividend_yield'] else 0,
                'avg_beta': float(summary['avg_beta']) if summary['avg_beta'] else 0,
                'avg_price': float(summary['avg_price']) if summary['avg_price'] else 0,
                'total_market_cap': float(summary['total_market_cap']) if summary['total_market_cap'] else 0,
                'market_cap_distribution': cap_dist.set_index('market_cap_category')['count'].to_dict(),
                'sector_distribution': sector_dist.set_index('sector')['count'].to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting stock summary: {str(e)}")
            return {}
    
    def get_top_stocks_by_metric(self, metric: str, top_n: int = 10) -> pd.DataFrame:
        """Get top N stocks by a specific metric"""
        try:
            query = f"""
                SELECT symbol, name, {metric}, sector, industry, market_cap_category, current_price
                FROM stock_info 
                WHERE {metric} IS NOT NULL 
                ORDER BY {metric} DESC 
                LIMIT {top_n}
            """
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Error getting top stocks by {metric}: {str(e)}")
            return pd.DataFrame()
    
    def save_filter_history(self, filter_name: str, filter_criteria: Dict, result_count: int):
        """Save filter history for tracking"""
        try:
            query = """
                INSERT INTO stock_filter_history (filter_name, filter_criteria, result_count)
                VALUES (%s, %s, %s)
            """
            with self.engine.connect() as conn:
                conn.execute(text(query), (filter_name, json.dumps(filter_criteria), result_count))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving filter history: {str(e)}")
    
    def get_filter_history(self, limit: int = 10) -> pd.DataFrame:
        """Get recent filter history"""
        try:
            query = f"""
                SELECT filter_name, filter_criteria, result_count, created_at
                FROM stock_filter_history 
                ORDER BY created_at DESC 
                LIMIT {limit}
            """
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Error getting filter history: {str(e)}")
            return pd.DataFrame()
