"""
Database setup script for the quantitative finance pipeline.
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config.config import DATABASE_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DATABASE_CONFIG["name"],)
        )
        
        if cursor.fetchone():
            logger.info(f"Database '{DATABASE_CONFIG['name']}' already exists")
        else:
            # Create database
            cursor.execute(f"CREATE DATABASE {DATABASE_CONFIG['name']}")
            logger.info(f"Database '{DATABASE_CONFIG['name']}' created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise


def create_tables():
    """Create all necessary tables."""
    try:
        # Connect to the specific database
        conn = psycopg2.connect(
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            database=DATABASE_CONFIG["name"]
        )
        cursor = conn.cursor()
        
        # Create stock_prices table
        cursor.execute("""
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
        """)
        
        # Create economic_indicators table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS economic_indicators (
                id SERIAL PRIMARY KEY,
                series_id VARCHAR(50) NOT NULL,
                date DATE NOT NULL,
                value DECIMAL(15,6),
                data_source VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(series_id, date, data_source)
            )
        """)
        
        # Create portfolio_data table
        cursor.execute("""
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
        """)
        
        # Create risk_metrics table
        cursor.execute("""
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
        """)
        
        # Create technical_indicators table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS technical_indicators (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10) NOT NULL,
                date DATE NOT NULL,
                sma_20 DECIMAL(10,4),
                sma_50 DECIMAL(10,4),
                ema_12 DECIMAL(10,4),
                ema_26 DECIMAL(10,4),
                macd DECIMAL(10,6),
                macd_signal DECIMAL(10,6),
                rsi DECIMAL(5,2),
                bb_upper DECIMAL(10,4),
                bb_middle DECIMAL(10,4),
                bb_lower DECIMAL(10,4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date)
            )
        """)
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON stock_prices(symbol, date)",
            "CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(date)",
            "CREATE INDEX IF NOT EXISTS idx_economic_indicators_series_date ON economic_indicators(series_id, date)",
            "CREATE INDEX IF NOT EXISTS idx_economic_indicators_date ON economic_indicators(date)",
            "CREATE INDEX IF NOT EXISTS idx_portfolio_data_name_date ON portfolio_data(portfolio_name, date)",
            "CREATE INDEX IF NOT EXISTS idx_risk_metrics_name_date ON risk_metrics(portfolio_name, date)",
            "CREATE INDEX IF NOT EXISTS idx_technical_indicators_symbol_date ON technical_indicators(symbol, date)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        logger.info("All tables and indexes created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise


def test_connection():
    """Test database connection."""
    try:
        conn = psycopg2.connect(
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            database=DATABASE_CONFIG["name"]
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"Connected to PostgreSQL: {version[0]}")
        
        # Test table creation
        cursor.execute("SELECT COUNT(*) FROM stock_prices;")
        count = cursor.fetchone()[0]
        logger.info(f"Stock prices table has {count} records")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return False


def main():
    """Main setup function."""
    logger.info("Starting database setup...")
    
    try:
        # Step 1: Create database
        create_database()
        
        # Step 2: Create tables
        create_tables()
        
        # Step 3: Test connection
        if test_connection():
            logger.info("Database setup completed successfully!")
        else:
            logger.error("Database setup failed!")
            return False
            
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
