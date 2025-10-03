"""
Setup database tables for portfolio management system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import DATABASE_CONFIG
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_portfolio_tables():
    """Create tables for portfolio management system"""
    
    # Create database connection
    engine = create_engine(
        f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@"
        f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['name']}"
    )
    
    try:
        with engine.connect() as conn:
            # Create portfolios table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    description TEXT,
                    symbols JSONB NOT NULL,
                    weights JSONB NOT NULL,
                    strategy VARCHAR(100) DEFAULT 'Custom',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create portfolio_analytics table for storing calculated analytics
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS portfolio_analytics (
                    id SERIAL PRIMARY KEY,
                    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
                    analytics_date DATE DEFAULT CURRENT_DATE,
                    total_return DECIMAL(10,4),
                    annualized_return DECIMAL(10,4),
                    sharpe_ratio DECIMAL(10,4),
                    sortino_ratio DECIMAL(10,4),
                    portfolio_volatility DECIMAL(10,4),
                    max_drawdown DECIMAL(10,4),
                    var_95 DECIMAL(10,4),
                    cvar_95 DECIMAL(10,4),
                    beta DECIMAL(10,4),
                    diversification_ratio DECIMAL(10,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create portfolio_backtests table for storing backtest results
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS portfolio_backtests (
                    id SERIAL PRIMARY KEY,
                    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    rebalance_frequency VARCHAR(20) DEFAULT 'monthly',
                    initial_value DECIMAL(15,2) DEFAULT 10000,
                    final_value DECIMAL(15,2),
                    total_return DECIMAL(10,4),
                    annualized_return DECIMAL(10,4),
                    max_value DECIMAL(15,2),
                    min_value DECIMAL(15,2),
                    backtest_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes for better performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_portfolios_name ON portfolios(name);
                CREATE INDEX IF NOT EXISTS idx_portfolios_created_at ON portfolios(created_at);
                CREATE INDEX IF NOT EXISTS idx_portfolio_analytics_portfolio_id ON portfolio_analytics(portfolio_id);
                CREATE INDEX IF NOT EXISTS idx_portfolio_analytics_date ON portfolio_analytics(analytics_date);
                CREATE INDEX IF NOT EXISTS idx_portfolio_backtests_portfolio_id ON portfolio_backtests(portfolio_id);
                CREATE INDEX IF NOT EXISTS idx_portfolio_backtests_dates ON portfolio_backtests(start_date, end_date);
            """))
            
            conn.commit()
            logger.info("Portfolio management tables created successfully")
            
    except Exception as e:
        logger.error(f"Error creating portfolio tables: {str(e)}")
        raise

if __name__ == "__main__":
    setup_portfolio_tables()

