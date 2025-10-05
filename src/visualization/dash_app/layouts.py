"""
Layout components for the dashboard tabs.
"""
from typing import List, Dict, Any
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go

from .config import (
    TABS, RISK_METRICS, DEFAULT_RISK_METRIC, SUPPORTED_STRATEGIES,
    DEFAULT_PORTFOLIO_VALUE, DEFAULT_STRATEGY, CHART_HEIGHT
)


def create_portfolio_overview() -> dbc.Container:
    """Create portfolio overview tab content."""
    return dbc.Container([
        # Key Metrics Row
        dbc.Row([
            dbc.Col([
                html.H3("Key Metrics"),
                html.Div(id="key-metrics")
            ], width=12)
        ], className="mb-4"),
        
        # Charts Row
        dbc.Row([
            dbc.Col([
                html.H3("Portfolio Performance"),
                dcc.Graph(id="portfolio-performance-chart")
            ], width=8),
            dbc.Col([
                html.H3("Asset Allocation"),
                dcc.Graph(id="asset-allocation-chart")
            ], width=4)
        ], className="mb-4")
    ], fluid=True)


def create_risk_analysis() -> dbc.Container:
    """Create risk analysis tab content."""
    return dbc.Container([
        # Controls Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Risk Analysis Controls", className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Portfolio Selection:"),
                                dcc.Dropdown(
                                    id="risk-portfolio-selector",
                                    multi=True,
                                    placeholder="Select portfolios to analyze risk..."
                                )
                            ], width=12)
                        ])
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Risk Summary Row
        dbc.Row([
            dbc.Col([
                html.H3("Risk Summary"),
                html.Div(id="risk-summary")
            ], width=12)
        ], className="mb-4"),
        
        # Charts Row 1
        dbc.Row([
            dbc.Col([
                html.H3("Risk Metrics Over Time"),
                dcc.Loading(
                    id="loading-risk-metrics",
                    type="default",
                    children=html.Div([
                        html.Div("Loading risk metrics...", id="risk-metrics-loading-text", 
                                style={"display": "none"}),
                        dcc.Graph(id="risk-metrics-chart")
                    ])
                )
            ], width=9),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Select Metric"),
                    dbc.CardBody([
                        dcc.RadioItems(
                            id="risk-metric-selector",
                            options=[
                                {"label": label, "value": value} 
                                for value, label in RISK_METRICS.items()
                            ],
                            value=DEFAULT_RISK_METRIC,
                            className="mt-2"
                        )
                    ])
                ])
            ], width=3)
        ], className="mb-4"),
        
        # Charts Row 2
        dbc.Row([
            dbc.Col([
                html.H3("Value at Risk (VaR)"),
                dcc.Graph(id="var-chart")
            ], width=6),
            dbc.Col([
                html.H3("Drawdown Analysis"),
                dcc.Graph(id="drawdown-chart")
            ], width=6)
        ], className="mb-4")
    ], fluid=True)


def create_performance_metrics() -> dbc.Container:
    """Create performance metrics tab content."""
    return dbc.Container([
        # Controls Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Performance Analysis Controls", className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Portfolio Selection:"),
                                dcc.Dropdown(
                                    id="performance-portfolio-selector",
                                    multi=True,
                                    placeholder="Select portfolios to analyze performance..."
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Date Range:"),
                                dcc.DatePickerRange(
                                    id="performance-date-range",
                                    start_date="2023-01-01",
                                    end_date="2024-12-31",
                                    display_format="YYYY-MM-DD"
                                )
                            ], width=6)
                        ])
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Performance Summary Row
        dbc.Row([
            dbc.Col([
                html.H3("Performance Summary"),
                html.Div(id="performance-summary")
            ], width=12)
        ], className="mb-4"),
        
        # Charts Row 1
        dbc.Row([
            dbc.Col([
                html.H3("Performance Comparison"),
                dcc.Loading(
                    id="loading-performance-comparison",
                    type="default",
                    children=html.Div([
                        html.Div("Loading performance data...", id="performance-loading-text", 
                                style={"display": "none"}),
                        dcc.Graph(id="performance-comparison-chart")
                    ])
                )
            ], width=12)
        ], className="mb-4"),
        
        # Charts Row 2
        dbc.Row([
            dbc.Col([
                html.H3("Rolling Sharpe Ratio"),
                dcc.Dropdown(
                    id="rolling-sharpe-portfolio-selector",
                    multi=False,
                    placeholder="Select portfolio for rolling Sharpe..."
                ),
                dcc.Loading(
                    id="loading-rolling-sharpe",
                    type="default",
                    children=html.Div([
                        html.Div("Loading rolling Sharpe...", id="rolling-sharpe-loading-text", 
                                style={"display": "none"}),
                        dcc.Graph(id="rolling-sharpe-chart")
                    ])
                )
            ], width=6),
            dbc.Col([
                html.H3("Rolling Volatility"),
                dcc.Dropdown(
                    id="rolling-volatility-portfolio-selector",
                    multi=False,
                    placeholder="Select portfolio for rolling volatility..."
                ),
                dcc.Loading(
                    id="loading-rolling-volatility",
                    type="default",
                    children=html.Div([
                        html.Div("Loading rolling volatility...", id="rolling-volatility-loading-text", 
                                style={"display": "none"}),
                        dcc.Graph(id="rolling-volatility-chart")
                    ])
                )
            ], width=6)
        ], className="mb-4"),
        
        # Performance Statistics Row
        dbc.Row([
            dbc.Col([
                html.H3("Performance Statistics"),
                html.Div(id="performance-statistics")
            ], width=12)
        ], className="mb-4")
    ], fluid=True)


