"""
Utility functions for the dashboard application.
"""
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from .config import (
    DEFAULT_START_DATE, DEFAULT_END_DATE, DEFAULT_ANALYSIS_PERIOD_DAYS,
    ERROR_MESSAGES, SUCCESS_MESSAGES, VALIDATION_RULES,
    SHARPE_COLOR_MAPPING, CHART_COLORS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations and provides a clean interface."""
    
    def __init__(self, portfolio_service=None, database_available: bool = False):
        self.portfolio_service = portfolio_service
        self.database_available = database_available
    
    def get_all_portfolios(self) -> List[Dict[str, Any]]:
        """Get all portfolios from the database."""
        if not self.database_available or not self.portfolio_service:
            logger.warning("Database not available")
            return []
        
        try:
            return self.portfolio_service.get_all_portfolios()
        except Exception as e:
            logger.error(f"Error fetching portfolios: {e}")
            return []
    
    def get_portfolio_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific portfolio by name."""
        portfolios = self.get_all_portfolios()
        for portfolio in portfolios:
            if portfolio.get("name") == name:
                return portfolio
        return None
    
    def calculate_portfolio_analytics(self, symbols: List[str], weights: List[float], 
                                    start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Calculate portfolio analytics."""
        if not self.database_available or not self.portfolio_service:
            return {"error": ERROR_MESSAGES["database_unavailable"]}
        
        try:
            start_date = start_date or DEFAULT_START_DATE
            end_date = end_date or DEFAULT_END_DATE
            
            return self.portfolio_service.calculate_portfolio_analytics(
                symbols=symbols,
                weights=weights,
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            logger.error(f"Error calculating portfolio analytics: {e}")
            return {"error": str(e)}


class PortfolioCalculator:
    """Handles portfolio calculations and formatting."""
    
    @staticmethod
    def calculate_portfolio_return(symbols: List[str], weights: List[float], 
                                 start_date: str = None, end_date: str = None,
                                 db_manager: DatabaseManager = None) -> str:
        """Calculate portfolio return with proper error handling."""
        if not db_manager or not db_manager.database_available:
            return ERROR_MESSAGES["data_unavailable"]
        
        try:
            analytics = db_manager.calculate_portfolio_analytics(
                symbols=symbols, weights=weights, 
                start_date=start_date, end_date=end_date
            )
            
            if "error" in analytics:
                return ERROR_MESSAGES["data_unavailable"]
            
            return analytics.get("total_return", ERROR_MESSAGES["data_unavailable"])
        except Exception as e:
            logger.error(f"Error calculating portfolio return: {e}")
            return ERROR_MESSAGES["data_unavailable"]
    
    @staticmethod
    def format_return_display(return_value: Any) -> str:
        """Format return value for display."""
        if isinstance(return_value, (int, float)):
            return f"{return_value:.1%}"
        return str(return_value)
    
    @staticmethod
    def format_assets_with_percentages(portfolio: Dict[str, Any]) -> str:
        """Format portfolio assets with percentages."""
        if not portfolio or "symbols" not in portfolio or "weights" not in portfolio:
            return "No assets"
        
        symbols = portfolio["symbols"]
        weights = portfolio["weights"]
        
        if len(symbols) != len(weights):
            return "Invalid portfolio data"
        
        formatted_assets = []
        for symbol, weight in zip(symbols, weights):
            formatted_assets.append(f"{symbol} ({weight:.1%})")
        
        return ", ".join(formatted_assets)


class ValidationHelper:
    """Handles validation logic."""
    
    @staticmethod
    def validate_stock_symbols(symbols: List[str]) -> Tuple[List[str], List[str]]:
        """Validate stock symbols and return valid and invalid lists."""
        if not symbols:
            return [], []
        
        valid_symbols = []
        invalid_symbols = []
        
        for symbol in symbols:
            symbol = symbol.strip().upper()
            if symbol and len(symbol) <= 10 and symbol.isalpha():
                valid_symbols.append(symbol)
            else:
                invalid_symbols.append(symbol)
        
        return valid_symbols, invalid_symbols
    
    @staticmethod
    def validate_portfolio_weights(weights: List[float]) -> bool:
        """Validate portfolio weights."""
        if not weights:
            return False
        
        # Check if weights sum to approximately 1.0
        total_weight = sum(weights)
        return abs(total_weight - 1.0) < 0.01
    
    @staticmethod
    def validate_portfolio_value(value: float) -> bool:
        """Validate portfolio value."""
        return (VALIDATION_RULES["min_portfolio_value"] <= value <= 
                VALIDATION_RULES["max_portfolio_value"])


class ChartHelper:
    """Helper functions for chart creation and styling."""
    
    @staticmethod
    def get_color_for_portfolio(index: int) -> str:
        """Get color for portfolio based on index."""
        return CHART_COLORS[index % len(CHART_COLORS)]
    
    @staticmethod
    def get_sharpe_color(sharpe_ratio: float) -> str:
        """Get color based on Sharpe ratio."""
        for level, config in SHARPE_COLOR_MAPPING.items():
            if sharpe_ratio >= config["threshold"]:
                return config["color"]
        return "danger"
    
    @staticmethod
    def create_empty_figure(message: str = "No data available") -> 'go.Figure':
        """Create an empty figure with a message."""
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white'
        )
        return fig


class DateHelper:
    """Helper functions for date operations."""
    
    @staticmethod
    def get_analysis_date_range(days: int = DEFAULT_ANALYSIS_PERIOD_DAYS) -> Tuple[str, str]:
        """Get start and end dates for analysis."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return start_date, end_date
    
    @staticmethod
    def format_date_range(start_date: str, end_date: str) -> str:
        """Format date range for display."""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').strftime('%b %d, %Y')
            end = datetime.strptime(end_date, '%Y-%m-%d').strftime('%b %d, %Y')
            return f"{start} - {end}"
        except ValueError:
            return f"{start_date} - {end_date}"


class ErrorHandler:
    """Centralized error handling."""
    
    @staticmethod
    def handle_database_error(error: Exception, operation: str = "database operation") -> str:
        """Handle database errors consistently."""
        logger.error(f"Database error during {operation}: {error}")
        return ERROR_MESSAGES["database_unavailable"]
    
    @staticmethod
    def handle_calculation_error(error: Exception, operation: str = "calculation") -> str:
        """Handle calculation errors consistently."""
        logger.error(f"Calculation error during {operation}: {error}")
        return ERROR_MESSAGES["calculation_error"]
    
    @staticmethod
    def handle_validation_error(error: Exception, field: str = "field") -> str:
        """Handle validation errors consistently."""
        logger.error(f"Validation error for {field}: {error}")
        return f"Invalid {field}"


def ensure_pandas_series(data: Any) -> pd.Series:
    """Ensure data is a pandas Series for calculations."""
    if isinstance(data, pd.Series):
        return data
    elif isinstance(data, (list, np.ndarray)):
        return pd.Series(data)
    else:
        raise ValueError(f"Cannot convert {type(data)} to pandas Series")


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default
