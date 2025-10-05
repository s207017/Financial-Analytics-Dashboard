#!/bin/bash

# Comprehensive Kubernetes Functionality Test

set -e

echo "🧪 Testing Kubernetes Functionality..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    echo -e "\n${BLUE}Testing: $test_name${NC}"
    echo "Command: $test_command"
    
    if eval "$test_command" &> /dev/null; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "Expected: $expected_result"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to check if cluster is running
check_cluster() {
    echo -e "\n${YELLOW}🔍 Checking Kubernetes Cluster Status${NC}"
    
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ No Kubernetes cluster found${NC}"
        echo "Please run: ./setup-local-k8s.sh"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Kubernetes cluster is running${NC}"
    kubectl cluster-info
    echo ""
}

# Function to check namespace
check_namespace() {
    echo -e "\n${YELLOW}📁 Checking Namespace${NC}"
    
    if kubectl get namespace quant-finance-pipeline &> /dev/null; then
        echo -e "${GREEN}✅ Namespace exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Namespace not found. Creating...${NC}"
        kubectl create namespace quant-finance-pipeline
    fi
}

# Function to test basic functionality
test_basic_functionality() {
    echo -e "\n${YELLOW}🔧 Testing Basic Kubernetes Functionality${NC}"
    
    # Test 1: Cluster connectivity
    run_test "Cluster Connectivity" "kubectl cluster-info" "Cluster should be accessible"
    
    # Test 2: Node status
    run_test "Node Status" "kubectl get nodes --no-headers | grep -v NotReady" "All nodes should be ready"
    
    # Test 3: API server
    run_test "API Server" "kubectl get --raw /healthz" "API server should be healthy"
    
    # Test 4: Namespace creation
    run_test "Namespace Creation" "kubectl create namespace test-namespace --dry-run=client" "Should be able to create namespaces"
    
    # Clean up test namespace
    kubectl delete namespace test-namespace --ignore-not-found=true &> /dev/null
}

# Function to test pod functionality
test_pod_functionality() {
    echo -e "\n${YELLOW}🐳 Testing Pod Functionality${NC}"
    
    # Create a test pod
    kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: quant-finance-pipeline
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
  restartPolicy: Never
EOF
    
    # Wait for pod to be ready
    echo "Waiting for test pod to be ready..."
    kubectl wait --for=condition=Ready pod/test-pod -n quant-finance-pipeline --timeout=60s
    
    # Test 5: Pod creation
    run_test "Pod Creation" "kubectl get pod test-pod -n quant-finance-pipeline --no-headers | grep Running" "Pod should be running"
    
    # Test 6: Pod logs
    run_test "Pod Logs" "kubectl logs test-pod -n quant-finance-pipeline" "Should be able to get pod logs"
    
    # Test 7: Pod exec
    run_test "Pod Exec" "kubectl exec test-pod -n quant-finance-pipeline -- nginx -v" "Should be able to execute commands in pod"
    
    # Test 8: Pod deletion
    run_test "Pod Deletion" "kubectl delete pod test-pod -n quant-finance-pipeline" "Should be able to delete pods"
    
    # Wait for pod to be deleted
    kubectl wait --for=delete pod/test-pod -n quant-finance-pipeline --timeout=30s
}

