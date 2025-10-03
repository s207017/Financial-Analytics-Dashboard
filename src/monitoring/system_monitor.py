"""
System monitoring tool for the quantitative finance pipeline.
"""
import sys
from pathlib import Path
import logging
import time
import psutil
import threading
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from data_access.data_service import DataService
from etl.loaders.database_loader import DatabaseLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """Real-time system monitoring for the quantitative finance pipeline."""
    
    def __init__(self, db_url="postgresql://postgres:password@localhost:5432/quant_finance"):
        """Initialize the system monitor."""
        self.db_url = db_url
        self.data_service = DataService(db_url)
        self.db_loader = DatabaseLoader(db_url)
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'db_connection_time': 5.0,
            'data_freshness_hours': 24.0,
            'error_rate': 5.0
        }
        self.alerts = []
        
    def start_monitoring(self, interval=30):
        """
        Start real-time monitoring.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"System monitoring started with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self, interval):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 1000 records
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                # Check for alerts
                self._check_alerts(metrics)
                
                logger.info(f"System metrics collected: CPU={metrics['cpu_usage']:.1f}%, "
                          f"Memory={metrics['memory_usage']:.1f}%, "
                          f"DB_Conn={metrics['db_connection_time']:.2f}s")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                self._add_alert("monitoring_error", f"Monitoring error: {str(e)}", "error")
            
            time.sleep(interval)
    
    def collect_system_metrics(self) -> Dict:
        """Collect current system metrics."""
        timestamp = datetime.now()
        
        # System metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database metrics
        db_connection_time = self._test_db_connection()
        data_freshness = self._check_data_freshness()
        
        # Pipeline metrics
        pipeline_status = self._check_pipeline_status()
        
        return {
            'timestamp': timestamp,
            'cpu_usage': cpu_usage,
            'memory_usage': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_usage': disk.percent,
            'disk_free_gb': disk.free / (1024**3),
            'db_connection_time': db_connection_time,
            'data_freshness_hours': data_freshness,
            'pipeline_status': pipeline_status,
            'active_connections': self._get_active_connections(),
            'data_volume': self._get_data_volume()
        }
    
    def _test_db_connection(self) -> float:
        """Test database connection and return response time."""
        try:
            start_time = time.time()
            self.db_loader.query_data("SELECT 1")
            return time.time() - start_time
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return float('inf')
    
    def _check_data_freshness(self) -> float:
        """Check how fresh the data is in hours."""
        try:
            query = """
                SELECT MAX(date) as latest_date 
                FROM stock_prices
            """
            result = self.db_loader.query_data(query)
            
            if result.empty or result.iloc[0]['latest_date'] is None:
                return float('inf')
            
            latest_date = pd.to_datetime(result.iloc[0]['latest_date'])
            hours_old = (datetime.now() - latest_date).total_seconds() / 3600
            return hours_old
            
        except Exception as e:
            logger.error(f"Error checking data freshness: {str(e)}")
            return float('inf')
    
    def _check_pipeline_status(self) -> str:
        """Check overall pipeline status."""
        try:
            # Check if we have recent data
            data_freshness = self._check_data_freshness()
            if data_freshness > 48:  # More than 2 days old
                return "stale_data"
            
            # Check database connectivity
            db_time = self._test_db_connection()
            if db_time > 5:  # More than 5 seconds
                return "db_slow"
            
            # Check system resources
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            if cpu_usage > 90 or memory_usage > 95:
                return "resource_high"
            
            return "healthy"
            
        except Exception as e:
            logger.error(f"Error checking pipeline status: {str(e)}")
            return "error"
    
    def _get_active_connections(self) -> int:
        """Get number of active database connections."""
        try:
            query = """
                SELECT count(*) as connections 
                FROM pg_stat_activity 
                WHERE state = 'active'
            """
            result = self.db_loader.query_data(query)
            return result.iloc[0]['connections'] if not result.empty else 0
        except Exception as e:
            logger.error(f"Error getting active connections: {str(e)}")
            return 0
    
    def _get_data_volume(self) -> Dict:
        """Get data volume statistics."""
        try:
            tables = ['stock_prices', 'portfolio_data', 'risk_metrics', 'technical_indicators']
            volumes = {}
            
            for table in tables:
                try:
                    query = f"SELECT COUNT(*) as count FROM {table}"
                    result = self.db_loader.query_data(query)
                    volumes[table] = result.iloc[0]['count'] if not result.empty else 0
                except:
                    volumes[table] = 0
            
            return volumes
            
        except Exception as e:
            logger.error(f"Error getting data volume: {str(e)}")
            return {}
    
    def _check_alerts(self, metrics: Dict):
        """Check metrics against alert thresholds."""
        timestamp = metrics['timestamp']
        
        # CPU usage alert
        if metrics['cpu_usage'] > self.alert_thresholds['cpu_usage']:
            self._add_alert("high_cpu", 
                          f"High CPU usage: {metrics['cpu_usage']:.1f}%", 
                          "warning")
        
        # Memory usage alert
        if metrics['memory_usage'] > self.alert_thresholds['memory_usage']:
            self._add_alert("high_memory", 
                          f"High memory usage: {metrics['memory_usage']:.1f}%", 
                          "warning")
        
        # Disk usage alert
        if metrics['disk_usage'] > self.alert_thresholds['disk_usage']:
            self._add_alert("high_disk", 
                          f"High disk usage: {metrics['disk_usage']:.1f}%", 
                          "critical")
        
        # Database connection time alert
        if metrics['db_connection_time'] > self.alert_thresholds['db_connection_time']:
            self._add_alert("slow_db", 
                          f"Slow database connection: {metrics['db_connection_time']:.2f}s", 
                          "warning")
        
        # Data freshness alert
        if metrics['data_freshness_hours'] > self.alert_thresholds['data_freshness_hours']:
            self._add_alert("stale_data", 
                          f"Stale data: {metrics['data_freshness_hours']:.1f} hours old", 
                          "warning")
        
        # Pipeline status alert
        if metrics['pipeline_status'] != "healthy":
            self._add_alert("pipeline_issue", 
                          f"Pipeline status: {metrics['pipeline_status']}", 
                          "error")
    
    def _add_alert(self, alert_type: str, message: str, severity: str):
        """Add an alert to the alerts list."""
        alert = {
            'timestamp': datetime.now(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        logger.warning(f"ALERT [{severity.upper()}]: {message}")
    
    def get_system_status(self) -> Dict:
        """Get current system status summary."""
        if not self.metrics_history:
            return {"status": "no_data", "message": "No monitoring data available"}
        
        latest_metrics = self.metrics_history[-1]
        
        return {
            "status": latest_metrics['pipeline_status'],
            "timestamp": latest_metrics['timestamp'],
            "system_health": {
                "cpu_usage": latest_metrics['cpu_usage'],
                "memory_usage": latest_metrics['memory_usage'],
                "disk_usage": latest_metrics['disk_usage']
            },
            "database_health": {
                "connection_time": latest_metrics['db_connection_time'],
                "data_freshness_hours": latest_metrics['data_freshness_hours'],
                "active_connections": latest_metrics['active_connections']
            },
            "data_volume": latest_metrics['data_volume'],
            "recent_alerts": self.get_recent_alerts(limit=5)
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts."""
        return self.alerts[-limit:] if self.alerts else []
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict]:
        """Get metrics history for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics_history if m['timestamp'] > cutoff_time]
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file."""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'metrics_history': [
                    {
                        **metrics,
                        'timestamp': metrics['timestamp'].isoformat()
                    } for metrics in self.metrics_history
                ],
                'alerts': [
                    {
                        **alert,
                        'timestamp': alert['timestamp'].isoformat()
                    } for alert in self.alerts
                ],
                'alert_thresholds': self.alert_thresholds
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {str(e)}")
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """Set alert threshold for a metric."""
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = threshold
            logger.info(f"Alert threshold for {metric} set to {threshold}")
        else:
            logger.warning(f"Unknown metric: {metric}")


# Global monitor instance
system_monitor = SystemMonitor()
