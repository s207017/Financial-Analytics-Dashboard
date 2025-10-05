#!/bin/bash

# Quantitative Finance Pipeline - Kubernetes Deployment Script

set -e

echo "🚀 Deploying Quantitative Finance Pipeline to Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if we can connect to a Kubernetes cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

echo "✅ Kubernetes cluster connection verified"

# Build Docker images (if not already built)
echo "📦 Building Docker images..."
docker build -t quant-finance-pipeline-app:latest .
docker build -t quant-finance-pipeline-dashboard:latest .
docker build -t quant-finance-pipeline-scheduler:latest .

echo "✅ Docker images built successfully"

# Apply Kubernetes manifests
echo "🔧 Applying Kubernetes manifests..."

# Base infrastructure
kubectl apply -f base/namespace.yaml
kubectl apply -f base/configmap.yaml
kubectl apply -f base/secrets.yaml

# Core services
kubectl apply -f base/postgres.yaml
kubectl apply -f base/redis.yaml

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n quant-finance-pipeline --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n quant-finance-pipeline --timeout=300s

# Application services
kubectl apply -f base/app.yaml
kubectl apply -f base/dashboard.yaml
kubectl apply -f base/scheduler.yaml

# Monitoring stack
kubectl apply -f monitoring/prometheus.yaml
kubectl apply -f monitoring/grafana.yaml
kubectl apply -f monitoring/exporters.yaml

# Ingress
kubectl apply -f base/ingress.yaml

echo "✅ All Kubernetes manifests applied successfully"

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment -l app=quant-finance-app -n quant-finance-pipeline --timeout=300s
kubectl wait --for=condition=available deployment -l app=quant-finance-dashboard -n quant-finance-pipeline --timeout=300s
kubectl wait --for=condition=available deployment -l app=prometheus -n quant-finance-pipeline --timeout=300s
kubectl wait --for=condition=available deployment -l app=grafana -n quant-finance-pipeline --timeout=300s

echo "✅ All deployments are ready"

# Display access information
echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Access URLs:"
echo "  • Dashboard: http://quant-finance.local:8051"
echo "  • Prometheus: http://prometheus.quant-finance.local:9090"
echo "  • Grafana: http://grafana.quant-finance.local:3000 (admin/admin123)"
echo ""
echo "🔧 To access services locally, add these entries to your /etc/hosts file:"
echo "  127.0.0.1 quant-finance.local"
echo "  127.0.0.1 prometheus.quant-finance.local"
echo "  127.0.0.1 grafana.quant-finance.local"
echo ""
echo "📋 Useful commands:"
echo "  • View pods: kubectl get pods -n quant-finance-pipeline"
echo "  • View services: kubectl get services -n quant-finance-pipeline"
echo "  • View logs: kubectl logs -f deployment/quant-finance-dashboard -n quant-finance-pipeline"
echo "  • Delete deployment: kubectl delete namespace quant-finance-pipeline"
echo ""
