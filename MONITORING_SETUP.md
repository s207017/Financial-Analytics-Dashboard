# 🔍 Prometheus + Grafana Monitoring Setup

This guide will help you set up industry-standard monitoring for the Quantitative Finance Pipeline using **Prometheus** and **Grafana**.

## 📋 Prerequisites

### External Software Required:

1. **Docker** (Latest version)
   - Download: https://docs.docker.com/get-docker/
   - Required for running Prometheus, Grafana, and exporters

2. **Docker Compose** (Latest version)
   - Download: https://docs.docker.com/compose/install/
   - Required for orchestrating the monitoring stack

3. **Python 3.8+** (Already installed)
   - Required for the metrics exporter

## 🚀 Quick Setup

### Step 1: Run the Setup Script
```bash
cd /Users/seunghwanchoi/Documents/quant-finance-pipeline
./scripts/setup_monitoring.sh
```

### Step 2: Start the Metrics Exporter
```bash
# In a new terminal
cd /Users/seunghwanchoi/Documents/quant-finance-pipeline
PYTHONPATH=/Users/seunghwanchoi/Documents/quant-finance-pipeline python3 -m src.monitoring.metrics_exporter
```

### Step 3: Access the Dashboards
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your Pipeline │    │   Prometheus    │    │     Grafana     │
│                 │    │                 │    │                 │
│  Metrics        │───▶│  Collects &     │───▶│  Visualizes &   │
│  Exporter       │    │  Stores Metrics │    │  Alerts         │
│  (Port 8000)    │    │  (Port 9090)    │    │  (Port 3000)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │  Node Exporter  │    │   Alertmanager  │
│   Exporter      │    │  (System Metrics│    │   (Alerting)    │
│   (Port 9187)   │    │   Port 9100)    │    │   (Port 9093)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 What Gets Monitored

### System Metrics
- **CPU Usage**: Real-time CPU utilization
- **Memory Usage**: RAM consumption
- **Disk Usage**: Storage utilization
- **Network I/O**: Network traffic

### Database Metrics
- **Connection Time**: Database response latency
- **Active Connections**: Number of concurrent connections
- **Query Performance**: Database operation metrics

### Pipeline Metrics
- **Data Volume**: Records per table (stock_prices, portfolio_data, etc.)
- **Data Freshness**: How old the data is
- **Request Metrics**: API call counts and durations
- **Error Rates**: Failed operations

### Container Metrics (if using Docker)
- **Container CPU/Memory**: Per-container resource usage
- **Container Health**: Container status and restarts

## 🎯 Key Features

### 1. Real-time Dashboards
- **System Overview**: CPU, Memory, Disk usage
- **Database Health**: Connection times, active connections
- **Data Volume**: Records per table over time
- **Performance Trends**: Historical performance data

### 2. Alerting
- **High CPU Usage**: >80% for 5 minutes
- **High Memory Usage**: >85% for 5 minutes
- **Database Down**: No response for 1 minute
- **Pipeline Down**: Service unavailable
- **Stale Data**: Data older than 24 hours

### 3. Custom Metrics
- **Pipeline-specific metrics**: Data volume, freshness
- **Business metrics**: Portfolio performance, risk metrics
- **Custom alerts**: Configurable thresholds

## 🔧 Configuration Files

### Prometheus Configuration (`monitoring/prometheus.yml`)
- Defines what to monitor and how often
- Scrape intervals and targets
- Alert rules and thresholds

### Grafana Configuration (`monitoring/grafana/`)
- Dashboard definitions
- Data source configurations
- User management

### Alertmanager Configuration (`monitoring/alertmanager.yml`)
- Alert routing and grouping
- Notification channels (email, webhook, etc.)
- Alert suppression rules

## 🚨 Alerting Setup

### Default Alerts
1. **High CPU Usage**: Warns when CPU >80% for 5+ minutes
2. **High Memory Usage**: Warns when Memory >85% for 5+ minutes
3. **Database Down**: Critical alert when DB is unreachable
4. **Pipeline Down**: Critical alert when pipeline is down
5. **Stale Data**: Warns when data is >24 hours old

### Customizing Alerts
Edit `monitoring/alertmanager.yml` to:
- Add new alert rules
- Change thresholds
- Configure notification channels
- Set up alert routing

## 📈 Dashboard Customization

### Adding New Panels
1. Access Grafana at http://localhost:3000
2. Navigate to the Quantitative Finance Pipeline dashboard
3. Click "Add Panel" to create new visualizations
4. Use Prometheus queries to fetch data

### Example Queries
```promql
# CPU Usage
pipeline_system_cpu_percent

# Memory Usage
pipeline_system_memory_percent

# Database Connection Time
pipeline_db_connection_seconds

# Data Volume by Table
pipeline_data_volume

# Data Freshness
pipeline_data_freshness_hours
```

## 🔄 Maintenance

### Starting/Stopping Services
```bash
# Start monitoring stack
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Stop monitoring stack
docker-compose -f docker-compose.monitoring.yml down

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f

# Restart specific service
docker-compose -f docker-compose.monitoring.yml restart grafana
```

### Updating Configuration
1. Edit configuration files in `monitoring/` directory
2. Restart the affected services
3. Reload Prometheus configuration: `curl -X POST http://localhost:9090/-/reload`

### Backup
```bash
# Backup Grafana dashboards
docker cp grafana:/var/lib/grafana/grafana.db ./backup/

# Backup Prometheus data
docker cp prometheus:/prometheus ./backup/
```

## 🆘 Troubleshooting

### Common Issues

1. **Services won't start**
   - Check Docker is running: `docker ps`
   - Check ports are available: `lsof -i :3000,9090,9093`

2. **No metrics appearing**
   - Verify metrics exporter is running
   - Check Prometheus targets: http://localhost:9090/targets
   - Verify database connection

3. **Grafana login issues**
   - Default credentials: admin/admin123
   - Reset password: `docker exec -it grafana grafana-cli admin reset-admin-password newpassword`

4. **High resource usage**
   - Adjust scrape intervals in prometheus.yml
   - Reduce retention period
   - Limit metrics collection

### Useful Commands
```bash
# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# View service logs
docker-compose -f docker-compose.monitoring.yml logs prometheus
docker-compose -f docker-compose.monitoring.yml logs grafana

# Test metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Query Language (PromQL)](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Examples](https://grafana.com/grafana/dashboards/)

## 🎉 Success!

Once everything is running, you'll have:
- ✅ Real-time system monitoring
- ✅ Database performance tracking
- ✅ Pipeline health monitoring
- ✅ Automated alerting
- ✅ Historical data analysis
- ✅ Professional monitoring setup

Your quantitative finance pipeline is now monitored with industry-standard tools! 🚀
