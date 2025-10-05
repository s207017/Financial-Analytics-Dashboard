#!/bin/bash

# Setup Local Kubernetes for Testing

set -e

echo "🚀 Setting up local Kubernetes cluster for testing..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    echo "   macOS: brew install kubectl"
    echo "   Linux: curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    exit 1
fi

echo "✅ kubectl is available"

# Check for existing cluster
if kubectl cluster-info &> /dev/null; then
    echo "⚠️  Kubernetes cluster already running:"
    kubectl cluster-info
    echo ""
    read -p "Do you want to continue with existing cluster? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 0
    fi
else
    echo "🔧 No Kubernetes cluster found. Setting up..."
    
    # Check for Minikube
    if command -v minikube &> /dev/null; then
        echo "📦 Using Minikube..."
        minikube start --driver=docker --memory=4096 --cpus=2
        minikube addons enable ingress
        minikube addons enable metrics-server
    # Check for Docker Desktop
    elif docker info &> /dev/null && docker context ls | grep -q "desktop-linux"; then
        echo "📦 Using Docker Desktop Kubernetes..."
        echo "Please enable Kubernetes in Docker Desktop:"
        echo "1. Open Docker Desktop"
        echo "2. Go to Settings > Kubernetes"
        echo "3. Check 'Enable Kubernetes'"
        echo "4. Click 'Apply & Restart'"
        echo ""
        read -p "Press Enter when Kubernetes is enabled in Docker Desktop..."
    # Check for Kind
    elif command -v kind &> /dev/null; then
        echo "📦 Using Kind..."
        kind create cluster --name quant-finance --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF
        # Install NGINX Ingress
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
        kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=90s
    else
        echo "❌ No Kubernetes cluster found. Please install one of:"
        echo "   - Minikube: brew install minikube"
        echo "   - Kind: brew install kind"
        echo "   - Docker Desktop with Kubernetes enabled"
        exit 1
    fi
fi

# Verify cluster is running
echo "🔍 Verifying cluster..."
kubectl cluster-info
kubectl get nodes

# Check if ingress controller is available
if kubectl get pods -n ingress-nginx &> /dev/null; then
    echo "✅ Ingress controller is available"
else
    echo "⚠️  Ingress controller not found. Installing NGINX Ingress..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=90s
fi

# Check if metrics server is available
if kubectl get pods -n kube-system | grep -q metrics-server; then
    echo "✅ Metrics server is available"
else
    echo "⚠️  Metrics server not found. Installing..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    kubectl wait --namespace kube-system --for=condition=ready pod --selector=k8s-app=metrics-server --timeout=90s
fi

echo ""
echo "🎉 Local Kubernetes cluster is ready!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy your application:"
echo "   cd deployment/kubernetes"
echo "   ./deploy.sh"
echo ""
echo "2. Run tests:"
echo "   ./test-deployment.sh"
echo ""
echo "3. Access services:"
echo "   - Dashboard: http://quant-finance.local:8051"
echo "   - Prometheus: http://prometheus.quant-finance.local:9090"
echo "   - Grafana: http://grafana.quant-finance.local:3000"
echo ""
echo "4. Add to /etc/hosts:"
echo "   127.0.0.1 quant-finance.local"
echo "   127.0.0.1 prometheus.quant-finance.local"
echo "   127.0.0.1 grafana.quant-finance.local"
echo ""
echo "🔧 Useful commands:"
echo "   kubectl get pods -n quant-finance-pipeline"
echo "   kubectl get services -n quant-finance-pipeline"
echo "   kubectl logs -f deployment/quant-finance-dashboard -n quant-finance-pipeline"
