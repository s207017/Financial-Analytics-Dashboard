"""
Configuration constants and settings for the dashboard application.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Dashboard Configuration
DASHBOARD_TITLE = "Quantitative Finance Pipeline Dashboard"
DASHBOARD_THEME = "BOOTSTRAP"

# Date Configuration
DEFAULT_START_DATE = "2023-01-01"
DEFAULT_END_DATE = datetime.now().strftime("%Y-%m-%d")
DEFAULT_ANALYSIS_PERIOD_DAYS = 365

# Portfolio Configuration
DEFAULT_PORTFOLIO_VALUE = 100000
DEFAULT_STRATEGY = "Balanced"
SUPPORTED_STRATEGIES = ["Conservative", "Balanced", "Growth", "Aggressive", "Custom"]

# Risk Analysis Configuration
RISK_METRICS = {
    "sharpe": "Sharpe Ratio",
    "volatility": "Volatility", 
    "var_95": "VaR (95%)"
}

DEFAULT_RISK_METRIC = "sharpe"
ROLLING_WINDOW_DAYS = 30

# Chart Configuration
CHART_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
]

CHART_HEIGHT = 500
CHART_HEIGHT_SMALL = 400

# Performance Metrics Configuration
PERFORMANCE_METRICS = [
    "Total Return", "Annualized Return", "Volatility", 
    "Sharpe Ratio", "Max Drawdown", "Beta", "Alpha"
]

# Error Messages
ERROR_MESSAGES = {
    "database_unavailable": "Database not available",
    "no_portfolios": "No portfolios found",
    "invalid_symbols": "Invalid stock symbols",
    "data_unavailable": "Data Unavailable",
    "loading_error": "Error loading data",
    "calculation_error": "Error calculating metrics"
}

# Success Messages
SUCCESS_MESSAGES = {
    "portfolio_created": "Portfolio created successfully",
    "portfolio_updated": "Portfolio updated successfully",
    "data_fetched": "Data fetched successfully"
}

# Loading Messages
LOADING_MESSAGES = {
    "portfolios": "Loading portfolios...",
    "risk_metrics": "Loading risk metrics...",
    "performance_data": "Loading performance data...",
    "stock_data": "Fetching stock data..."
}

# Tab Configuration
TABS = {
    "portfolio_overview": {
        "id": "portfolio-tab",
        "label": "Portfolio Overview"
    },
    "portfolio_management": {
        "id": "portfolio-mgmt-tab", 
        "label": "Portfolio Management"
    },
    "risk_analysis": {
        "id": "risk-tab",
        "label": "Risk Analysis"
    },
    "performance_metrics": {
        "id": "performance-tab",
        "label": "Performance Metrics"
    }
}

# Database Configuration
DATABASE_CONFIG = {
    "connection_timeout": 30,
    "max_retries": 3,
    "retry_delay": 1
}

# API Configuration
API_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "rate_limit_delay": 1
}

# Validation Rules
VALIDATION_RULES = {
    "min_portfolio_value": 1000,
    "max_portfolio_value": 10000000,
    "min_weight": 0.01,
    "max_weight": 1.0,
    "max_symbols": 50,
    "min_symbols": 1
}

# Chart Layout Configuration
CHART_LAYOUT = {
    "title_font_size": 16,
    "axis_title_font_size": 14,
    "legend_font_size": 12,
    "hover_mode": "x unified",
    "margin": {"l": 50, "r": 50, "t": 50, "b": 50}
}

# Color Schemes
COLOR_SCHEMES = {
    "success": "success",
    "warning": "warning", 
    "danger": "danger",
    "info": "info",
    "primary": "primary"
}

# Sharpe Ratio Color Mapping
SHARPE_COLOR_MAPPING = {
    "excellent": {"threshold": 2.0, "color": "success"},
    "good": {"threshold": 1.0, "color": "success"},
    "average": {"threshold": 0.5, "color": "warning"},
    "poor": {"threshold": 0.0, "color": "warning"},
    "negative": {"threshold": -float('inf'), "color": "danger"}
}
