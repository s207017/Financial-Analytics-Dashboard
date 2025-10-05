# Kubernetes Deployment Guide

## 🎯 Overview

This guide walks you through deploying the Quantitative Finance Pipeline to Kubernetes, covering different environments and deployment strategies.

## 📋 Prerequisites

### Required Tools
- **kubectl**: Kubernetes command-line tool
- **Docker**: For building container images
- **Kubernetes Cluster**: Minikube, Docker Desktop, or cloud provider
- **Ingress Controller**: NGINX Ingress Controller (recommended)

### Cluster Requirements
- **CPU**: Minimum 4 cores
- **Memory**: Minimum 8GB RAM
- **Storage**: Minimum 50GB for persistent volumes
- **Network**: Ingress controller installed

## 🚀 Deployment Options

### Option 1: Quick Deploy (Recommended for Development)

```bash
# Navigate to kubernetes directory
cd deployment/kubernetes

# Run the deployment script
./deploy.sh
```

This will:
- Build Docker images
- Apply all Kubernetes manifests
- Wait for services to be ready
- Display access URLs

### Option 2: Manual Deploy

```bash
# Apply base infrastructure
kubectl apply -f base/

# Apply monitoring stack
kubectl apply -f monitoring/

# Check deployment status
kubectl get pods -n quant-finance-pipeline
```

### Option 3: Environment-Specific Deploy

#### Development Environment
```bash
# Deploy with development settings
kubectl apply -k overlays/dev/
```

#### Production Environment
```bash
# Deploy with production settings
kubectl apply -k overlays/prod/
```

## 🔧 Configuration

### Environment Variables

Key configuration is managed through ConfigMaps:

```yaml
# base/configmap.yaml
data:
  DATABASE_URL: "postgresql://postgres:password@postgres-service:5432/quant_finance"
  REDIS_URL: "redis://redis-service:6379"
  ENVIRONMENT: "production"
```

### Secrets Management

Sensitive data is stored in Kubernetes Secrets:

```yaml
# base/secrets.yaml
data:
  POSTGRES_PASSWORD: cGFzc3dvcmQ=  # Base64 encoded
  POSTGRES_USER: cG9zdGdyZXM=
```

### Resource Limits

Each service has defined resource constraints:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

## 📊 Service Architecture

### Core Services
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   Main App      │    │   Scheduler     │
│   (Port 8051)   │    │   (Port 8050)   │    │   (Background)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐
         │   PostgreSQL    │    │     Redis       │
         │   (Port 5432)   │    │   (Port 6379)   │
         └─────────────────┘    └─────────────────┘
```

### Monitoring Stack
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │     Grafana     │    │   Exporters     │
│   (Port 9090)   │    │   (Port 3000)   │    │  (Various)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🌐 Access Configuration

### Local Development

1. **Add hosts entries**:
   ```bash
   sudo nano /etc/hosts
   ```
   
   Add these lines:
   ```
   127.0.0.1 quant-finance.local
   127.0.0.1 prometheus.quant-finance.local
   127.0.0.1 grafana.quant-finance.local
   ```

2. **Access services**:
   - Dashboard: http://quant-finance.local:8051
   - Prometheus: http://prometheus.quant-finance.local:9090
   - Grafana: http://grafana.quant-finance.local:3000

### Production Access

Configure your DNS or load balancer to point to the ingress controller.

## 🔍 Monitoring and Observability

### Metrics Collection

The deployment includes comprehensive monitoring:

- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Portfolio counts, analytics calculations
- **Database Metrics**: Connection counts, query performance
- **Cache Metrics**: Hit/miss ratios, memory usage

### Grafana Dashboards

Pre-configured dashboards for:
- System overview
- Application performance
- Database metrics
- Redis cache performance
- Portfolio analytics

### Alerting

Built-in alerts for:
- High resource usage
- Service downtime
- Database connectivity issues
- Cache performance degradation

## 🛠️ Management Commands

### View Resources
```bash
# All resources in namespace
kubectl get all -n quant-finance-pipeline

# Specific resource types
kubectl get pods -n quant-finance-pipeline
kubectl get services -n quant-finance-pipeline
kubectl get deployments -n quant-finance-pipeline
kubectl get pvc -n quant-finance-pipeline
```

### View Logs
```bash
# Application logs
kubectl logs -f deployment/quant-finance-app -n quant-finance-pipeline

# Dashboard logs
kubectl logs -f deployment/quant-finance-dashboard -n quant-finance-pipeline

# All logs with label selector
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

# Rollback if needed
kubectl rollout undo deployment/quant-finance-app -n quant-finance-pipeline
```

### Backup and Restore
```bash
# Backup PostgreSQL data
kubectl exec -it deployment/postgres -n quant-finance-pipeline -- pg_dump -U postgres quant_finance > backup.sql

# Restore PostgreSQL data
kubectl exec -i deployment/postgres -n quant-finance-pipeline -- psql -U postgres quant_finance < backup.sql
```

## 🧹 Cleanup

### Complete Removal
```bash
# Use the cleanup script
./undeploy.sh

# Or manually delete namespace
kubectl delete namespace quant-finance-pipeline
```

### Partial Cleanup
```bash
# Delete specific deployments
kubectl delete deployment quant-finance-app -n quant-finance-pipeline

# Delete specific services
kubectl delete service app-service -n quant-finance-pipeline
```

## 🔍 Troubleshooting

### Common Issues

1. **Pods stuck in Pending state**:
   ```bash
   kubectl describe pod <pod-name> -n quant-finance-pipeline
   # Check for resource constraints or volume issues
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
   kubectl describe pvc <pvc-name> -n quant-finance-pipeline
   ```

4. **Image pull errors**:
   ```bash
   kubectl describe pod <pod-name> -n quant-finance-pipeline
   # Check image name and registry access
   ```

### Health Checks

All services include health checks:
- **Liveness Probes**: Restart unhealthy containers
- **Readiness Probes**: Ensure containers are ready to serve traffic
- **Init Containers**: Wait for dependencies before starting

### Debug Commands
```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n quant-finance-pipeline

# Check pod logs
kubectl logs <pod-name> -n quant-finance-pipeline

# Execute commands in pod
kubectl exec -it <pod-name> -n quant-finance-pipeline -- /bin/bash

# Check service endpoints
kubectl get endpoints -n quant-finance-pipeline
```

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

### Scaling
- Implement horizontal pod autoscaling
- Use cluster autoscaling for node management
- Monitor resource usage and adjust limits
- Consider using StatefulSets for stateful services

## 🤝 Contributing

When modifying Kubernetes manifests:
1. Test changes in development environment
2. Update documentation
3. Follow Kubernetes best practices
4. Ensure backward compatibility
5. Use Kustomize for environment-specific configurations
