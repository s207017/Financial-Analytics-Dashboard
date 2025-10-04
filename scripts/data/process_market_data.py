"""
ETL pipeline to process raw market data and calculate derived metrics.
"""
import sys
from pathlib import Path
import logging
from datetime import datetime
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from etl.loaders.database_loader import DatabaseLoader
from etl.transformers.data_cleaner import FinancialDataTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_stock_data():
    """Process raw stock data and calculate derived metrics."""
    logger.info("Starting ETL pipeline for stock data processing...")
    
    try:
        db_loader = DatabaseLoader("postgresql://postgres:password@localhost:5432/quant_finance")
        transformer = FinancialDataTransformer()
        
        # Get all symbols from database
        symbols_query = "SELECT DISTINCT symbol FROM stock_prices ORDER BY symbol"
        symbols_df = db_loader.query_data(symbols_query)
        symbols = symbols_df['symbol'].tolist()
        
        logger.info(f"Processing data for {len(symbols)} symbols: {symbols}")
        
        processed_data = {}
        
        for symbol in symbols:
            logger.info(f"Processing {symbol}...")
            
            # Get raw data for symbol
            query = f"""
                SELECT date, open, high, low, close, adjusted_close, volume
                FROM stock_prices 
                WHERE symbol = '{symbol}' 
                ORDER BY date
            """
            raw_data = db_loader.query_data(query)
            
            if raw_data.empty:
                logger.warning(f"No data found for {symbol}")
                continue
            
            # Set date as index
            raw_data['date'] = pd.to_datetime(raw_data['date'])
            raw_data.set_index('date', inplace=True)
            
            # Calculate returns
            data_with_returns = transformer.calculate_returns(raw_data, 'adjusted_close', 'simple')
            
            # Calculate technical indicators
            data_with_indicators = transformer.calculate_technical_indicators(
                data_with_returns, 'adjusted_close', 'volume'
            )
            
            # Calculate volatility
            data_with_vol = transformer.calculate_volatility(
                data_with_indicators, 'returns', window=30
            )
            
            # Clean data
            cleaned_data = transformer.cleaner.clean_missing_values(
                data_with_vol, method="forward_fill"
            )
            
            # Reset index to make date a column for database storage
            cleaned_data = cleaned_data.reset_index()
            
            # Add metadata
            cleaned_data['symbol'] = symbol
            cleaned_data['processed_at'] = datetime.now()
            
            processed_data[symbol] = cleaned_data
            
            logger.info(f"Processed {symbol}: {len(cleaned_data)} records")
        
        # Store technical indicators in database
        store_technical_indicators(processed_data, db_loader)
        
        # Calculate and store portfolio metrics
        calculate_portfolio_metrics(processed_data, db_loader)
        
        logger.info("ETL pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in ETL pipeline: {str(e)}")
        raise


