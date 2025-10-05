# Kubernetes Testing Guide

## 🎯 Overview

This guide shows you how to properly test if Kubernetes is actually working and doing its job. We'll cover local cluster setup, deployment testing, and verification methods.

## 🚀 Setting Up Local Kubernetes

### Option 1: Minikube (Recommended)

```bash
# Install Minikube (macOS)
brew install minikube

# Start Minikube cluster
minikube start --driver=docker --memory=4096 --cpus=2

# Verify cluster is running
kubectl cluster-info
```

### Option 2: Docker Desktop Kubernetes

```bash
# Enable Kubernetes in Docker Desktop
# Go to Docker Desktop > Settings > Kubernetes > Enable Kubernetes

# Verify cluster
kubectl cluster-info
```

### Option 3: Kind (Kubernetes in Docker)

```bash
# Install Kind
brew install kind

# Create cluster
kind create cluster --name quant-finance

# Verify cluster
kubectl cluster-info
```

## 🧪 Testing Kubernetes Functionality

### 1. **Basic Cluster Health Check**

```bash
# Check cluster status
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check system pods
kubectl get pods -n kube-system

# Check cluster version
kubectl version
```

### 2. **Deploy Your Application**

```bash
# Navigate to kubernetes directory
cd deployment/kubernetes

# Deploy the application
./deploy.sh

# Or manual deployment
kubectl apply -f base/
kubectl apply -f monitoring/
```

### 3. **Verify Deployment**

```bash
# Check all resources
kubectl get all -n quant-finance-pipeline

# Check pods status
kubectl get pods -n quant-finance-pipeline

# Check services
kubectl get services -n quant-finance-pipeline

# Check deployments
kubectl get deployments -n quant-finance-pipeline
```

### 4. **Test Pod Functionality**

```bash
# Check pod logs
kubectl logs -f deployment/quant-finance-dashboard -n quant-finance-pipeline

# Execute commands in pod
kubectl exec -it deployment/quant-finance-app -n quant-finance-pipeline -- /bin/bash

# Check pod resource usage
kubectl top pods -n quant-finance-pipeline
```

### 5. **Test Service Discovery**

```bash
# Test internal service communication
kubectl exec -it deployment/quant-finance-app -n quant-finance-pipeline -- curl postgres-service:5432

# Test service endpoints
kubectl get endpoints -n quant-finance-pipeline

# Test DNS resolution
kubectl exec -it deployment/quant-finance-app -n quant-finance-pipeline -- nslookup postgres-service
```

### 6. **Test Load Balancing**

```bash
# Scale deployment
kubectl scale deployment quant-finance-dashboard --replicas=3 -n quant-finance-pipeline

# Check load distribution
kubectl get pods -n quant-finance-pipeline -l app=quant-finance-dashboard

# Test service load balancing
kubectl exec -it deployment/quant-finance-app -n quant-finance-pipeline -- curl dashboard-service:8051
```

### 7. **Test Self-Healing**

```bash
# Delete a pod
kubectl delete pod -l app=quant-finance-dashboard -n quant-finance-pipeline

# Watch it get recreated
kubectl get pods -n quant-finance-pipeline -w

# Check pod events
kubectl get events -n quant-finance-pipeline
```

### 8. **Test Rolling Updates**

```bash
# Update image
kubectl set image deployment/quant-finance-dashboard dashboard=quant-finance-pipeline-dashboard:v2.0 -n quant-finance-pipeline

# Watch rolling update
kubectl rollout status deployment/quant-finance-dashboard -n quant-finance-pipeline

# Check rollout history
kubectl rollout history deployment/quant-finance-dashboard -n quant-finance-pipeline

# Rollback if needed
kubectl rollout undo deployment/quant-finance-dashboard -n quant-finance-pipeline
```

### 9. **Test Resource Management**

```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n quant-finance-pipeline

# Check resource limits
kubectl describe pod -l app=quant-finance-dashboard -n quant-finance-pipeline

# Test resource constraints
kubectl exec -it deployment/quant-finance-dashboard -n quant-finance-pipeline -- stress --cpu 2 --timeout 30s
```

### 10. **Test Persistent Storage**

```bash
# Check persistent volumes
kubectl get pv
kubectl get pvc -n quant-finance-pipeline

# Test data persistence
kubectl exec -it deployment/postgres -n quant-finance-pipeline -- psql -U postgres -c "CREATE TABLE test (id int);"

# Delete and recreate pod
kubectl delete pod -l app=postgres -n quant-finance-pipeline
kubectl get pods -n quant-finance-pipeline -w

# Verify data persistence
kubectl exec -it deployment/postgres -n quant-finance-pipeline -- psql -U postgres -c "SELECT * FROM test;"
```

## 🔍 Advanced Testing

### 1. **Network Policies Testing**

```bash
# Apply network policy
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-network-policy
  namespace: quant-finance-pipeline
spec:
  podSelector:
    matchLabels:
      app: quant-finance-dashboard
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: quant-finance-app
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
EOF

# Test network isolation
kubectl exec -it deployment/quant-finance-app -n quant-finance-pipeline -- curl dashboard-service:8051
```

### 2. **ConfigMap and Secret Testing**

