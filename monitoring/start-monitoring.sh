#!/bin/bash

# Start Monitoring Stack for Quantitative Finance Pipeline
# This script starts Prometheus, Grafana, and related monitoring services

set -e

echo "🚀 Starting Quantitative Finance Pipeline Monitoring Stack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to monitoring directory
cd "$(dirname "$0")"

# Create necessary directories
mkdir -p grafana/dashboards
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/provisioning/datasources

echo "📊 Starting monitoring services..."

# Start the monitoring stack
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."

# Wait for Prometheus
echo "Waiting for Prometheus..."
until curl -s http://localhost:9090/-/healthy > /dev/null; do
    sleep 2
done
echo "✅ Prometheus is ready"

# Wait for Grafana
echo "Waiting for Grafana..."
until curl -s http://localhost:3000/api/health > /dev/null; do
    sleep 2
done
echo "✅ Grafana is ready"

# Wait for Redis Exporter
echo "Waiting for Redis Exporter..."
until curl -s http://localhost:9121/metrics > /dev/null; do
    sleep 2
done
echo "✅ Redis Exporter is ready"

echo ""
echo "🎉 Monitoring stack is ready!"
echo ""
echo "📊 Access URLs:"
echo "  • Grafana Dashboard:     http://localhost:3000 (admin/admin123)"
echo "  • Prometheus:            http://localhost:9090"
echo "  • Alertmanager:          http://localhost:9093"
echo "  • Node Exporter:         http://localhost:9100/metrics"
echo "  • cAdvisor:              http://localhost:8080"
echo "  • Redis Exporter:        http://localhost:9121/metrics"
echo "  • PostgreSQL Exporter:   http://localhost:9187/metrics"
echo ""
echo "📈 Available Dashboards:"
echo "  • Quantitative Finance Pipeline - Comprehensive Monitoring"
echo "  • Redis Monitoring Dashboard"
echo "  • Simple Dashboard"
echo ""
echo "🔧 To stop the monitoring stack:"
echo "  docker compose -f docker-compose.monitoring.yml down"
echo ""
echo "📝 To view logs:"
echo "  docker compose -f docker-compose.monitoring.yml logs -f"
