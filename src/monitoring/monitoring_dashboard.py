"""
Real-time monitoring dashboard for the quantitative finance pipeline.
"""
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import threading
import time

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from monitoring.system_monitor import SystemMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize system monitor
monitor = SystemMonitor()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Quantitative Finance Pipeline - System Monitor"

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🔍 System Monitor", className="text-center mb-4"),
            html.P("Real-time monitoring of the quantitative finance pipeline", 
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    # System Status Overview
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📊 System Status", className="card-title"),
                    html.Div(id="system-status")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Real-time Metrics
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📈 Real-time Metrics", className="card-title"),
                    dcc.Graph(id="system-metrics-chart")
                ])
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("⚠️ Recent Alerts", className="card-title"),
                    html.Div(id="recent-alerts")
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    # Database Health
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🗄️ Database Health", className="card-title"),
                    dcc.Graph(id="database-health-chart")
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📊 Data Volume", className="card-title"),
                    dcc.Graph(id="data-volume-chart")
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    )
], fluid=True)


@app.callback(
    Output("system-status", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_system_status(n):
    """Update system status overview."""
    try:
        status = monitor.get_system_status()
        
        if status["status"] == "no_data":
            return html.P("No monitoring data available", className="text-muted")
        
        # Status badge
        status_color = {
            "healthy": "success",
            "stale_data": "warning", 
            "db_slow": "warning",
            "resource_high": "danger",
            "error": "danger"
        }.get(status["status"], "secondary")
        
        status_badge = dbc.Badge(
            status["status"].upper().replace("_", " "),
            color=status_color,
            className="mb-3"
        )
        
        # System health cards
        system_health = status["system_health"]
        health_cards = []
        
        # CPU
        cpu_color = "success" if system_health["cpu_usage"] < 70 else "warning" if system_health["cpu_usage"] < 90 else "danger"
        health_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{system_health['cpu_usage']:.1f}%", className=f"text-{cpu_color}"),
                    html.P("CPU Usage", className="mb-0")
                ])
            ], className="text-center")
        )
        
        # Memory
        memory_color = "success" if system_health["memory_usage"] < 70 else "warning" if system_health["memory_usage"] < 90 else "danger"
        health_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{system_health['memory_usage']:.1f}%", className=f"text-{memory_color}"),
                    html.P("Memory Usage", className="mb-0")
                ])
            ], className="text-center")
        )
        
        # Disk
        disk_color = "success" if system_health["disk_usage"] < 70 else "warning" if system_health["disk_usage"] < 90 else "danger"
        health_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{system_health['disk_usage']:.1f}%", className=f"text-{disk_color}"),
                    html.P("Disk Usage", className="mb-0")
                ])
            ], className="text-center")
        )
        
        # Database connection time
        db_health = status["database_health"]
        db_color = "success" if db_health["connection_time"] < 1 else "warning" if db_health["connection_time"] < 3 else "danger"
        health_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{db_health['connection_time']:.2f}s", className=f"text-{db_color}"),
                    html.P("DB Response", className="mb-0")
                ])
            ], className="text-center")
        )
        
        return html.Div([
            status_badge,
            dbc.Row([dbc.Col(card, width=3) for card in health_cards])
        ])
        
    except Exception as e:
        logger.error(f"Error updating system status: {str(e)}")
        return html.P(f"Error loading status: {str(e)}", className="text-danger")