```bash
# Update ConfigMap
kubectl patch configmap app-config -n quant-finance-pipeline --patch '{"data":{"ENVIRONMENT":"testing"}}'

# Restart deployment to pick up changes
kubectl rollout restart deployment/quant-finance-app -n quant-finance-pipeline

# Verify environment variable
kubectl exec -it deployment/quant-finance-app -n quant-finance-pipeline -- env | grep ENVIRONMENT
```

### 3. **Health Check Testing**

```bash
# Check health check status
kubectl describe pod -l app=quant-finance-dashboard -n quant-finance-pipeline

# Simulate health check failure
kubectl exec -it deployment/quant-finance-dashboard -n quant-finance-pipeline -- rm /app/health

# Watch pod restart
kubectl get pods -n quant-finance-pipeline -w
```

### 4. **Ingress Testing**

```bash
# Check ingress status
kubectl get ingress -n quant-finance-pipeline

# Test external access
curl -H "Host: quant-finance.local" http://localhost:8051

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

## 📊 Monitoring and Observability Testing

### 1. **Prometheus Metrics**

```bash
# Port forward to Prometheus
kubectl port-forward service/prometheus-service 9090:9090 -n quant-finance-pipeline

# Check metrics in browser
open http://localhost:9090

# Query metrics
curl http://localhost:9090/api/v1/query?query=up
```

### 2. **Grafana Dashboards**

```bash
# Port forward to Grafana
kubectl port-forward service/grafana-service 3000:3000 -n quant-finance-pipeline

# Access Grafana
open http://localhost:3000
# Login: admin/admin123
```

### 3. **Application Metrics**

```bash
# Check custom metrics
kubectl exec -it deployment/quant-finance-app -n quant-finance-pipeline -- curl localhost:8000/metrics

# Test metrics endpoint
curl http://localhost:8000/metrics
```

## 🚨 Failure Testing

### 1. **Node Failure Simulation**

```bash
# Drain a node (if multi-node cluster)
kubectl drain minikube --ignore-daemonsets

# Watch pods reschedule
kubectl get pods -n quant-finance-pipeline -o wide

# Uncordon node
kubectl uncordon minikube
```

### 2. **Service Failure Testing**

```bash
# Scale service to 0
kubectl scale deployment quant-finance-dashboard --replicas=0 -n quant-finance-pipeline

# Test service unavailability
kubectl exec -it deployment/quant-finance-app -n quant-finance-pipeline -- curl dashboard-service:8051

# Scale back up
kubectl scale deployment quant-finance-dashboard --replicas=2 -n quant-finance-pipeline
```

### 3. **Database Failure Testing**

```bash
# Delete database pod
kubectl delete pod -l app=postgres -n quant-finance-pipeline

# Watch application behavior
kubectl logs -f deployment/quant-finance-app -n quant-finance-pipeline

# Check database recovery
kubectl get pods -n quant-finance-pipeline -l app=postgres
```

## 📋 Testing Checklist

### ✅ Basic Functionality
- [ ] Cluster is running and healthy
- [ ] All pods are running and ready
- [ ] Services are accessible
- [ ] Ingress is working
- [ ] Persistent volumes are mounted

### ✅ High Availability
- [ ] Pods restart automatically on failure
- [ ] Load balancing works across replicas
- [ ] Rolling updates work without downtime
- [ ] Services remain available during pod restarts

### ✅ Resource Management
- [ ] Resource limits are enforced
- [ ] Pods are scheduled on available nodes
- [ ] Resource usage is within limits
- [ ] OOMKilled pods are restarted

### ✅ Networking
- [ ] Service discovery works
- [ ] DNS resolution works
- [ ] Network policies are enforced
- [ ] External access works

### ✅ Storage
- [ ] Persistent volumes are created
- [ ] Data persists across pod restarts
- [ ] Storage classes work
- [ ] Backup/restore works

### ✅ Monitoring
- [ ] Prometheus collects metrics
- [ ] Grafana displays dashboards
- [ ] Alerts are configured
- [ ] Logs are accessible

## 🎯 What to Look For

### **Success Indicators:**
- All pods show `Running` status
- Services have valid endpoints
- Health checks pass
- Metrics are being collected
- Logs show no errors
- External access works

### **Failure Indicators:**
- Pods stuck in `Pending` or `CrashLoopBackOff`
- Services have no endpoints
- Health checks failing
- Network connectivity issues
- Resource exhaustion
- Persistent volume issues

## 🔧 Troubleshooting Commands

```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n quant-finance-pipeline

# Check pod logs
kubectl logs <pod-name> -n quant-finance-pipeline

# Check events
kubectl get events -n quant-finance-pipeline --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n quant-finance-pipeline

# Check service endpoints
kubectl get endpoints -n quant-finance-pipeline

# Check persistent volumes
kubectl get pv,pvc -n quant-finance-pipeline
```

## 🎉 Conclusion

This comprehensive testing approach will verify that Kubernetes is actually doing its job:

1. **Orchestration**: Managing pod lifecycle
2. **Service Discovery**: Enabling communication between services
3. **Load Balancing**: Distributing traffic across replicas
4. **Self-Healing**: Restarting failed containers
5. **Rolling Updates**: Deploying new versions without downtime
6. **Resource Management**: Enforcing limits and requests
7. **Storage Management**: Providing persistent storage
8. **Monitoring**: Collecting metrics and logs

By following this guide, you'll have confidence that your Kubernetes deployment is working correctly and providing the benefits of container orchestration.
