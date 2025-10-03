"""
Scheduler for automated data collection and analysis.
"""
import schedule
import time
import logging
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from main import QuantitativeFinancePipeline
from config.config import DATA_SOURCES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PipelineScheduler:
    """Scheduler for automated pipeline execution."""
    
    def __init__(self):
        """Initialize scheduler."""
        self.pipeline = QuantitativeFinancePipeline()
        self.symbols = DATA_SOURCES['yahoo_finance']['symbols']
    
    def daily_data_collection(self):
        """Run daily data collection."""
        try:
            logger.info("Starting daily data collection...")
            self.pipeline.collect_data(symbols=self.symbols, days_back=1)
            logger.info("Daily data collection completed")
        except Exception as e:
            logger.error(f"Error in daily data collection: {str(e)}")
    
    def weekly_portfolio_optimization(self):
        """Run weekly portfolio optimization."""
        try:
            logger.info("Starting weekly portfolio optimization...")
            self.pipeline.optimize_portfolio(symbols=self.symbols, method="markowitz")
            logger.info("Weekly portfolio optimization completed")
        except Exception as e:
            logger.error(f"Error in weekly portfolio optimization: {str(e)}")
    
    def daily_risk_calculation(self):
        """Run daily risk metrics calculation."""
        try:
            logger.info("Starting daily risk calculation...")
            self.pipeline.calculate_risk_metrics(symbols=self.symbols)
            logger.info("Daily risk calculation completed")
        except Exception as e:
            logger.error(f"Error in daily risk calculation: {str(e)}")
    
    def monthly_full_analysis(self):
        """Run monthly full analysis."""
        try:
            logger.info("Starting monthly full analysis...")
            self.pipeline.run_full_pipeline()
            logger.info("Monthly full analysis completed")
        except Exception as e:
            logger.error(f"Error in monthly full analysis: {str(e)}")
    
    def setup_schedule(self):
        """Set up the scheduling."""
        # Daily data collection at 6 PM (after market close)
        schedule.every().day.at("18:00").do(self.daily_data_collection)
        
        # Daily risk calculation at 6:30 PM
        schedule.every().day.at("18:30").do(self.daily_risk_calculation)
        
        # Weekly portfolio optimization on Sundays at 7 PM
        schedule.every().sunday.at("19:00").do(self.weekly_portfolio_optimization)
        
        # Monthly full analysis on the first day of each month at 8 PM
        schedule.every().month.do(self.monthly_full_analysis)
        
        logger.info("Schedule setup completed")
        logger.info("Daily data collection: 18:00")
        logger.info("Daily risk calculation: 18:30")
        logger.info("Weekly portfolio optimization: Sunday 19:00")
        logger.info("Monthly full analysis: 1st of month 20:00")
    
    def run(self):
        """Run the scheduler."""
        logger.info("Starting pipeline scheduler...")
        self.setup_schedule()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduler: {str(e)}")
                time.sleep(60)


if __name__ == "__main__":
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    scheduler = PipelineScheduler()
    scheduler.run()