# Function to test service functionality
test_service_functionality() {
    echo -e "\n${YELLOW}🌐 Testing Service Functionality${NC}"
    
    # Create a test deployment and service
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-deployment
  namespace: quant-finance-pipeline
spec:
  replicas: 2
  selector:
    matchLabels:
      app: test-app
  template:
    metadata:
      labels:
        app: test-app
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: test-service
  namespace: quant-finance-pipeline
spec:
  selector:
    app: test-app
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
EOF
    
    # Wait for deployment to be ready
    echo "Waiting for test deployment to be ready..."
    kubectl wait --for=condition=available deployment/test-deployment -n quant-finance-pipeline --timeout=60s
    
    # Test 9: Deployment creation
    run_test "Deployment Creation" "kubectl get deployment test-deployment -n quant-finance-pipeline --no-headers | grep 2/2" "Deployment should have 2/2 replicas"
    
    # Test 10: Service creation
    run_test "Service Creation" "kubectl get service test-service -n quant-finance-pipeline" "Service should be created"
    
    # Test 11: Service endpoints
    run_test "Service Endpoints" "kubectl get endpoints test-service -n quant-finance-pipeline" "Service should have endpoints"
    
    # Test 12: Service connectivity
    run_test "Service Connectivity" "kubectl run test-client --image=busybox --rm -i --restart=Never -n quant-finance-pipeline -- wget -qO- test-service" "Should be able to connect to service"
    
    # Test 13: Load balancing
    run_test "Load Balancing" "kubectl scale deployment test-deployment --replicas=3 -n quant-finance-pipeline" "Should be able to scale deployment"
    
    # Wait for scaling
    kubectl wait --for=condition=available deployment/test-deployment -n quant-finance-pipeline --timeout=60s
    
    # Test 14: Scaling verification
    run_test "Scaling Verification" "kubectl get deployment test-deployment -n quant-finance-pipeline --no-headers | grep 3/3" "Should have 3/3 replicas"
    
    # Clean up
    kubectl delete deployment test-deployment -n quant-finance-pipeline
    kubectl delete service test-service -n quant-finance-pipeline
}

# Function to test persistent storage
test_storage_functionality() {
    echo -e "\n${YELLOW}💾 Testing Storage Functionality${NC}"
    
    # Create a test PVC
    kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
  namespace: quant-finance-pipeline
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF
    
    # Test 15: PVC creation
    run_test "PVC Creation" "kubectl get pvc test-pvc -n quant-finance-pipeline" "PVC should be created"
    
    # Test 16: PV creation
    run_test "PV Creation" "kubectl get pv" "PV should be created"
    
    # Clean up
    kubectl delete pvc test-pvc -n quant-finance-pipeline
}

# Function to test self-healing
test_self_healing() {
    echo -e "\n${YELLOW}🔄 Testing Self-Healing Functionality${NC}"
    
    # Create a test deployment
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-healing
  namespace: quant-finance-pipeline
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test-healing
  template:
    metadata:
      labels:
        app: test-healing
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
EOF
    
    # Wait for deployment to be ready
    kubectl wait --for=condition=available deployment/test-healing -n quant-finance-pipeline --timeout=60s
    
    # Get the pod name
    POD_NAME=$(kubectl get pods -n quant-finance-pipeline -l app=test-healing -o jsonpath='{.items[0].metadata.name}')
    
    # Test 17: Pod deletion and recreation
    run_test "Pod Deletion" "kubectl delete pod $POD_NAME -n quant-finance-pipeline" "Should be able to delete pod"
    
    # Wait for pod to be recreated
    echo "Waiting for pod to be recreated..."
    kubectl wait --for=condition=Ready pod -l app=test-healing -n quant-finance-pipeline --timeout=60s
    
    # Test 18: Pod recreation
    run_test "Pod Recreation" "kubectl get pods -n quant-finance-pipeline -l app=test-healing --no-headers | grep Running" "Pod should be recreated and running"
    
    # Clean up
    kubectl delete deployment test-healing -n quant-finance-pipeline
}

# Function to test rolling updates
test_rolling_updates() {
    echo -e "\n${YELLOW}🔄 Testing Rolling Updates${NC}"
    
    # Create a test deployment
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-rolling
  namespace: quant-finance-pipeline
spec:
  replicas: 2
  selector:
    matchLabels:
      app: test-rolling
  template:
    metadata:
      labels:
        app: test-rolling
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
EOF
    
    # Wait for deployment to be ready
    kubectl wait --for=condition=available deployment/test-rolling -n quant-finance-pipeline --timeout=60s
    
    # Test 19: Rolling update
    run_test "Rolling Update" "kubectl set image deployment/test-rolling nginx=nginx:1.21 -n quant-finance-pipeline" "Should be able to update image"
    
    # Wait for rolling update to complete
    kubectl rollout status deployment/test-rolling -n quant-finance-pipeline --timeout=120s
    
    # Test 20: Rolling update completion
    run_test "Rolling Update Completion" "kubectl get deployment test-rolling -n quant-finance-pipeline --no-headers | grep 2/2" "Deployment should be updated and ready"
    
    # Clean up
    kubectl delete deployment test-rolling -n quant-finance-pipeline
}

