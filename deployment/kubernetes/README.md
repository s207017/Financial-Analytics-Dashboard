# Quantitative Finance Pipeline - Kubernetes Deployment

This directory contains Kubernetes manifests and deployment scripts for the Quantitative Finance Pipeline project.

## 🏗️ Architecture

The Kubernetes deployment includes:

### Core Services
- **PostgreSQL**: Database with persistent storage
- **Redis**: Caching layer with persistent storage
- **Main Application**: Data processing and analytics engine
- **Dashboard**: Interactive web interface
- **Scheduler**: Automated task scheduling

### Monitoring Stack
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Node Exporter**: System metrics
- **cAdvisor**: Container metrics
- **PostgreSQL Exporter**: Database metrics
- **Redis Exporter**: Cache metrics

## 📁 Directory Structure

```
deployment/kubernetes/
├── base/                    # Base Kubernetes manifests
│   ├── namespace.yaml      # Namespace definition
│   ├── configmap.yaml      # Application configuration
│   ├── secrets.yaml        # Sensitive data
│   ├── postgres.yaml       # PostgreSQL deployment
│   ├── redis.yaml          # Redis deployment
│   ├── app.yaml            # Main application
│   ├── dashboard.yaml      # Dashboard service
│   ├── scheduler.yaml      # Scheduler service
│   └── ingress.yaml        # External access
├── monitoring/             # Monitoring stack
│   ├── prometheus.yaml     # Prometheus configuration
│   ├── grafana.yaml        # Grafana deployment
│   └── exporters.yaml      # Metrics exporters
├── overlays/               # Environment-specific configs
│   ├── dev/               # Development environment
│   └── prod/              # Production environment
├── deploy.sh              # Deployment script
├── undeploy.sh            # Cleanup script
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes Cluster**: Minikube, Docker Desktop, or cloud provider
2. **kubectl**: Kubernetes command-line tool
3. **Docker**: For building images
4. **Ingress Controller**: NGINX Ingress Controller (recommended)

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd deployment/kubernetes
   ```

2. **Deploy the application**:
   ```bash
   ./deploy.sh
   ```

3. **Access the services**:
   - Dashboard: http://quant-finance.local:8051
   - Prometheus: http://prometheus.quant-finance.local:9090
   - Grafana: http://grafana.quant-finance.local:3000 (admin/admin123)

### Local Access Setup

Add these entries to your `/etc/hosts` file:
```
127.0.0.1 quant-finance.local
127.0.0.1 prometheus.quant-finance.local
127.0.0.1 grafana.quant-finance.local
```

## 🔧 Configuration

### Environment Variables

Key configuration is managed through ConfigMaps and Secrets:

- **ConfigMap**: Database URLs, Redis settings, API keys
- **Secrets**: Database passwords, sensitive credentials

### Resource Limits

Each service has defined resource requests and limits:
- **CPU**: 100m - 500m
- **Memory**: 256Mi - 1Gi

### Scaling

The application supports horizontal scaling:
- **App**: 2 replicas
- **Dashboard**: 2 replicas
- **Scheduler**: 1 replica (singleton)

## 📊 Monitoring

### Metrics Collection

- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Portfolio counts, analytics calculations
- **Database Metrics**: Connection counts, query performance
- **Cache Metrics**: Hit/miss ratios, memory usage

### Alerting

Pre-configured alerts for:
- High CPU usage (>80%)
- High memory usage (>85%)
- Service downtime
- Database connectivity issues

## 🛠️ Management Commands

### View Resources
```bash
# All pods
kubectl get pods -n quant-finance-pipeline

# All services
kubectl get services -n quant-finance-pipeline

# All deployments
kubectl get deployments -n quant-finance-pipeline
```

### View Logs
```bash
# Application logs
kubectl logs -f deployment/quant-finance-app -n quant-finance-pipeline

# Dashboard logs
kubectl logs -f deployment/quant-finance-dashboard -n quant-finance-pipeline

# All logs
kubectl logs -f -l app=quant-finance-app -n quant-finance-pipeline
```

### Scale Services
```bash
# Scale dashboard
kubectl scale deployment quant-finance-dashboard --replicas=3 -n quant-finance-pipeline

# Scale application
kubectl scale deployment quant-finance-app --replicas=3 -n quant-finance-pipeline
```

### Update Configuration
```bash
# Update ConfigMap
kubectl apply -f base/configmap.yaml

# Restart deployments to pick up changes
kubectl rollout restart deployment/quant-finance-app -n quant-finance-pipeline
```

## 🔄 Updates and Maintenance

### Rolling Updates
```bash
# Update application image
kubectl set image deployment/quant-finance-app app=quant-finance-pipeline-app:v2.0 -n quant-finance-pipeline

# Check rollout status
kubectl rollout status deployment/quant-finance-app -n quant-finance-pipeline
```

### Backup and Restore
```bash
# Backup PostgreSQL data
kubectl exec -it deployment/postgres -n quant-finance-pipeline -- pg_dump -U postgres quant_finance > backup.sql

# Restore PostgreSQL data
kubectl exec -i deployment/postgres -n quant-finance-pipeline -- psql -U postgres quant_finance < backup.sql
```

## 🧹 Cleanup

To remove all resources:
```bash
./undeploy.sh
```

Or manually:
```bash
kubectl delete namespace quant-finance-pipeline
```

## 🔍 Troubleshooting

### Common Issues

1. **Pods not starting**:
   ```bash
   kubectl describe pod <pod-name> -n quant-finance-pipeline
   kubectl logs <pod-name> -n quant-finance-pipeline
   ```

2. **Services not accessible**:
   ```bash
   kubectl get endpoints -n quant-finance-pipeline
   kubectl describe service <service-name> -n quant-finance-pipeline
   ```

3. **Persistent volume issues**:
   ```bash
   kubectl get pv
   kubectl get pvc -n quant-finance-pipeline
   ```

### Health Checks

All services include health checks:
- **Liveness Probes**: Restart unhealthy containers
- **Readiness Probes**: Ensure containers are ready to serve traffic
- **Init Containers**: Wait for dependencies before starting

## 📈 Production Considerations

### Security
- Use proper secrets management (e.g., Kubernetes Secrets, external secret operators)
- Enable RBAC (Role-Based Access Control)
- Use network policies for traffic isolation
- Regular security updates

### Performance
- Adjust resource limits based on load testing
- Use node affinity for better performance
- Consider using StatefulSets for databases
- Implement horizontal pod autoscaling

### High Availability
- Deploy across multiple availability zones
- Use anti-affinity rules for pod distribution
- Implement proper backup strategies
- Monitor and alert on critical metrics

## 🤝 Contributing

When modifying Kubernetes manifests:
1. Test changes in development environment
2. Update documentation
3. Follow Kubernetes best practices
4. Ensure backward compatibility
