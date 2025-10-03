"""
Configuration management for the quantitative finance pipeline.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
LOGS_DIR = PROJECT_ROOT / "logs"

# Database configuration
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL", "postgresql://localhost:5432/quant_finance"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "name": os.getenv("DB_NAME", "quant_finance"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
}

# API Keys
API_KEYS = {
    "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY"),
    "quandl": os.getenv("QUANDL_API_KEY"),
    "fred": os.getenv("FRED_API_KEY"),
}

# AWS Configuration
AWS_CONFIG = {
    "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "region": os.getenv("AWS_REGION", "us-east-1"),
    "s3_bucket": os.getenv("S3_BUCKET", "quant-finance-data"),
}

# Application Configuration
APP_CONFIG = {
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "environment": os.getenv("ENVIRONMENT", "development"),
}

# Data sources configuration
DATA_SOURCES = {
    "yahoo_finance": {
        "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"],
        "period": "5y",
        "interval": "1d"
    },
    "alpha_vantage": {
        "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
        "function": "TIME_SERIES_DAILY_ADJUSTED"
    },
    "fred": {
        "series": ["DGS10", "DGS2", "UNRATE", "CPIAUCSL", "GDP"]
    }
}

# Portfolio configuration
PORTFOLIO_CONFIG = {
    "risk_free_rate": 0.02,
    "rebalance_frequency": "monthly",
    "max_weight": 0.3,
    "min_weight": 0.01
}
