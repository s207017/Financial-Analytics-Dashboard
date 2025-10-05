"""
Main pipeline script for the quantitative finance pipeline.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent))

from config.config import DATABASE_CONFIG, DATA_SOURCES, API_KEYS
from data_ingestion.yahoo_finance.collector import YahooFinanceCollector
from data_ingestion.alpha_vantage.collector import AlphaVantageCollector
from data_ingestion.fred.collector import FREDCollector
from data_ingestion.quandl.collector import QuandlCollector
from etl.transformers.data_cleaner import FinancialDataTransformer
from etl.loaders.database_loader import DatabaseLoader
from analytics.portfolio_optimization.optimizer import PortfolioOptimizer
from analytics.risk_metrics.calculator import RiskCalculator
from ml.regression.return_predictor import ReturnPredictor
from ml.clustering.asset_clusterer import AssetClusterer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)

# Start metrics exporter
try:
    from monitoring.metrics_exporter import start_metrics_exporter
    start_metrics_exporter(port=8000, collection_interval=30)
    logging.info("Metrics exporter started on port 8000")
except Exception as e:
    logging.warning(f"Failed to start metrics exporter: {e}")
logger = logging.getLogger(__name__)


class QuantitativeFinancePipeline:
    """Main pipeline class for quantitative finance analysis."""
    
    def __init__(self):
        """Initialize the pipeline."""
        self.data_collectors = {}
        self.transformer = FinancialDataTransformer()
        self.db_loader = None
        self.portfolio_optimizer = PortfolioOptimizer()
        self.risk_calculator = RiskCalculator()
        self.return_predictor = ReturnPredictor()
        self.asset_clusterer = AssetClusterer()
        
        # Initialize data collectors
        self._initialize_collectors()
        
        # Initialize database connection
        self._initialize_database()
    
    def _initialize_collectors(self):
        """Initialize data collectors."""
        try:
            # Yahoo Finance (no API key required)
            self.data_collectors['yahoo'] = YahooFinanceCollector()
            logger.info("Yahoo Finance collector initialized")
            
            # Alpha Vantage
            if API_KEYS.get('alpha_vantage'):
                self.data_collectors['alpha_vantage'] = AlphaVantageCollector(API_KEYS['alpha_vantage'])
                logger.info("Alpha Vantage collector initialized")
            
            # FRED
            if API_KEYS.get('fred'):
                self.data_collectors['fred'] = FREDCollector(API_KEYS['fred'])
                logger.info("FRED collector initialized")
            
            # Quandl
            if API_KEYS.get('quandl'):
                self.data_collectors['quandl'] = QuandlCollector(API_KEYS['quandl'])
                logger.info("Quandl collector initialized")
                
        except Exception as e:
            logger.error(f"Error initializing data collectors: {str(e)}")
    
    def _initialize_database(self):
        """Initialize database connection."""
        try:
            self.db_loader = DatabaseLoader(DATABASE_CONFIG["url"])
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    def collect_data(self, symbols: list = None, days_back: int = 365):
        """
        Collect data from all sources.
        
        Args:
            symbols: List of symbols to collect (if None, uses default)
            days_back: Number of days to collect data for
        """
        if symbols is None:
            symbols = DATA_SOURCES['yahoo_finance']['symbols']
        
        logger.info(f"Starting data collection for {len(symbols)} symbols")
        
        # Collect stock data from Yahoo Finance
        if 'yahoo' in self.data_collectors:
            try:
                logger.info("Collecting Yahoo Finance data...")
                yahoo_data = self.data_collectors['yahoo'].collect_data(
                    symbols=symbols,
                    period="5y",
                    interval="1d"
                )
                
                if yahoo_data and self.db_loader:
                    self.db_loader.load_stock_data(yahoo_data)
                    logger.info(f"Loaded {len(yahoo_data)} symbols to database")
                
            except Exception as e:
                logger.error(f"Error collecting Yahoo Finance data: {str(e)}")
        
        # Collect economic data from FRED
        if 'fred' in self.data_collectors:
            try:
                logger.info("Collecting FRED economic data...")
                fred_data = self.data_collectors['fred'].get_economic_indicators()
                
                if fred_data and self.db_loader:
                    self.db_loader.load_economic_data(fred_data)
                    logger.info(f"Loaded {len(fred_data)} economic indicators to database")
                
            except Exception as e:
                logger.error(f"Error collecting FRED data: {str(e)}")
        
        # Collect data from Alpha Vantage (limited by API rate limits)
        if 'alpha_vantage' in self.data_collectors:
            try:
                logger.info("Collecting Alpha Vantage data...")
                # Limit to first 5 symbols due to API rate limits
                limited_symbols = symbols[:5]
                av_data = self.data_collectors['alpha_vantage'].collect_batch_data(
                    limited_symbols,
                    delay=12.0  # 12 seconds between requests
                )
                
                if av_data and self.db_loader:
                    self.db_loader.load_stock_data(av_data)
                    logger.info(f"Loaded {len(av_data)} symbols from Alpha Vantage to database")
                
            except Exception as e:
                logger.error(f"Error collecting Alpha Vantage data: {str(e)}")
    
    def process_data(self, symbols: list = None):
        """
        Process and transform collected data.
        
        Args:
            symbols: List of symbols to process
        """
        if symbols is None:
            symbols = DATA_SOURCES['yahoo_finance']['symbols']
        
        logger.info("Starting data processing...")
        
        try:
            # Get data from database
            if not self.db_loader:
                logger.error("Database loader not initialized")
                return
            
            # Get stock data
            stock_data = {}
            for symbol in symbols:
                query = f"""
                    SELECT date, open, high, low, close, adjusted_close, volume
                    FROM stock_prices 
                    WHERE symbol = '{symbol}' 
                    ORDER BY date
                """
                data = self.db_loader.query_data(query)
                if not data.empty:
                    data['date'] = pd.to_datetime(data['date'])
                    data.set_index('date', inplace=True)
                    stock_data[symbol] = data
            
            if not stock_data:
                logger.warning("No stock data found for processing")
                return
            
            # Process each symbol
            processed_data = {}
            for symbol, data in stock_data.items():
                try:
                    # Calculate returns
                    data_with_returns = self.transformer.calculate_returns(data, 'adjusted_close')
                    
                    # Calculate technical indicators
                    data_with_indicators = self.transformer.calculate_technical_indicators(
                        data_with_returns, 'adjusted_close', 'volume'
                    )
                    
                    # Calculate volatility
                    data_with_vol = self.transformer.calculate_volatility(
                        data_with_indicators, 'returns'
                    )
                    
                    # Clean data
                    cleaned_data = self.transformer.cleaner.clean_missing_values(
                        data_with_vol, method="forward_fill"
                    )
                    
                    processed_data[symbol] = cleaned_data
                    logger.info(f"Processed data for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error processing data for {symbol}: {str(e)}")
                    continue
            
            # Calculate correlation matrix
            returns_data = pd.DataFrame({
                symbol: data['returns'] for symbol, data in processed_data.items()
                if 'returns' in data.columns
            })
            
            if not returns_data.empty:
                correlation_matrix = self.transformer.calculate_correlation_matrix(
                    {symbol: data for symbol, data in processed_data.items()}
                )
                logger.info("Calculated correlation matrix")
            
            logger.info(f"Data processing completed for {len(processed_data)} symbols")
            
        except Exception as e:
            logger.error(f"Error in data processing: {str(e)}")
    
    def optimize_portfolio(self, symbols: list = None, method: str = "markowitz"):
        """
        Optimize portfolio using specified method.
        
        Args:
            symbols: List of symbols to include in portfolio
            method: Optimization method
        """
        if symbols is None:
            symbols = DATA_SOURCES['yahoo_finance']['symbols']
        
        logger.info(f"Starting portfolio optimization using {method} method...")
        
        try:
            if not self.db_loader:
                logger.error("Database loader not initialized")
                return
            
            # Get returns data
            returns_data = {}
            for symbol in symbols:
                query = f"""
                    SELECT date, close
                    FROM stock_prices 
                    WHERE symbol = '{symbol}' 
                    ORDER BY date
                """
                data = self.db_loader.query_data(query)
                if not data.empty:
                    data['date'] = pd.to_datetime(data['date'])
                    data.set_index('date', inplace=True)
                    data['returns'] = data['close'].pct_change()
                    returns_data[symbol] = data['returns']
            
            if not returns_data:
                logger.warning("No returns data found for optimization")
                return
            
            # Create returns DataFrame
            returns_df = pd.DataFrame(returns_data).dropna()
            
            if returns_df.empty:
                logger.warning("No valid returns data for optimization")
                return
            
            # Optimize portfolio
            results = self.portfolio_optimizer.optimize_portfolio(returns_df, method=method)
            
            logger.info(f"Portfolio optimization completed:")
            logger.info(f"Expected Return: {results['expected_return']:.4f}")
            logger.info(f"Volatility: {results['volatility']:.4f}")
            logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.4f}")
            
            # Save results to database
            portfolio_data = []
            for symbol, weight in results['weights'].items():
                portfolio_data.append({
                    'portfolio_name': f'optimized_{method}',
                    'date': datetime.now().date(),
                    'symbol': symbol,
                    'weight': weight,
                    'returns': returns_df[symbol].iloc[-1] if symbol in returns_df.columns else 0,
                    'value': weight * 100000  # Assuming $100k portfolio
                })
            
            if portfolio_data and self.db_loader:
                portfolio_df = pd.DataFrame(portfolio_data)
                self.db_loader.load_portfolio_data('optimized_portfolio', portfolio_df)
                logger.info("Portfolio optimization results saved to database")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {str(e)}")
            return None
    
    def calculate_risk_metrics(self, symbols: list = None):
        """
        Calculate risk metrics for the portfolio.
        
        Args:
            symbols: List of symbols to analyze
        """
        if symbols is None:
            symbols = DATA_SOURCES['yahoo_finance']['symbols']
        
        logger.info("Calculating risk metrics...")
        
        try:
            if not self.db_loader:
                logger.error("Database loader not initialized")
                return
            
            # Get returns data
            returns_data = {}
            for symbol in symbols:
                query = f"""
                    SELECT date, close
                    FROM stock_prices 
                    WHERE symbol = '{symbol}' 
                    ORDER BY date
                """
                data = self.db_loader.query_data(query)
                if not data.empty:
                    data['date'] = pd.to_datetime(data['date'])
                    data.set_index('date', inplace=True)
                    data['returns'] = data['close'].pct_change()
                    returns_data[symbol] = data['returns']
            
            if not returns_data:
                logger.warning("No returns data found for risk calculation")
                return
            
            # Create returns DataFrame
            returns_df = pd.DataFrame(returns_data).dropna()
            
            if returns_df.empty:
                logger.warning("No valid returns data for risk calculation")
                return
            
            # Calculate portfolio returns (equal weight for now)
            portfolio_returns = returns_df.mean(axis=1)
            
            # Calculate risk metrics
            risk_metrics = self.risk_calculator.calculate_risk_metrics(portfolio_returns)
            
            logger.info("Risk metrics calculated:")
            for metric, value in risk_metrics.items():
                logger.info(f"{metric}: {value:.4f}")
            
            # Save risk metrics to database
            risk_data = [{
                'portfolio_name': 'main_portfolio',
                'date': datetime.now().date(),
                'sharpe_ratio': risk_metrics.get('sharpe_ratio', 0),
                'var_95': risk_metrics.get('var_95', 0),
                'var_99': risk_metrics.get('var_99', 0),
                'max_drawdown': risk_metrics.get('max_drawdown', 0),
                'volatility': risk_metrics.get('volatility', 0),
                'beta': risk_metrics.get('beta', 0)
            }]
            
            if risk_data and self.db_loader:
                risk_df = pd.DataFrame(risk_data)
                self.db_loader.load_risk_metrics('main_portfolio', risk_df)
                logger.info("Risk metrics saved to database")
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {str(e)}")
            return None
    
    def run_full_pipeline(self):
        """Run the complete pipeline."""
        logger.info("Starting full quantitative finance pipeline...")
        
        try:
            # Step 1: Collect data
            self.collect_data()
            
            # Step 2: Process data
            self.process_data()
            
            # Step 3: Optimize portfolio
            self.optimize_portfolio()
            
            # Step 4: Calculate risk metrics
            self.calculate_risk_metrics()
            
            logger.info("Full pipeline completed successfully!")
            
        except Exception as e:
            logger.error(f"Error in full pipeline: {str(e)}")
            raise


def main():
    """Main function to run the pipeline."""
    try:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Initialize and run pipeline
        pipeline = QuantitativeFinancePipeline()
        pipeline.run_full_pipeline()
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
