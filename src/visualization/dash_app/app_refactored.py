"""
Refactored Dash application with improved design principles.
"""
import dash
import logging
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import our new modules
from .config import DASHBOARD_TITLE, DASHBOARD_THEME
from .utils import DatabaseManager
from .layouts import create_main_layout
from .callbacks import CallbackManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection
try:
    from src.data_access.portfolio_management_service import PortfolioManagementService
    portfolio_service = PortfolioManagementService()
    database_available = True
    logger.info("Database connection established successfully")
except Exception as e:
    logger.warning(f"Database not available: {e}")
    portfolio_service = None
    database_available = False

# Initialize database manager
db_manager = DatabaseManager(portfolio_service, database_available)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[DASHBOARD_THEME])
app.title = DASHBOARD_TITLE

# Set app layout
app.layout = create_main_layout()

# Initialize callback manager
callback_manager = CallbackManager(app, db_manager)

# Global variables for backward compatibility (if needed)
DATABASE_AVAILABLE = database_available
PORTFOLIO_SERVICE = portfolio_service

if __name__ == "__main__":
    print("Starting Quantitative Finance Pipeline Dashboard...")
    print("Dashboard will be available at: http://localhost:8050")
    print("Press Ctrl+C to stop the server")
    app.run_server(debug=True, host="0.0.0.0", port=8050)