# Function to test monitoring
test_monitoring() {
    echo -e "\n${YELLOW}📊 Testing Monitoring Functionality${NC}"
    
    # Test 21: Metrics server
    run_test "Metrics Server" "kubectl top nodes" "Should be able to get node metrics"
    
    # Test 22: Pod metrics
    run_test "Pod Metrics" "kubectl top pods -n kube-system" "Should be able to get pod metrics"
    
    # Test 23: Events
    run_test "Events" "kubectl get events -n quant-finance-pipeline" "Should be able to get events"
}

# Function to test ingress
test_ingress() {
    echo -e "\n${YELLOW}🌐 Testing Ingress Functionality${NC}"
    
    # Check if ingress controller is available
    if kubectl get pods -n ingress-nginx &> /dev/null; then
        echo -e "${GREEN}✅ Ingress controller is available${NC}"
        
        # Create a test ingress
        kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-ingress-app
  namespace: quant-finance-pipeline
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test-ingress-app
  template:
    metadata:
      labels:
        app: test-ingress-app
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: test-ingress-service
  namespace: quant-finance-pipeline
spec:
  selector:
    app: test-ingress-app
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-ingress
  namespace: quant-finance-pipeline
spec:
  rules:
  - host: test.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: test-ingress-service
            port:
              number: 80
EOF
        
        # Wait for deployment to be ready
        kubectl wait --for=condition=available deployment/test-ingress-app -n quant-finance-pipeline --timeout=60s
        
        # Test 24: Ingress creation
        run_test "Ingress Creation" "kubectl get ingress test-ingress -n quant-finance-pipeline" "Ingress should be created"
        
        # Clean up
        kubectl delete deployment test-ingress-app -n quant-finance-pipeline
        kubectl delete service test-ingress-service -n quant-finance-pipeline
        kubectl delete ingress test-ingress -n quant-finance-pipeline
    else
        echo -e "${YELLOW}⚠️  Ingress controller not available${NC}"
    fi
}

# Function to test ConfigMap and Secrets
test_config_secrets() {
    echo -e "\n${YELLOW}🔐 Testing ConfigMap and Secrets${NC}"
    
    # Create a test ConfigMap
    kubectl create configmap test-config --from-literal=key1=value1 --from-literal=key2=value2 -n quant-finance-pipeline
    
    # Test 25: ConfigMap creation
    run_test "ConfigMap Creation" "kubectl get configmap test-config -n quant-finance-pipeline" "ConfigMap should be created"
    
    # Create a test Secret
    kubectl create secret generic test-secret --from-literal=username=admin --from-literal=password=secret -n quant-finance-pipeline
    
    # Test 26: Secret creation
    run_test "Secret Creation" "kubectl get secret test-secret -n quant-finance-pipeline" "Secret should be created"
    
    # Clean up
    kubectl delete configmap test-config -n quant-finance-pipeline
    kubectl delete secret test-secret -n quant-finance-pipeline
}

# Main execution
main() {
    echo -e "${BLUE}🧪 Kubernetes Functionality Test Suite${NC}"
    echo "======================================"
    
    # Check cluster
    check_cluster
    
    # Check namespace
    check_namespace
    
    # Run tests
    test_basic_functionality
    test_pod_functionality
    test_service_functionality
    test_storage_functionality
    test_self_healing
    test_rolling_updates
    test_monitoring
    test_ingress
    test_config_secrets
    
    # Print results
    echo -e "\n${BLUE}📊 Test Results${NC}"
    echo "==============="
    echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
    echo -e "${BLUE}📈 Total Tests: $((TESTS_PASSED + TESTS_FAILED))${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All tests passed! Kubernetes is working correctly.${NC}"
        exit 0
    else
        echo -e "\n${RED}⚠️  Some tests failed. Check the output above for details.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
