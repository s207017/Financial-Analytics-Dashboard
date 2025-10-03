"""
Prometheus metrics exporter for the quantitative finance pipeline.
"""
import sys
from pathlib import Path
import logging
import time
import threading
from datetime import datetime, timedelta
import psutil
from prometheus_client import start_http_server, Counter, Histogram, Gauge, Info
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from data_access.data_service import DataService
from etl.loaders.database_loader import DatabaseLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
pipeline_requests_total = Counter('pipeline_requests_total', 'Total pipeline requests', ['method', 'endpoint'])
pipeline_request_duration = Histogram('pipeline_request_duration_seconds', 'Pipeline request duration')
pipeline_data_volume = Gauge('pipeline_data_volume', 'Data volume by table', ['table'])
pipeline_data_freshness = Gauge('pipeline_data_freshness_hours', 'Data freshness in hours')
pipeline_db_connection_time = Histogram('pipeline_db_connection_seconds', 'Database connection time')
pipeline_system_cpu = Gauge('pipeline_system_cpu_percent', 'System CPU usage percentage')
pipeline_system_memory = Gauge('pipeline_system_memory_percent', 'System memory usage percentage')
pipeline_system_disk = Gauge('pipeline_system_disk_percent', 'System disk usage percentage')
pipeline_active_connections = Gauge('pipeline_db_active_connections', 'Active database connections')
pipeline_info = Info('pipeline_info', 'Pipeline information')


class MetricsExporter:
    """Prometheus metrics exporter for the quantitative finance pipeline."""
    
    def __init__(self, db_url="postgresql://postgres:password@localhost:5432/quant_finance", port=8000):
        """Initialize the metrics exporter."""
        self.db_url = db_url
        self.port = port
        self.data_service = DataService(db_url)
        self.db_loader = DatabaseLoader(db_url)
        self.running = False
        self.metrics_thread = None
        
        # Set pipeline info
        pipeline_info.info({
            'version': '1.0.0',
            'name': 'quantitative-finance-pipeline',
            'description': 'Quantitative Finance Pipeline with Real-time Monitoring'
        })
    
    def start(self):
        """Start the metrics exporter."""
        if self.running:
            logger.warning("Metrics exporter is already running")
            return
        
        self.running = True
        
        # Start Prometheus HTTP server
        start_http_server(self.port)
        logger.info(f"Prometheus metrics server started on port {self.port}")
        
        # Start metrics collection thread
        self.metrics_thread = threading.Thread(target=self._collect_metrics_loop, daemon=True)
        self.metrics_thread.start()
        logger.info("Metrics collection started")
    
    def stop(self):
        """Stop the metrics exporter."""
        self.running = False
        if self.metrics_thread:
            self.metrics_thread.join(timeout=5)
        logger.info("Metrics exporter stopped")
    
    def _collect_metrics_loop(self):
        """Main metrics collection loop."""
        while self.running:
            try:
                self._collect_system_metrics()
                self._collect_database_metrics()
                self._collect_pipeline_metrics()
                time.sleep(10)  # Collect metrics every 10 seconds
            except Exception as e:
                logger.error(f"Error collecting metrics: {str(e)}")
                time.sleep(30)  # Wait longer on error
    
    def _collect_system_metrics(self):
        """Collect system metrics."""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            pipeline_system_cpu.set(cpu_usage)
            
            # Memory usage
            memory = psutil.virtual_memory()
            pipeline_system_memory.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            pipeline_system_disk.set(disk.percent)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
    
    def _collect_database_metrics(self):
        """Collect database metrics."""
        try:
            # Test database connection time
            start_time = time.time()
            self.db_loader.query_data("SELECT 1")
            connection_time = time.time() - start_time
            pipeline_db_connection_time.observe(connection_time)
            
            # Get active connections
            try:
                query = """
                    SELECT count(*) as connections 
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                """
                result = self.db_loader.query_data(query)
                active_connections = result.iloc[0]['connections'] if not result.empty else 0
                pipeline_active_connections.set(active_connections)
            except:
                pipeline_active_connections.set(0)
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {str(e)}")
            pipeline_db_connection_time.observe(float('inf'))
            pipeline_active_connections.set(0)
    
    def _collect_pipeline_metrics(self):
        """Collect pipeline-specific metrics."""
        try:
            # Data volume by table
            tables = ['stock_prices', 'portfolio_data', 'risk_metrics', 'technical_indicators']
            for table in tables:
                try:
                    query = f"SELECT COUNT(*) as count FROM {table}"
                    result = self.db_loader.query_data(query)
                    count = result.iloc[0]['count'] if not result.empty else 0
                    pipeline_data_volume.labels(table=table).set(count)
                except:
                    pipeline_data_volume.labels(table=table).set(0)
            
            # Data freshness
            try:
                query = """
                    SELECT MAX(date) as latest_date 
                    FROM stock_prices
                """
                result = self.db_loader.query_data(query)
                
                if not result.empty and result.iloc[0]['latest_date'] is not None:
                    latest_date = pd.to_datetime(result.iloc[0]['latest_date'])
                    hours_old = (datetime.now() - latest_date).total_seconds() / 3600
                    pipeline_data_freshness.set(hours_old)
                else:
                    pipeline_data_freshness.set(float('inf'))
            except:
                pipeline_data_freshness.set(float('inf'))
            
        except Exception as e:
            logger.error(f"Error collecting pipeline metrics: {str(e)}")
    
    def record_request(self, method: str, endpoint: str, duration: float):
        """Record a pipeline request."""
        pipeline_requests_total.labels(method=method, endpoint=endpoint).inc()
        pipeline_request_duration.observe(duration)


# Global metrics exporter instance
metrics_exporter = MetricsExporter()


if __name__ == "__main__":
    print("Starting Quantitative Finance Pipeline Metrics Exporter...")
    print("Metrics will be available at: http://localhost:8000/metrics")
    print("Press Ctrl+C to stop the server")
    
    try:
        metrics_exporter.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down metrics exporter...")
        metrics_exporter.stop()