@app.callback(
    Output("system-metrics-chart", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_system_metrics_chart(n):
    """Update system metrics chart."""
    try:
        # Get metrics history for last hour
        metrics_history = monitor.get_metrics_history(hours=1)
        
        if not metrics_history:
            return go.Figure().add_annotation(
                text="No metrics data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Convert to DataFrame
        df = pd.DataFrame(metrics_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('System Resources', 'Database Performance'),
            vertical_spacing=0.1
        )
        
        # System resources
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['cpu_usage'],
                mode='lines',
                name='CPU Usage (%)',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['memory_usage'],
                mode='lines',
                name='Memory Usage (%)',
                line=dict(color='red', width=2)
            ),
            row=1, col=1
        )
        
        # Database performance
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['db_connection_time'],
                mode='lines',
                name='DB Response Time (s)',
                line=dict(color='green', width=2)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['data_freshness_hours'],
                mode='lines',
                name='Data Age (hours)',
                line=dict(color='orange', width=2)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Usage (%)", row=1, col=1)
        fig.update_yaxes(title_text="Time/Age", row=2, col=1)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating system metrics chart: {str(e)}")
        return go.Figure().add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )


@app.callback(
    Output("recent-alerts", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_recent_alerts(n):
    """Update recent alerts display."""
    try:
        alerts = monitor.get_recent_alerts(limit=10)
        
        if not alerts:
            return html.P("No recent alerts", className="text-muted")
        
        alert_items = []
        for alert in reversed(alerts):  # Show newest first
            severity_color = {
                "info": "primary",
                "warning": "warning",
                "error": "danger",
                "critical": "danger"
            }.get(alert["severity"], "secondary")
            
            time_str = alert["timestamp"].strftime("%H:%M:%S")
            
            alert_items.append(
                dbc.Alert([
                    html.Strong(f"[{time_str}] "),
                    alert["message"]
                ], color=severity_color, className="mb-2")
            )
        
        return html.Div(alert_items)
        
    except Exception as e:
        logger.error(f"Error updating recent alerts: {str(e)}")
        return html.P(f"Error loading alerts: {str(e)}", className="text-danger")


@app.callback(
    Output("database-health-chart", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_database_health_chart(n):
    """Update database health chart."""
    try:
        metrics_history = monitor.get_metrics_history(hours=1)
        
        if not metrics_history:
            return go.Figure().add_annotation(
                text="No database metrics available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        df = pd.DataFrame(metrics_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        
        # Connection time
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['db_connection_time'],
            mode='lines+markers',
            name='Connection Time (s)',
            line=dict(color='blue', width=2)
        ))
        
        # Active connections
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['active_connections'],
            mode='lines+markers',
            name='Active Connections',
            line=dict(color='green', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Database Performance",
            xaxis_title="Time",
            yaxis=dict(title="Connection Time (s)", side="left"),
            yaxis2=dict(title="Active Connections", side="right", overlaying="y"),
            hovermode='x unified',
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating database health chart: {str(e)}")
        return go.Figure().add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )


@app.callback(
    Output("data-volume-chart", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_data_volume_chart(n):
    """Update data volume chart."""
    try:
        metrics_history = monitor.get_metrics_history(hours=1)
        
        if not metrics_history:
            return go.Figure().add_annotation(
                text="No data volume metrics available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Get latest data volume
        latest_metrics = metrics_history[-1]
        data_volume = latest_metrics.get('data_volume', {})
        
        if not data_volume:
            return go.Figure().add_annotation(
                text="No data volume information available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Create bar chart
        tables = list(data_volume.keys())
        counts = list(data_volume.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=tables,
                y=counts,
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            )
        ])
        
        fig.update_layout(
            title="Data Volume by Table",
            xaxis_title="Table",
            yaxis_title="Record Count",
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating data volume chart: {str(e)}")
        return go.Figure().add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )


def start_monitoring():
    """Start the system monitoring."""
    monitor.start_monitoring(interval=10)  # Monitor every 10 seconds


if __name__ == "__main__":
    print("Starting Quantitative Finance Pipeline System Monitor...")
    print("Monitor Dashboard will be available at: http://localhost:8051")
    print("Press Ctrl+C to stop the server")
    
    # Start monitoring in background
    start_monitoring()
    
    try:
        app.run_server(debug=True, host='0.0.0.0', port=8051)
    except KeyboardInterrupt:
        print("\nShutting down monitor...")
        monitor.stop_monitoring()
