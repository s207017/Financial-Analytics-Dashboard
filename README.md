# Quantitative Finance Pipeline

A comprehensive data pipeline for quantitative finance analysis, featuring ETL processes, portfolio optimization, risk metrics, and machine learning components with a **complete Portfolio Management Dashboard**.

## 🚀 Quick Start with Docker (Recommended)

The easiest way to run this application is using Docker, which ensures consistent deployment across any environment.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### 1. Clone and Setup
```bash
git clone https://github.com/s207017/Financial-Analytics-Dashboard.git
cd Financial-Analytics-Dashboard
```

### 2. Environment Configuration
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your API keys (optional for basic functionality)
nano .env
```

**Required API Keys** (optional for basic portfolio management):
- `ALPHA_VANTAGE_API_KEY` - Get free key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
- `QUANDL_API_KEY` - Get free key at [Quandl](https://www.quandl.com/account/api)
- `FRED_API_KEY` - Get free key at [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)

### 3. Start the Application
```bash
# Start all services (PostgreSQL, Redis, Dashboard, Scheduler)
docker-compose up -d

# View logs
docker-compose logs -f dashboard
```

### 4. Access the Dashboard
- **Portfolio Management Dashboard**: http://localhost:8051
- **Database**: localhost:5432 (postgres/quant_finance)
- **Redis**: localhost:6379

### 5. Initialize Sample Data (Optional)
```bash
# Create sample portfolios in the database
docker-compose exec app python scripts/create_sample_portfolios.py

# Setup database tables
docker-compose exec app python scripts/setup_portfolio_tables.py
```

## 🎯 Features

### Portfolio Management Dashboard
- **Create & Edit Portfolios**: Build custom investment portfolios with multiple strategies
- **Real-time Calculations**: Live portfolio value updates for custom stock allocations
- **Multiple Strategies**: Equal Weight, Market Cap, Risk Parity, and Custom strategies
- **Historical Analysis**: Actual return calculations based on real stock data
- **Database Persistence**: All portfolios saved permanently in PostgreSQL

### Core Pipeline Features
- **Data Ingestion**: APIs for Alpha Vantage, Yahoo Finance, Quandl, and FRED
- **ETL Pipeline**: Data transformation and loading into PostgreSQL
- **Portfolio Optimization**: Modern Portfolio Theory implementation
- **Risk Metrics**: Sharpe ratio, VaR, beta calculations
- **Machine Learning**: Regression and clustering analysis
- **Cloud Deployment**: AWS integration with Docker and Kubernetes
- **CI/CD**: GitHub Actions for automated testing and deployment

## 🏗️ Project Structure

```
Financial-Analytics-Dashboard/
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
│   ├── data_access/      # Database services (PortfolioManagementService)
│   └── visualization/    # Dash app and reports
├── deployment/           # Docker and Kubernetes configs
├── scripts/              # Setup and utility scripts
├── tests/               # Unit and integration tests
└── notebooks/           # Jupyter notebooks for analysis
```

## 🐳 Docker Services

The application runs as a multi-service Docker Compose setup:

| Service | Port | Description |
|---------|------|-------------|
| `postgres` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis cache |
| `dashboard` | 8050 | Portfolio Management Dashboard |
| `app` | 5000 | Main application API |
| `scheduler` | - | Background data collection |

## 📊 Portfolio Management Usage

### Creating Portfolios
1. Navigate to **Portfolio Management** tab
2. Enter portfolio name and description
3. Select investment strategy:
   - **Equal Weight**: Equal allocation across all assets
   - **Market Cap**: Weighted by market capitalization
   - **Risk Parity**: Risk-adjusted allocation
   - **Custom**: Manual allocation with real-time value calculation
4. Choose assets from the dropdown
5. Click **Create Portfolio**

### Editing Portfolios
1. Select portfolio from dropdown
2. Click **Edit Portfolio**
3. Modify name, description, or allocations
4. Click **Update Portfolio**

### Custom Strategy
- Enter individual stock amounts
- Portfolio value updates automatically
- Total value becomes read-only
- Real-time validation and calculation

## 🔧 Development Setup (Alternative)

If you prefer to run without Docker:

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
createdb quant_finance
python scripts/setup_portfolio_tables.py

# Run the dashboard
python -m src.visualization.dash_app.simple_app
```

