#!/bin/bash

# Quantitative Finance Pipeline - Kubernetes Undeploy Script

set -e

echo "🗑️  Undeploying Quantitative Finance Pipeline from Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Delete the entire namespace (this will delete all resources)
echo "🔧 Deleting namespace and all resources..."
kubectl delete namespace quant-finance-pipeline --ignore-not-found=true

echo "✅ Quantitative Finance Pipeline undeployed successfully"
echo ""
echo "📋 All resources have been removed from the cluster."
