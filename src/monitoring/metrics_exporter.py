"""
Custom Metrics Exporter for Quantitative Finance Pipeline
Exposes application-specific metrics to Prometheus
"""

import time
import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
import psutil
import redis
import os
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class FinancialMetricsExporter:
    """Exports custom metrics for the quantitative finance pipeline."""
    
    def __init__(self, port: int = 8000):
        """Initialize the metrics exporter."""
        self.port = port
        
        # Database connection
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/quant_finance')
        self.engine = create_engine(self.db_url)
        
        # Redis connection
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True
            )
            self.redis_available = True
        except Exception as e:
            logger.warning(f"Redis not available for metrics: {e}")
            self.redis_available = False
            self.redis_client = None
        
        # Define Prometheus metrics
        self._define_metrics()
        
        # Start HTTP server for metrics
        start_http_server(self.port)
        logger.info(f"Metrics exporter started on port {self.port}")
    
    def _define_metrics(self):
        """Define all Prometheus metrics."""
        
        # Application metrics
        self.app_info = Info('quant_finance_app_info', 'Application information')
        self.app_info.info({
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'start_time': datetime.now().isoformat()
        })
        
        # Portfolio metrics
        self.portfolio_count = Gauge('quant_finance_portfolios_total', 'Total number of portfolios')
        self.portfolio_analytics_calculations = Counter(
            'quant_finance_portfolio_analytics_calculations_total',
            'Total portfolio analytics calculations',
            ['portfolio_name', 'calculation_type']
        )
        self.portfolio_analytics_duration = Histogram(
            'quant_finance_portfolio_analytics_duration_seconds',
            'Time spent calculating portfolio analytics',
            ['portfolio_name', 'calculation_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        # Stock data metrics
        self.stock_data_fetches = Counter(
            'quant_finance_stock_data_fetches_total',
            'Total stock data fetches',
            ['symbol', 'source', 'status']
        )
        self.stock_data_fetch_duration = Histogram(
            'quant_finance_stock_data_fetch_duration_seconds',
            'Time spent fetching stock data',
            ['symbol', 'source'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
        )
        self.stock_symbols_count = Gauge('quant_finance_stock_symbols_total', 'Total number of stock symbols')
        
        # Cache metrics
        self.cache_hits = Counter(
            'quant_finance_cache_hits_total',
            'Total cache hits',
            ['cache_type', 'key_pattern']
        )
        self.cache_misses = Counter(
            'quant_finance_cache_misses_total',
            'Total cache misses',
            ['cache_type', 'key_pattern']
        )
        self.cache_size = Gauge('quant_finance_cache_size_bytes', 'Cache size in bytes', ['cache_type'])
        
        # Database metrics
        self.db_connections_active = Gauge('quant_finance_db_connections_active', 'Active database connections')
        self.db_query_duration = Histogram(
            'quant_finance_db_query_duration_seconds',
            'Database query duration',
            ['query_type'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        # System metrics
        self.system_cpu_usage = Gauge('quant_finance_system_cpu_usage_percent', 'System CPU usage percentage')
        self.system_memory_usage = Gauge('quant_finance_system_memory_usage_bytes', 'System memory usage in bytes')
        self.system_disk_usage = Gauge('quant_finance_system_disk_usage_bytes', 'System disk usage in bytes')
        
        # Error metrics
        self.errors_total = Counter(
            'quant_finance_errors_total',
            'Total errors',
            ['error_type', 'component']
        )
        
        # Performance metrics
        self.dashboard_requests = Counter(
            'quant_finance_dashboard_requests_total',
            'Total dashboard requests',
            ['endpoint', 'method', 'status']
        )
        self.dashboard_request_duration = Histogram(
            'quant_finance_dashboard_request_duration_seconds',
            'Dashboard request duration',
            ['endpoint', 'method'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
    
    def update_portfolio_metrics(self):
        """Update portfolio-related metrics."""
        try:
            # Count total portfolios
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM portfolios"))
                portfolio_count = result.scalar()
                self.portfolio_count.set(portfolio_count)
                
                # Count stock symbols
                result = conn.execute(text("SELECT COUNT(DISTINCT symbol) FROM stock_prices"))
                symbols_count = result.scalar()
                self.stock_symbols_count.set(symbols_count)
                
        except Exception as e:
            logger.error(f"Error updating portfolio metrics: {e}")
            self.errors_total.labels(error_type='database_error', component='metrics_exporter').inc()
    
    def update_cache_metrics(self):
        """Update cache-related metrics."""
        if not self.redis_available:
            return
        
        try:
            # Get Redis info
            info = self.redis_client.info()
            
            # Cache size
            self.cache_size.labels(cache_type='redis').set(info.get('used_memory', 0))
            
            # Cache hit/miss ratio
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            
            if hits > 0 or misses > 0:
                # Update cache metrics (these are cumulative)
                self.cache_hits.labels(cache_type='redis', key_pattern='portfolio_analytics').inc(hits)
                self.cache_misses.labels(cache_type='redis', key_pattern='portfolio_analytics').inc(misses)
                
        except Exception as e:
            logger.error(f"Error updating cache metrics: {e}")
            self.errors_total.labels(error_type='redis_error', component='metrics_exporter').inc()
    
    def update_system_metrics(self):
        """Update system-related metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_disk_usage.set(disk.used)
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
            self.errors_total.labels(error_type='system_error', component='metrics_exporter').inc()
    
    def update_database_metrics(self):
        """Update database-related metrics."""
        try:
            with self.engine.connect() as conn:
                # Get active connections
                result = conn.execute(text("SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'quant_finance'"))
                active_connections = result.scalar()
                self.db_connections_active.set(active_connections)
                
        except Exception as e:
            logger.error(f"Error updating database metrics: {e}")
            self.errors_total.labels(error_type='database_error', component='metrics_exporter').inc()
    
    def record_portfolio_calculation(self, portfolio_name: str, calculation_type: str, duration: float):
        """Record portfolio calculation metrics."""
        self.portfolio_analytics_calculations.labels(
            portfolio_name=portfolio_name,
            calculation_type=calculation_type
        ).inc()
        
        self.portfolio_analytics_duration.labels(
            portfolio_name=portfolio_name,
            calculation_type=calculation_type
        ).observe(duration)
    
    def record_stock_data_fetch(self, symbol: str, source: str, status: str, duration: float):
        """Record stock data fetch metrics."""
        self.stock_data_fetches.labels(
            symbol=symbol,
            source=source,
            status=status
        ).inc()
        
        self.stock_data_fetch_duration.labels(
            symbol=symbol,
            source=source
        ).observe(duration)
    
    def record_cache_operation(self, cache_type: str, key_pattern: str, hit: bool):
        """Record cache operation metrics."""
        if hit:
            self.cache_hits.labels(cache_type=cache_type, key_pattern=key_pattern).inc()
        else:
            self.cache_misses.labels(cache_type=cache_type, key_pattern=key_pattern).inc()
    
    def record_dashboard_request(self, endpoint: str, method: str, status: str, duration: float):
        """Record dashboard request metrics."""
        self.dashboard_requests.labels(
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()
        
        self.dashboard_request_duration.labels(
            endpoint=endpoint,
            method=method
        ).observe(duration)
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics."""
        self.errors_total.labels(error_type=error_type, component=component).inc()
    
    def update_all_metrics(self):
        """Update all metrics."""
        self.update_portfolio_metrics()
        self.update_cache_metrics()
        self.update_system_metrics()
        self.update_database_metrics()
    
    def run_metrics_collection(self, interval: int = 30):
        """Run continuous metrics collection."""
        logger.info(f"Starting metrics collection with {interval}s interval")
        
        while True:
            try:
                self.update_all_metrics()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Metrics collection stopped")
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                time.sleep(interval)


# Global metrics exporter instance
_metrics_exporter: Optional[FinancialMetricsExporter] = None

def get_metrics_exporter() -> FinancialMetricsExporter:
    """Get the global metrics exporter instance."""
    global _metrics_exporter
    if _metrics_exporter is None:
        _metrics_exporter = FinancialMetricsExporter()
    return _metrics_exporter

def start_metrics_exporter(port: int = 8000, collection_interval: int = 30):
    """Start the metrics exporter."""
    global _metrics_exporter
    _metrics_exporter = FinancialMetricsExporter(port)
    
    # Start metrics collection in a separate thread
    import threading
    collection_thread = threading.Thread(
        target=_metrics_exporter.run_metrics_collection,
        args=(collection_interval,),
        daemon=True
    )
    collection_thread.start()
    
    return _metrics_exporter

if __name__ == "__main__":
    # Start metrics exporter when run directly
    logging.basicConfig(level=logging.INFO)
    exporter = start_metrics_exporter()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Metrics exporter stopped")