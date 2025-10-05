#!/bin/bash

# Quantitative Finance Pipeline - Kubernetes Deployment Test Script

set -e

echo "🧪 Testing Kubernetes deployment..."

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

# Test namespace
echo "🔍 Checking namespace..."
if kubectl get namespace quant-finance-pipeline &> /dev/null; then
    echo "✅ Namespace exists"
else
    echo "❌ Namespace not found"
    exit 1
fi

# Test pods
echo "🔍 Checking pods..."
PODS=$(kubectl get pods -n quant-finance-pipeline --no-headers | wc -l)
if [ $PODS -gt 0 ]; then
    echo "✅ Found $PODS pods"
    kubectl get pods -n quant-finance-pipeline
else
    echo "❌ No pods found"
    exit 1
fi

# Test services
echo "🔍 Checking services..."
SERVICES=$(kubectl get services -n quant-finance-pipeline --no-headers | wc -l)
if [ $SERVICES -gt 0 ]; then
    echo "✅ Found $SERVICES services"
    kubectl get services -n quant-finance-pipeline
else
    echo "❌ No services found"
    exit 1
fi

# Test deployments
echo "🔍 Checking deployments..."
DEPLOYMENTS=$(kubectl get deployments -n quant-finance-pipeline --no-headers | wc -l)
if [ $DEPLOYMENTS -gt 0 ]; then
    echo "✅ Found $DEPLOYMENTS deployments"
    kubectl get deployments -n quant-finance-pipeline
else
    echo "❌ No deployments found"
    exit 1
fi

# Test persistent volumes
echo "🔍 Checking persistent volumes..."
PVC=$(kubectl get pvc -n quant-finance-pipeline --no-headers | wc -l)
if [ $PVC -gt 0 ]; then
    echo "✅ Found $PVC persistent volume claims"
    kubectl get pvc -n quant-finance-pipeline
else
    echo "❌ No persistent volume claims found"
fi

# Test ingress
echo "🔍 Checking ingress..."
if kubectl get ingress quant-finance-ingress -n quant-finance-pipeline &> /dev/null; then
    echo "✅ Ingress found"
    kubectl get ingress -n quant-finance-pipeline
else
    echo "⚠️  Ingress not found (this is optional)"
fi

# Test pod readiness
echo "🔍 Checking pod readiness..."
READY_PODS=$(kubectl get pods -n quant-finance-pipeline --field-selector=status.phase=Running --no-headers | wc -l)
TOTAL_PODS=$(kubectl get pods -n quant-finance-pipeline --no-headers | wc -l)

if [ $READY_PODS -eq $TOTAL_PODS ] && [ $TOTAL_PODS -gt 0 ]; then
    echo "✅ All $TOTAL_PODS pods are running"
else
    echo "⚠️  $READY_PODS out of $TOTAL_PODS pods are running"
    echo "Pods status:"
    kubectl get pods -n quant-finance-pipeline
fi

# Test service endpoints
echo "🔍 Checking service endpoints..."
kubectl get endpoints -n quant-finance-pipeline

echo ""
echo "🎉 Kubernetes deployment test completed!"
echo ""
echo "📊 Summary:"
echo "  • Namespace: quant-finance-pipeline"
echo "  • Pods: $TOTAL_PODS (Running: $READY_PODS)"
echo "  • Services: $SERVICES"
echo "  • Deployments: $DEPLOYMENTS"
echo "  • PVCs: $PVC"
echo ""
echo "🔧 Next steps:"
echo "  • Check logs: kubectl logs -f deployment/quant-finance-dashboard -n quant-finance-pipeline"
echo "  • Access dashboard: http://quant-finance.local:8051"
echo "  • Access monitoring: http://grafana.quant-finance.local:3000"
echo ""
