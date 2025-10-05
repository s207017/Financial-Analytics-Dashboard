# Monitoring Stack for Quantitative Finance Pipeline

This directory contains the complete monitoring infrastructure for the Quantitative Finance Pipeline, including Prometheus, Grafana, and various exporters.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │   Prometheus    │    │     Grafana     │
│   (Port 8000)   │───▶│   (Port 9090)   │───▶│   (Port 3000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Redis Exporter │    │  Node Exporter  │    │  Alertmanager   │
│   (Port 9121)   │    │   (Port 9100)   │    │   (Port 9093)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Redis      │    │     System      │    │     Alerts      │
│   (Port 6379)   │    │    Metrics      │    │   & Notifications│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the Monitoring Stack

```bash
# Navigate to monitoring directory
cd monitoring

# Start all monitoring services
./start-monitoring.sh
```

### 2. Access the Dashboards

- **Grafana Dashboard**: http://localhost:3000
  - Username: `admin`
  - Password: `admin123`

- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

## 📊 Available Dashboards

### 1. Quantitative Finance Pipeline - Comprehensive Monitoring
- **Purpose**: Overall system health and performance
- **Metrics**: CPU, Memory, Database connections, Application metrics
- **Location**: `grafana/dashboards/financial-pipeline-comprehensive.json`

### 2. Redis Monitoring Dashboard
- **Purpose**: Redis cache performance and health
- **Metrics**: Cache hit/miss ratio, memory usage, connections
- **Location**: `grafana/dashboards/redis-monitoring.json`

### 3. Simple Dashboard
- **Purpose**: Basic system overview
- **Metrics**: Basic system metrics
- **Location**: `grafana/dashboards/simple-dashboard.json`

## 🔧 Services and Ports

| Service | Port | Purpose |
|---------|------|---------|
| Grafana | 3000 | Dashboard visualization |
| Prometheus | 9090 | Metrics collection and storage |
| Alertmanager | 9093 | Alert handling and notifications |
| Node Exporter | 9100 | System metrics |
| Redis Exporter | 9121 | Redis metrics |
| PostgreSQL Exporter | 9187 | Database metrics |
| cAdvisor | 8080 | Container metrics |

## 📈 Custom Metrics

The application exposes custom metrics on port 8000:

### Portfolio Metrics
- `quant_finance_portfolios_total` - Total number of portfolios
- `quant_finance_portfolio_analytics_calculations_total` - Portfolio calculations
- `quant_finance_portfolio_analytics_duration_seconds` - Calculation duration

### Stock Data Metrics
- `quant_finance_stock_data_fetches_total` - Stock data fetches
- `quant_finance_stock_data_fetch_duration_seconds` - Fetch duration
- `quant_finance_stock_symbols_total` - Total stock symbols

### Cache Metrics
- `quant_finance_cache_hits_total` - Cache hits
- `quant_finance_cache_misses_total` - Cache misses
- `quant_finance_cache_size_bytes` - Cache size

### Database Metrics
- `quant_finance_db_connections_active` - Active connections
- `quant_finance_db_query_duration_seconds` - Query duration

### System Metrics
- `quant_finance_system_cpu_usage_percent` - CPU usage
- `quant_finance_system_memory_usage_bytes` - Memory usage
- `quant_finance_system_disk_usage_bytes` - Disk usage

### Error Metrics
- `quant_finance_errors_total` - Total errors by type and component

## 🚨 Alerting Rules

The monitoring stack includes comprehensive alerting rules:

### Critical Alerts
- **Service Down**: Service unavailable for > 1 minute
- **High Error Rate**: Error rate > 0.1 errors/second
- **Portfolio Calculation Failures**: Failure rate > 0.05 failures/second
- **Low Disk Space**: Disk space < 10%

### Warning Alerts
- **High CPU Usage**: CPU usage > 80% for 5 minutes
- **High Memory Usage**: Memory usage > 85% for 5 minutes
- **High Database Connections**: > 20 active connections
- **High Redis Connections**: > 50 connected clients
- **Low Cache Hit Rate**: < 70% for 10 minutes
- **Slow Database Queries**: 95th percentile > 2 seconds
- **Slow Portfolio Calculations**: 95th percentile > 10 seconds

## 🔄 Integration with Application

### 1. Enable Metrics in Application

Add to your application startup:

```python
from src.monitoring.metrics_exporter import start_metrics_exporter

# Start metrics exporter
start_metrics_exporter(port=8000, collection_interval=30)
```

### 2. Record Custom Metrics

```python
from src.monitoring.metrics_exporter import get_metrics_exporter

# Get metrics exporter
metrics = get_metrics_exporter()

# Record portfolio calculation
metrics.record_portfolio_calculation(
    portfolio_name="Tech Growth",
    calculation_type="analytics",
    duration=2.5
)

# Record stock data fetch
metrics.record_stock_data_fetch(
    symbol="AAPL",
    source="yahoo_finance",
    status="success",
    duration=1.2
)

# Record cache operation
metrics.record_cache_operation(
    cache_type="redis",
    key_pattern="portfolio_analytics",
    hit=True
)
```

## 🛠️ Configuration

### Prometheus Configuration
- **File**: `prometheus.yml`
- **Scrape Interval**: 15 seconds
- **Retention**: 200 hours
- **Targets**: Application, Redis, PostgreSQL, System metrics

### Grafana Configuration
- **Admin User**: admin
- **Admin Password**: admin123
- **Auto-provisioning**: Enabled for dashboards and datasources
- **Theme**: Dark

### Alertmanager Configuration
- **File**: `alertmanager.yml`
- **Notification Channels**: Email, Slack (configurable)

## 📝 Maintenance

### View Logs
```bash
# All services
docker compose -f docker-compose.monitoring.yml logs -f

# Specific service
docker compose -f docker-compose.monitoring.yml logs -f grafana
```

### Restart Services
```bash
# Restart all
docker compose -f docker-compose.monitoring.yml restart

# Restart specific service
docker compose -f docker-compose.monitoring.yml restart grafana
```

### Stop Services
```bash
docker compose -f docker-compose.monitoring.yml down
```

### Update Dashboards
1. Edit JSON files in `grafana/dashboards/`
2. Restart Grafana: `docker compose -f docker-compose.monitoring.yml restart grafana`

## 🔍 Troubleshooting

### Common Issues

1. **Services not starting**
   - Check Docker is running
   - Check port conflicts
   - View logs: `docker compose -f docker-compose.monitoring.yml logs`

2. **Metrics not appearing**
   - Verify application is exposing metrics on port 8000
   - Check Prometheus targets: http://localhost:9090/targets
   - Verify network connectivity

3. **Grafana not loading dashboards**
   - Check Grafana logs
   - Verify dashboard JSON syntax
   - Check datasource configuration

4. **Alerts not firing**
   - Check Prometheus rules: http://localhost:9090/rules
   - Verify Alertmanager configuration
   - Check alert thresholds

### Health Checks

```bash
# Check Prometheus health
curl http://localhost:9090/-/healthy

# Check Grafana health
curl http://localhost:3000/api/health

# Check metrics endpoint
curl http://localhost:8000/metrics
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Redis Exporter](https://github.com/oliver006/redis_exporter)
- [PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter)

## 🤝 Contributing

To add new metrics or dashboards:

1. **Add Custom Metrics**: Update `src/monitoring/metrics_exporter.py`
2. **Create Dashboard**: Add JSON file to `grafana/dashboards/`
3. **Add Alerting Rules**: Update `alerting-rules.yml`
4. **Update Documentation**: Update this README

## 📄 License

This monitoring stack is part of the Quantitative Finance Pipeline project.
