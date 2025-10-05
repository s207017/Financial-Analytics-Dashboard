#!/usr/bin/env python3
"""
Test script for monitoring setup
"""

import requests
import time
import sys
from datetime import datetime

def test_service_health(service_name, url, expected_status=200):
    """Test if a service is healthy."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"✅ {service_name} is healthy")
            return True
        else:
            print(f"❌ {service_name} returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name} is not accessible: {e}")
        return False

def test_metrics_endpoint(url):
    """Test if metrics endpoint is working."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            metrics_text = response.text
            if "quant_finance_" in metrics_text:
                print(f"✅ Metrics endpoint is working and contains custom metrics")
                return True
            else:
                print(f"⚠️  Metrics endpoint is working but no custom metrics found")
                return False
        else:
            print(f"❌ Metrics endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Metrics endpoint is not accessible: {e}")
        return False

def main():
    """Run monitoring tests."""
    print("🔍 Testing Monitoring Stack Health...")
    print("=" * 50)
    
    services = [
        ("Prometheus", "http://localhost:9090/-/healthy"),
        ("Grafana", "http://localhost:3000/api/health"),
        ("Alertmanager", "http://localhost:9093/-/healthy"),
        ("Node Exporter", "http://localhost:9100/metrics"),
        ("Redis Exporter", "http://localhost:9121/metrics"),
        ("PostgreSQL Exporter", "http://localhost:9187/metrics"),
        ("cAdvisor", "http://localhost:8080/healthz"),
    ]
    
    healthy_services = 0
    total_services = len(services)
    
    for service_name, url in services:
        if test_service_health(service_name, url):
            healthy_services += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Service Health Summary: {healthy_services}/{total_services} services healthy")
    
    # Test custom metrics
    print("\n🔍 Testing Custom Metrics...")
    print("=" * 50)
    
    if test_metrics_endpoint("http://localhost:8000/metrics"):
        print("✅ Custom application metrics are working")
    else:
        print("❌ Custom application metrics are not working")
        print("   Make sure the application is running and exposing metrics on port 8000")
    
    # Test Prometheus targets
    print("\n🔍 Testing Prometheus Targets...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        if response.status_code == 200:
            targets_data = response.json()
            active_targets = 0
            total_targets = 0
            
            for target in targets_data.get('data', {}).get('activeTargets', []):
                total_targets += 1
                if target.get('health') == 'up':
                    active_targets += 1
                    print(f"✅ {target.get('labels', {}).get('job', 'Unknown')} - UP")
                else:
                    print(f"❌ {target.get('labels', {}).get('job', 'Unknown')} - DOWN")
            
            print(f"\n📊 Prometheus Targets: {active_targets}/{total_targets} active")
        else:
            print("❌ Could not fetch Prometheus targets")
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to Prometheus: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Monitoring Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Access Grafana at http://localhost:3000 (admin/admin123)")
    print("2. Check Prometheus at http://localhost:9090")
    print("3. View alerts at http://localhost:9093")
    print("4. Import dashboards from grafana/dashboards/")

if __name__ == "__main__":
    main()
