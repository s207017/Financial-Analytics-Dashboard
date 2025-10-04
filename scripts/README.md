# Scripts Directory

This directory contains utility scripts organized by functionality.

## 📁 Directory Structure

### `/setup/` - Database and System Setup
Scripts for initial setup and configuration:
- `setup_database.py` - Initialize PostgreSQL database schema
- `setup_portfolio_tables.py` - Create portfolio-related tables
- `setup_stock_filtering_tables.py` - Create stock filtering tables
- `setup_monitoring.sh` - Setup monitoring infrastructure

### `/data/` - Data Collection and Management
Scripts for data ingestion and portfolio management:
- `create_sample_portfolios.py` - Create sample portfolios with fresh stock data
- `collect_market_data.py` - Collect market data from various sources
- `collect_market_data_robust.py` - Robust market data collection with error handling
- `collect_stock_data.py` - Collect individual stock data
- `process_market_data.py` - Process and transform market data
- `generate_sample_stock_data.py` - Generate sample stock data for testing
- `update_custom_portfolio_weights.py` - Update portfolio weight allocations

### `/testing/` - Testing and Validation
Scripts for testing system components:
- `test_data_service.py` - Test data service functionality
- `test_db_connection.py` - Test database connectivity
- `test_dynamic_date_range.py` - Test dynamic date range functionality
- `test_stock_data_service.py` - Test stock data service

### `/deployment/` - Deployment and AWS Integration
Scripts for deployment and cloud integration:
- `aws_eventbridge_setup.py` - Setup AWS EventBridge for scheduling
- `deploy_lambda.py` - Deploy AWS Lambda functions
- `lambda_function.py` - AWS Lambda function code

## 🚀 Quick Start

### Initial Setup
```bash
# Setup database
python scripts/setup/setup_database.py

# Create sample portfolios with fresh data
python scripts/data/create_sample_portfolios.py
```

### Testing
```bash
# Test database connection
python scripts/testing/test_db_connection.py

# Test data services
python scripts/testing/test_data_service.py
```

### Deployment
```bash
# Deploy to AWS
python scripts/deployment/deploy_lambda.py
```

## 📝 Usage Notes

- All scripts should be run from the project root directory
- Ensure Docker containers are running for database-dependent scripts
- Check individual script documentation for specific requirements