def create_portfolio_management() -> dbc.Container:
    """Create portfolio management tab content."""
    return dbc.Container([
        # Portfolio List Row
        dbc.Row([
            dbc.Col([
                html.H3("Existing Portfolios"),
                dcc.Loading(
                    id="loading-portfolios",
                    type="default",
                    children=html.Div([
                        html.Div("Loading portfolios...", id="portfolios-loading-text", 
                                style={"display": "none"}),
                        html.Div(id="portfolios-list")
                    ])
                )
            ], width=12)
        ], className="mb-4"),
        
        # Portfolio Creation Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Create New Portfolio"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Portfolio Name:"),
                                dbc.Input(
                                    id="portfolio-name",
                                    placeholder="Enter portfolio name...",
                                    type="text"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Portfolio Value:"),
                                dbc.Input(
                                    id="portfolio-value",
                                    placeholder="100000",
                                    type="number",
                                    value=DEFAULT_PORTFOLIO_VALUE
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Label("Strategy:"),
                                dcc.Dropdown(
                                    id="strategy-selector",
                                    options=[{"label": s, "value": s} for s in SUPPORTED_STRATEGIES],
                                    value=DEFAULT_STRATEGY
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Description:"),
                                dbc.Input(
                                    id="portfolio-description",
                                    placeholder="Portfolio description...",
                                    type="text"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Label("Asset Selection:"),
                                dcc.Dropdown(
                                    id="asset-selector",
                                    multi=True,
                                    placeholder="Select assets...",
                                    searchable=True
                                )
                            ], width=8),
                            dbc.Col([
                                html.Label("Custom Symbol:"),
                                dbc.Input(
                                    id="custom-symbol-input",
                                    placeholder="e.g., AAPL",
                                    type="text"
                                ),
                                dbc.Button(
                                    "Add Symbol",
                                    id="add-symbol-btn",
                                    color="primary",
                                    size="sm",
                                    className="mt-2"
                                )
                            ], width=4)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Create Portfolio",
                                    id="create-portfolio-btn",
                                    color="success",
                                    size="lg",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "Auto Allocate",
                                    id="auto-allocate-btn",
                                    color="info",
                                    size="lg"
                                )
                            ], width=12)
                        ]),
                        
                        html.Div(id="portfolio-actions-feedback", className="mt-3")
                    ])
                ])
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Portfolio Summary"),
                    dbc.CardBody([
                        html.Div(id="portfolio-summary")
                    ])
                ]),
                dbc.Card([
                    dbc.CardHeader("Portfolio Weights"),
                    dbc.CardBody([
                        html.Div(id="portfolio-weights")
                    ])
                ])
            ], width=4)
        ], className="mb-4"),
        
        # Portfolio Management Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Manage Existing Portfolio"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Select Portfolio:"),
                                dcc.Dropdown(
                                    id="manage-portfolio-selector",
                                    placeholder="Select portfolio to manage..."
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Action:"),
                                dcc.Dropdown(
                                    id="portfolio-action",
                                    options=[
                                        {"label": "Update Portfolio", "value": "update"},
                                        {"label": "Delete Portfolio", "value": "delete"}
                                    ],
                                    placeholder="Select action..."
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Execute Action",
                                    id="execute-action-btn",
                                    color="warning",
                                    size="lg"
                                )
                            ], width=12)
                        ]),
                        
                        html.Div(id="portfolio-management-feedback", className="mt-3")
                    ])
                ])
            ], width=12)
        ], className="mb-4")
    ], fluid=True)


def create_main_layout() -> dbc.Container:
    """Create the main application layout."""
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("Quantitative Finance Pipeline", className="text-center mb-4"),
                html.P("Advanced Portfolio Management and Risk Analysis Dashboard", 
                      className="text-center text-muted mb-4")
            ], width=12)
        ], className="mb-4"),
        
        # Navigation tabs
        dbc.Row([
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(label=tab_config["label"], tab_id=tab_config["id"])
                    for tab_config in TABS.values()
                ], id="tabs", active_tab="portfolio-tab")
            ], width=12)
        ], className="mb-4"),
        
        # Tab content
        html.Div(id="tab-content"),
        
        # Hidden div to store portfolio data
        html.Div(id="portfolio-storage", style={"display": "none"}),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P("Quantitative Finance Pipeline Dashboard - Built with Dash and Plotly", 
                      className="text-center text-muted")
            ], width=12)
        ], className="mt-4")
    ], fluid=True)
