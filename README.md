# Quantitative Finance Pipeline

A comprehensive data pipeline for quantitative finance analysis, featuring ETL processes, portfolio optimization, risk metrics, and machine learning components.

## Features

- **Data Ingestion**: APIs for Alpha Vantage, Yahoo Finance, Quandl, and FRED
- **ETL Pipeline**: Data transformation and loading into PostgreSQL
- **Portfolio Optimization**: Modern Portfolio Theory implementation
- **Risk Metrics**: Sharpe ratio, VaR, beta calculations
- **Machine Learning**: Regression and clustering analysis
- **Visualization**: Interactive Dash dashboard
- **Cloud Deployment**: AWS integration with Docker and Kubernetes
- **CI/CD**: GitHub Actions for automated testing and deployment

## Project Structure

```
quant-finance-pipeline/
├── config/                 # Configuration files
├── data/                   # Data storage
│   ├── raw/               # Raw data from APIs
│   ├── processed/         # Cleaned and transformed data
│   └── external/          # External data sources
├── src/                   # Source code
│   ├── data_ingestion/    # API data collectors
│   ├── etl/              # ETL pipeline components
│   ├── analytics/        # Portfolio optimization and risk metrics
│   ├── ml/               # Machine learning models
│   └── visualization/    # Dash app and reports
├── deployment/           # Docker and Kubernetes configs
├── tests/               # Unit and integration tests
└── notebooks/           # Jupyter notebooks for analysis
```

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd quant-finance-pipeline
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database credentials
   ```

4. **Set up PostgreSQL database**:
   ```bash
   # Create database
   createdb quant_finance
   ```

5. **Run the pipeline**:
   ```bash
   python -m src.main
   ```

## API Keys Required

- Alpha Vantage API key (free tier available)
- Quandl API key (free tier available)
- FRED API key (free registration required)

## Usage

### Data Ingestion
```python
from src.data_ingestion.yahoo_finance import YahooFinanceCollector

collector = YahooFinanceCollector()
data = collector.collect_data(["AAPL", "GOOGL"])
```

### Portfolio Optimization
```python
from src.analytics.portfolio_optimization import PortfolioOptimizer

optimizer = PortfolioOptimizer()
weights = optimizer.optimize_portfolio(returns_data)
```

### Risk Metrics
```python
from src.analytics.risk_metrics import RiskCalculator

calculator = RiskCalculator()
sharpe_ratio = calculator.calculate_sharpe_ratio(returns, risk_free_rate)
```

## Deployment

### Docker
```bash
docker build -t quant-finance-pipeline .
docker run -p 5000:5000 quant-finance-pipeline
```

### Kubernetes
```bash
kubectl apply -f deployment/kubernetes/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