def store_technical_indicators(processed_data, db_loader):
    """Store technical indicators in database."""
    logger.info("Storing technical indicators...")
    
    try:
        for symbol, data in processed_data.items():
            # Select technical indicator columns
            tech_columns = [
                'date', 'symbol', 'sma_20', 'sma_50', 'ema_12', 'ema_26',
                'macd', 'macd_signal', 'macd_histogram', 'rsi',
                'bb_upper', 'bb_middle', 'bb_lower', 'bb_width'
            ]
            
            # Filter to available columns
            available_columns = [col for col in tech_columns if col in data.columns]
            tech_data = data[available_columns].copy()
            
            if not tech_data.empty:
                # Store in technical_indicators table
                tech_data.to_sql(
                    'technical_indicators',
                    db_loader.engine,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                logger.info(f"Stored technical indicators for {symbol}")
        
    except Exception as e:
        logger.error(f"Error storing technical indicators: {str(e)}")


def calculate_portfolio_metrics(processed_data, db_loader):
    """Calculate portfolio-level metrics."""
    logger.info("Calculating portfolio metrics...")
    
    try:
        # Create returns DataFrame
        returns_data = {}
        for symbol, data in processed_data.items():
            if 'returns' in data.columns:
                returns_data[symbol] = data.set_index('date')['returns']
        
        if not returns_data:
            logger.warning("No returns data available for portfolio metrics")
            return
        
        returns_df = pd.DataFrame(returns_data).dropna()
        
        if returns_df.empty:
            logger.warning("No valid returns data after cleaning")
            return
        
        # Calculate portfolio returns (equal weight)
        portfolio_returns = returns_df.mean(axis=1)
        
        # Calculate risk metrics
        from analytics.risk_metrics.calculator import RiskCalculator
        risk_calc = RiskCalculator()
        
        risk_metrics = risk_calc.calculate_risk_metrics(portfolio_returns)
        
        # Store risk metrics
        risk_data = [{
            'portfolio_name': 'equal_weight_portfolio',
            'date': datetime.now().date(),
            'sharpe_ratio': risk_metrics.get('sharpe_ratio', 0),
            'var_95': risk_metrics.get('var_95', 0),
            'var_99': risk_metrics.get('var_99', 0),
            'max_drawdown': risk_metrics.get('max_drawdown', 0),
            'volatility': risk_metrics.get('volatility', 0),
            'beta': risk_metrics.get('beta', 0)
        }]
        
        risk_df = pd.DataFrame(risk_data)
        db_loader.load_risk_metrics('equal_weight_portfolio', risk_df)
        
        logger.info("Portfolio risk metrics calculated and stored")
        
        # Store portfolio data
        portfolio_data = []
        for date, row in returns_df.iterrows():
            for symbol in returns_df.columns:
                portfolio_data.append({
                    'portfolio_name': 'equal_weight_portfolio',
                    'date': date.date(),
                    'symbol': symbol,
                    'weight': 1.0 / len(returns_df.columns),  # Equal weight
                    'returns': row[symbol],
                    'value': 100000 * (1.0 / len(returns_df.columns))  # $100k portfolio
                })
        
        if portfolio_data:
            portfolio_df = pd.DataFrame(portfolio_data)
            db_loader.load_portfolio_data('equal_weight_portfolio', portfolio_df)
            logger.info("Portfolio data stored")
        
    except Exception as e:
        logger.error(f"Error calculating portfolio metrics: {str(e)}")


def verify_processed_data():
    """Verify that processed data was stored correctly."""
    try:
        db_loader = DatabaseLoader("postgresql://postgres:password@localhost:5432/quant_finance")
        
        # Check technical indicators
        query = """
            SELECT symbol, COUNT(*) as record_count,
                   MIN(date) as earliest_date,
                   MAX(date) as latest_date
            FROM technical_indicators 
            GROUP BY symbol 
            ORDER BY symbol
        """
        
        result = db_loader.query_data(query)
        
        if not result.empty:
            logger.info("Technical indicators verification:")
            for _, row in result.iterrows():
                logger.info(f"  {row['symbol']}: {row['record_count']} records "
                          f"({row['earliest_date']} to {row['latest_date']})")
        
        # Check risk metrics
        risk_query = "SELECT * FROM risk_metrics ORDER BY date DESC LIMIT 5"
        risk_result = db_loader.query_data(risk_query)
        
        if not risk_result.empty:
            logger.info("Risk metrics verification:")
            for _, row in risk_result.iterrows():
                logger.info(f"  {row['portfolio_name']}: Sharpe={row['sharpe_ratio']:.3f}, "
                          f"Vol={row['volatility']:.3f}, VaR95={row['var_95']:.3f}")
        
        # Check portfolio data
        portfolio_query = """
            SELECT portfolio_name, COUNT(*) as record_count,
                   MIN(date) as earliest_date,
                   MAX(date) as latest_date
            FROM portfolio_data 
            GROUP BY portfolio_name 
            ORDER BY portfolio_name
        """
        
        portfolio_result = db_loader.query_data(portfolio_query)
        
        if not portfolio_result.empty:
            logger.info("Portfolio data verification:")
            for _, row in portfolio_result.iterrows():
                logger.info(f"  {row['portfolio_name']}: {row['record_count']} records "
                          f"({row['earliest_date']} to {row['latest_date']})")
        
    except Exception as e:
        logger.error(f"Error verifying processed data: {str(e)}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process market data')
    parser.add_argument('--verify', action='store_true',
                       help='Verify processed data')
    
    args = parser.parse_args()
    
    try:
        # Process the data
        process_stock_data()
        
        if args.verify:
            verify_processed_data()
            
        logger.info("Data processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Data processing failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