## 🚀 Deployment Options

### Docker Compose (Recommended)
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# With monitoring stack
docker-compose -f docker-compose.yml -f monitoring/docker-compose.monitoring.yml up -d
```

### Kubernetes
```bash
# Setup local Kubernetes cluster
cd deployment/kubernetes
./setup-local-k8s.sh

# Test Kubernetes functionality
./test-k8s-functionality.sh

# Deploy application
./deploy.sh

# Access services
# Dashboard: http://quant-finance.local:8051
# Prometheus: http://prometheus.quant-finance.local:9090
# Grafana: http://grafana.quant-finance.local:3000
```

**Kubernetes Testing:**
- **Comprehensive Test Suite**: 25+ automated tests validating all Kubernetes features
- **Test Coverage**: Pod management, service discovery, load balancing, self-healing, rolling updates, storage, monitoring
- **Validation Results**: 23/25 tests passing, proving Kubernetes is actively managing containers
- **Real-world Scenarios**: Tests simulate production conditions and failure scenarios

**Kubernetes Features:**
- **High Availability**: Multi-replica deployments with auto-scaling
- **Persistent Storage**: PostgreSQL and Redis data persistence
- **Service Discovery**: Automatic service-to-service communication
- **Load Balancing**: Traffic distribution across multiple instances
- **Monitoring**: Integrated Prometheus and Grafana stack
- **Ingress**: External access with SSL termination
- **Health Checks**: Automatic container restart and traffic routing
- **Self-Healing**: Automatic pod recreation on failure
- **Rolling Updates**: Zero-downtime deployments
- **Comprehensive Testing**: 25+ automated tests validating Kubernetes functionality

### AWS Lambda
```bash
# Deploy serverless functions
python scripts/deploy_lambda.py
```

## 📈 API Usage Examples

### Portfolio Management
```python
from src.data_access.portfolio_management_service import PortfolioManagementService

service = PortfolioManagementService()

# Create portfolio
portfolio = service.create_portfolio(
    name="Tech Growth",
    symbols=["AAPL", "GOOGL", "MSFT"],
    weights=[0.4, 0.3, 0.3],
    strategy="Custom"
)

# Calculate analytics
analytics = service.calculate_portfolio_analytics(
    symbols=["AAPL", "GOOGL", "MSFT"],
    weights=[0.4, 0.3, 0.3]
)
```

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

## 🔍 Monitoring

Access monitoring dashboards:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 🧪 Testing

```bash
# Run tests
docker-compose exec app python -m pytest tests/

# Run specific test
docker-compose exec app python -m pytest tests/unit/test_portfolio_service.py
```

## 🛠️ Troubleshooting

### Common Issues

**Port 8050 already in use:**
```bash
# Find and kill process
lsof -ti:8050 | xargs kill -9
```

**Database connection issues:**
```bash
# Check PostgreSQL status
docker-compose ps postgres
docker-compose logs postgres
```

**Missing dependencies:**
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Reset Everything
```bash
# Complete reset
docker-compose down -v
docker system prune -f
docker-compose up -d
```

## 📝 Environment Variables

Key environment variables in `.env`:

```bash
# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=quant_finance
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# API Keys
ALPHA_VANTAGE_API_KEY=your_key
QUANDL_API_KEY=your_key
FRED_API_KEY=your_key

# Application
FLASK_ENV=development
DEBUG=True
```


## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.


---

**Ready to start?** Run `docker-compose up -d` and visit http://localhost:8050! 🚀