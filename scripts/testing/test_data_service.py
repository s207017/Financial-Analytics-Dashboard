"""
Test script for the data service.
"""
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from data_access.data_service import DataService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_data_service():
    """Test the data service functionality."""
    logger.info("Testing DataService...")
    
    try:
        # Initialize data service
        data_service = DataService()
        
        # Test 1: Get available symbols
        logger.info("Test 1: Getting available symbols...")
        symbols = data_service.get_available_symbols()
        logger.info(f"Available symbols: {symbols}")
        
        # Test 2: Get stock prices
        logger.info("Test 2: Getting stock prices...")
        stock_prices = data_service.get_stock_prices(symbols=symbols[:2])  # First 2 symbols
        logger.info(f"Retrieved {len(stock_prices)} stock price records")
        if not stock_prices.empty:
            logger.info(f"Date range: {stock_prices['date'].min()} to {stock_prices['date'].max()}")
        
        # Test 3: Get portfolio performance
        logger.info("Test 3: Getting portfolio performance...")
        portfolio_data = data_service.get_portfolio_performance()
        logger.info(f"Retrieved {len(portfolio_data)} portfolio records")
        
        # Test 4: Get risk metrics
        logger.info("Test 4: Getting risk metrics...")
        risk_metrics = data_service.get_risk_metrics()
        logger.info(f"Risk metrics: {risk_metrics.to_dict('records') if not risk_metrics.empty else 'No data'}")
        
        # Test 5: Get portfolio summary
        logger.info("Test 5: Getting portfolio summary...")
        summary = data_service.get_portfolio_summary()
        logger.info(f"Portfolio summary: {summary}")
        
        # Test 6: Get correlation matrix
        logger.info("Test 6: Getting correlation matrix...")
        correlation_matrix = data_service.get_correlation_matrix()
        logger.info(f"Correlation matrix shape: {correlation_matrix.shape}")
        if not correlation_matrix.empty:
            logger.info(f"Correlation matrix:\n{correlation_matrix}")
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    test_data_service()
