"""
Setup database tables for stock filtering system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import DATABASE_CONFIG
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_stock_filtering_tables():
    """Create tables for stock filtering system"""
    
    # Create database connection
    engine = create_engine(
        f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@"
        f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['name']}"
    )
    
    try:
        with engine.connect() as conn:
            # Create stock_info table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stock_info (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL UNIQUE,
                    name VARCHAR(255),
                    sector VARCHAR(100),
                    industry VARCHAR(100),
                    market_cap BIGINT,
                    market_cap_category VARCHAR(20),
                    current_price DECIMAL(10,2),
                    previous_close DECIMAL(10,2),
                    day_change DECIMAL(10,2),
                    day_change_percent DECIMAL(8,4),
                    volume BIGINT,
                    avg_volume BIGINT,
                    pe_ratio DECIMAL(8,2),
                    forward_pe DECIMAL(8,2),
                    peg_ratio DECIMAL(8,2),
                    price_to_book DECIMAL(8,2),
                    price_to_sales DECIMAL(8,2),
                    dividend_yield DECIMAL(8,4),
                    dividend_rate DECIMAL(8,2),
                    beta DECIMAL(8,2),
                    debt_to_equity DECIMAL(8,2),
                    return_on_equity DECIMAL(8,4),
                    profit_margins DECIMAL(8,4),
                    revenue_growth DECIMAL(8,4),
                    earnings_growth DECIMAL(8,4),
                    week_52_high DECIMAL(10,2),
                    week_52_low DECIMAL(10,2),
                    enterprise_value BIGINT,
                    shares_outstanding BIGINT,
                    float_shares BIGINT,
                    short_ratio DECIMAL(8,2),
                    short_percent DECIMAL(8,4),
                    institutional_ownership DECIMAL(8,4),
                    insider_ownership DECIMAL(8,4),
                    analyst_recommendation DECIMAL(8,2),
                    target_price DECIMAL(10,2),
                    currency VARCHAR(10),
                    exchange VARCHAR(50),
                    country VARCHAR(50),
                    website VARCHAR(255),
                    business_summary TEXT,
                    employees INTEGER,
                    founded_year INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create stock_filter_history table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stock_filter_history (
                    id SERIAL PRIMARY KEY,
                    filter_name VARCHAR(100),
                    filter_criteria JSONB,
                    result_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes for better performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_stock_info_symbol ON stock_info(symbol);
                CREATE INDEX IF NOT EXISTS idx_stock_info_sector ON stock_info(sector);
                CREATE INDEX IF NOT EXISTS idx_stock_info_industry ON stock_info(industry);
                CREATE INDEX IF NOT EXISTS idx_stock_info_market_cap_category ON stock_info(market_cap_category);
                CREATE INDEX IF NOT EXISTS idx_stock_info_pe_ratio ON stock_info(pe_ratio);
                CREATE INDEX IF NOT EXISTS idx_stock_info_dividend_yield ON stock_info(dividend_yield);
                CREATE INDEX IF NOT EXISTS idx_stock_info_beta ON stock_info(beta);
                CREATE INDEX IF NOT EXISTS idx_stock_info_current_price ON stock_info(current_price);
                CREATE INDEX IF NOT EXISTS idx_stock_info_volume ON stock_info(volume);
            """))
            
            conn.commit()
            logger.info("Stock filtering tables created successfully")
            
    except Exception as e:
        logger.error(f"Error creating stock filtering tables: {str(e)}")
        raise

if __name__ == "__main__":
    setup_stock_filtering_tables()
