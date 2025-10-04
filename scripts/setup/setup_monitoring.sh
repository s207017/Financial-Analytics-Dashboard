#!/bin/bash

# Setup script for Prometheus + Grafana monitoring stack
# for the Quantitative Finance Pipeline

echo "🚀 Setting up Prometheus + Grafana monitoring stack..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Create monitoring directories
echo "📁 Creating monitoring directories..."
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/grafana/dashboards

# Install Python dependencies for metrics exporter
echo "📦 Installing Python dependencies..."
pip install prometheus_client psutil

# Start the monitoring stack
echo "🐳 Starting monitoring stack with Docker Compose..."
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.monitoring.yml ps

echo ""
echo "✅ Monitoring stack setup complete!"
echo ""
echo "🌐 Access URLs:"
echo "   • Grafana Dashboard: http://localhost:3000"
echo "     Username: admin"
echo "     Password: admin123"
echo ""
echo "   • Prometheus: http://localhost:9090"
echo ""
echo "   • Alertmanager: http://localhost:9093"
echo ""
echo "📊 Next steps:"
echo "   1. Start the metrics exporter: python3 -m src.monitoring.metrics_exporter"
echo "   2. Access Grafana and import dashboards"
echo "   3. Configure alerts in Alertmanager"
echo ""
echo "🛑 To stop monitoring: docker-compose -f docker-compose.monitoring.yml down"
