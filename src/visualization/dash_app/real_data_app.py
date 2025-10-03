"""
Real data dashboard for the quantitative finance pipeline.
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
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from data_access.data_service import DataService
from data_access.stock_filtering_service import StockFilteringService
from data_access.portfolio_management_service import PortfolioManagementService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize data services
data_service = DataService()
stock_filtering_service = StockFilteringService()
portfolio_management_service = PortfolioManagementService()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Quantitative Finance Pipeline - Real Data Dashboard"

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("📊 Quantitative Finance Pipeline", className="text-center mb-4"),
            html.P("Real-time financial data analysis and portfolio optimization", 
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📈 Portfolio Overview", className="card-title"),
                    html.Div(id="portfolio-overview")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="📊 Market Data", tab_id="market-tab"),
                dbc.Tab(label="📈 Portfolio Performance", tab_id="portfolio-tab"),
                dbc.Tab(label="⚠️ Risk Analysis", tab_id="risk-tab"),
                dbc.Tab(label="🔗 Correlation Analysis", tab_id="correlation-tab"),
                dbc.Tab(label="🔍 Stock Filtering", tab_id="stock-filtering-tab"),
                dbc.Tab(label="💼 Portfolio Manager", tab_id="portfolio-manager-tab"),
            ], id="tabs", active_tab="market-tab")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id="tab-content")
        ])
    ], className="mt-4")
], fluid=True)


@app.callback(
    Output("portfolio-overview", "children"),
    [Input("tabs", "active_tab")]
)
def update_portfolio_overview(active_tab):
    """Update portfolio overview with real data."""
    try:
        # Get portfolio summary
        summary = data_service.get_portfolio_summary()
        
        if not summary:
            return html.P("No portfolio data available", className="text-muted")
        
        # Create overview cards
        cards = []
        
        # Total symbols
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{summary['total_symbols']}", className="text-primary"),
                    html.P("Symbols", className="mb-0")
                ])
            ], className="text-center")
        )
        
        # Total return
        total_return = summary.get('total_return', 0) * 100
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{total_return:.2f}%", 
                           className="text-success" if total_return >= 0 else "text-danger"),
                    html.P("Total Return", className="mb-0")
                ])
            ], className="text-center")
        )
        
        # Volatility
        volatility = summary.get('volatility', 0) * 100
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{volatility:.2f}%", className="text-warning"),
                    html.P("Volatility", className="mb-0")
                ])
            ], className="text-center")
        )
        
        # Risk metrics
        risk_metrics = summary.get('risk_metrics', {})
        sharpe_ratio = risk_metrics.get('sharpe_ratio', 0)
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{sharpe_ratio:.3f}", 
                           className="text-success" if sharpe_ratio >= 0 else "text-danger"),
                    html.P("Sharpe Ratio", className="mb-0")
                ])
            ], className="text-center")
        )
        
        return dbc.Row([dbc.Col(card, width=3) for card in cards])
        
    except Exception as e:
        logger.error(f"Error updating portfolio overview: {str(e)}")
        return html.P(f"Error loading data: {str(e)}", className="text-danger")


@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)
def update_tab_content(active_tab):
    """Update tab content based on active tab."""
    if active_tab == "market-tab":
        return create_market_data_tab()
    elif active_tab == "portfolio-tab":
        return create_portfolio_tab()
    elif active_tab == "risk-tab":
        return create_risk_tab()
    elif active_tab == "correlation-tab":
        return create_correlation_tab()
    elif active_tab == "stock-filtering-tab":
        return create_stock_filtering_tab()
    elif active_tab == "portfolio-manager-tab":
        return create_portfolio_manager_tab()
    else:
        return html.P("Select a tab to view content")


def create_market_data_tab():
    """Create market data tab content."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Stock Prices", className="card-title"),
                    dcc.Graph(id="stock-prices-chart")
                ])
            ])
        ], width=12)
    ])


def create_portfolio_tab():
    """Create portfolio performance tab content."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Portfolio Performance", className="card-title"),
                    dcc.Graph(id="portfolio-performance-chart")
                ])
            ])
        ], width=12)
    ])


def create_risk_tab():
    """Create risk analysis tab content."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Risk Metrics Over Time", className="card-title"),
                        dcc.Graph(id="risk-metrics-chart")
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Risk Summary", className="card-title"),
                        html.Div(id="risk-summary")
                    ])
                ])
            ], width=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Value at Risk (VaR)", className="card-title"),
                        dcc.Graph(id="var-chart")
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Drawdown Analysis", className="card-title"),
                        dcc.Graph(id="drawdown-chart")
                    ])
                ])
            ], width=6)
        ])
    ])


def create_correlation_tab():
    """Create correlation analysis tab content."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Asset Correlation Matrix", className="card-title"),
                    dcc.Graph(id="correlation-matrix")
                ])
            ])
        ], width=12)
    ])


def create_stock_filtering_tab():
    """Create stock filtering tab content."""
    # Get available filter options
    available_filters = stock_filtering_service.get_available_filters()
    
    return dbc.Row([
        # Filter Controls
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Stock Filters"),
                dbc.CardBody([
                    dbc.Row([
                        # Market Cap Categories
                        dbc.Col([
                            dbc.Label("Market Cap Categories"),
                            dcc.Dropdown(
                                id="stock-market-cap-filter",
                                options=[{"label": cat, "value": cat} for cat in available_filters.get('market_cap_categories', [])],
                                multi=True,
                                placeholder="Select market cap categories"
                            )
                        ], width=6),
                        
                        # Sectors
                        dbc.Col([
                            dbc.Label("Sectors"),
                            dcc.Dropdown(
                                id="stock-sector-filter",
                                options=[{"label": sector, "value": sector} for sector in available_filters.get('sectors', [])],
                                multi=True,
                                placeholder="Select sectors"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        # Industries
                        dbc.Col([
                            dbc.Label("Industries"),
                            dcc.Dropdown(
                                id="stock-industry-filter",
                                options=[{"label": industry, "value": industry} for industry in available_filters.get('industries', [])],
                                multi=True,
                                placeholder="Select industries"
                            )
                        ], width=6),
                        
                        # Price Range
                        dbc.Col([
                            dbc.Label("Price Range"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Input(
                                        id="stock-price-min",
                                        type="number",
                                        placeholder="Min Price",
                                        min=0
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Input(
                                        id="stock-price-max",
                                        type="number",
                                        placeholder="Max Price",
                                        min=0
                                    )
                                ], width=6)
                            ])
                        ], width=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        # PE Ratio Range
                        dbc.Col([
                            dbc.Label("PE Ratio Range"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Input(
                                        id="stock-pe-min",
                                        type="number",
                                        placeholder="Min PE",
                                        min=0
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Input(
                                        id="stock-pe-max",
                                        type="number",
                                        placeholder="Max PE",
                                        min=0
                                    )
                                ], width=6)
                            ])
                        ], width=6),
                        
                        # Dividend Yield Range
                        dbc.Col([
                            dbc.Label("Dividend Yield Range (%)"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Input(
                                        id="stock-div-min",
                                        type="number",
                                        placeholder="Min Div %",
                                        min=0,
                                        step=0.1
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Input(
                                        id="stock-div-max",
                                        type="number",
                                        placeholder="Max Div %",
                                        min=0,
                                        step=0.1
                                    )
                                ], width=6)
                            ])
                        ], width=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        # Action Buttons
                        dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Apply Filters", id="stock-apply-filters", color="primary", className="me-2")
                                ], width=6),
                                dbc.Col([
                                    dbc.Button("Clear Filters", id="stock-clear-filters", color="secondary")
                                ], width=6)
                            ])
                        ], width=12)
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Summary Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="stock-total-count", className="card-title"),
                    html.P("Total Stocks", className="card-text")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="stock-filtered-count", className="card-title"),
                    html.P("Filtered Stocks", className="card-text")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="stock-avg-pe", className="card-title"),
                    html.P("Average PE Ratio", className="card-text")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="stock-avg-dividend", className="card-title"),
                    html.P("Average Dividend Yield", className="card-text")
                ])
            ])
        ], width=3)
    ], className="mb-4"),
    
    # Charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Market Cap Distribution"),
                dbc.CardBody([
                    dcc.Graph(id="stock-market-cap-chart")
                ])
            ])
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Sector Distribution"),
                dbc.CardBody([
                    dcc.Graph(id="stock-sector-chart")
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Stock Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filtered Stocks"),
                dbc.CardBody([
                    html.Div(id="stock-results-table")
                ])
            ])
        ], width=12)
    ]),
    
    # Hidden div to store filtered data
    html.Div(id="stock-filtered-data", style={"display": "none"})


def create_portfolio_manager_tab():
    """Create portfolio management tab content."""
    # Get available stocks for selection
    available_stocks = stock_filtering_service.get_all_stocks()
    stock_options = [{"label": f"{row['symbol']} - {row['name']}", "value": row['symbol']} 
                     for _, row in available_stocks.iterrows()]
    
    return [
        dbc.Row([
        # Portfolio Creation Section
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Create New Portfolio"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Portfolio Name"),
                            dbc.Input(id="portfolio-name", placeholder="Enter portfolio name", type="text"),
                            html.Div(id="portfolio-error-alert", style={"margin-top": "10px"})
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Strategy"),
                            dcc.Dropdown(
                                id="portfolio-strategy",
                                options=[
                                    {"label": "Custom", "value": "Custom"},
                                    {"label": "Equal Weight", "value": "Equal Weight"},
                                    {"label": "Market Cap Weighted", "value": "Market Cap Weighted"},
                                    {"label": "Value", "value": "Value"},
                                    {"label": "Growth", "value": "Growth"},
                                    {"label": "Dividend", "value": "Dividend"}
                                ],
                                value="Custom"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Description"),
                            dbc.Textarea(id="portfolio-description", placeholder="Enter portfolio description")
                        ], width=12)
                    ], className="mb-3"),
                    
                    # Dynamic Stock Selection
                    dbc.Row([
                        dbc.Col([
                            html.H5("Portfolio Holdings", className="mb-3"),
                            html.Div(id="stock-holdings-container", children=[
                                # First stock row
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Stock Symbol"),
                                        dcc.Dropdown(
                                            id={"type": "stock-dropdown", "index": 0},
                                            options=stock_options,
                                            placeholder="Select stock"
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Weight (%)"),
                                        dbc.Input(
                                            id={"type": "weight-input", "index": 0},
                                            type="number",
                                            placeholder="0",
                                            min=0,
                                            max=100,
                                            step=0.1
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label("Action"),
                                        dbc.Button(
                                            "Add Stock",
                                            id={"type": "add-stock-btn", "index": 0},
                                            color="success",
                                            size="sm",
                                            className="mt-3"
                                        )
                                    ], width=2)
                                ], className="mb-2", id={"type": "stock-row", "index": 0})
                            ]),
                            
                            # Weight Summary
                            dbc.Row([
                                dbc.Col([
                                    dbc.Alert(
                                        id="weight-summary",
                                        children="Total Weight: 0%",
                                        color="info",
                                        className="mt-2"
                                    )
                                ], width=12)
                            ])
                        ], width=12)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Create Portfolio", id="create-portfolio-btn", color="primary", className="me-2"),
                            dbc.Button("Auto-Weight", id="auto-weight-btn", color="secondary")
                        ], width=12)
                    ])
                ])
            ])
        ], width=6),
        
        # Portfolio List Section
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Saved Portfolios"),
                dbc.CardBody([
                    html.Div(id="portfolio-list")
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Portfolio Analytics Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Portfolio Analytics"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Select Portfolio"),
                            dcc.Dropdown(id="analytics-portfolio-select", placeholder="Select portfolio for analytics")
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Analysis Period"),
                            dcc.Dropdown(
                                id="analytics-period",
                                options=[
                                    {"label": "1 Month", "value": "1M"},
                                    {"label": "3 Months", "value": "3M"},
                                    {"label": "6 Months", "value": "6M"},
                                    {"label": "1 Year", "value": "1Y"},
                                    {"label": "2 Years", "value": "2Y"},
                                    {"label": "5 Years", "value": "5Y"}
                                ],
                                value="1Y"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Calculate Analytics", id="calculate-analytics-btn", color="success", className="me-2"),
                            dbc.Button("Run Backtest", id="run-backtest-btn", color="info")
                        ], width=12)
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Analytics Results
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Performance Metrics"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(id="total-return-metric", className="card-title"),
                                    html.P("Total Return", className="card-text")
                                ])
                            ])
                        ], width=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(id="annualized-return-metric", className="card-title"),
                                    html.P("Annualized Return", className="card-text")
                                ])
                            ])
                        ], width=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(id="sharpe-ratio-metric", className="card-title"),
                                    html.P("Sharpe Ratio", className="card-text")
                                ])
                            ])
                        ], width=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(id="max-drawdown-metric", className="card-title"),
                                    html.P("Max Drawdown", className="card-text")
                                ])
                            ])
                        ], width=3)
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Risk Metrics
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Risk Metrics"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(id="portfolio-volatility-metric", className="card-title"),
                                    html.P("Portfolio Volatility", className="card-text")
                                ])
                            ])
                        ], width=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(id="var-95-metric", className="card-title"),
                                    html.P("VaR (95%)", className="card-text")
                                ])
                            ])
                        ], width=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(id="cvar-95-metric", className="card-title"),
                                    html.P("CVaR (95%)", className="card-text")
                                ])
                            ])
                        ], width=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(id="diversification-ratio-metric", className="card-title"),
                                    html.P("Diversification Ratio", className="card-text")
                                ])
                            ])
                        ], width=3)
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Portfolio Performance Chart"),
                dbc.CardBody([
                    dcc.Graph(id="portfolio-performance-chart-manager")
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Drawdown Chart"),
                dbc.CardBody([
                    dcc.Graph(id="portfolio-drawdown-chart")
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Portfolio Comparison
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Portfolio Comparison"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Select Portfolios to Compare"),
                            dcc.Dropdown(id="comparison-portfolios", multi=True, placeholder="Select portfolios")
                        ], width=8),
                        dbc.Col([
                            dbc.Button("Compare Portfolios", id="compare-portfolios-btn", color="warning")
                        ], width=4)
                    ], className="mb-3"),
                    html.Div(id="portfolio-comparison-results")
                ])
            ])
        ], width=12)
    ]),
    
    # Portfolio Details Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Portfolio Details")),
        dbc.ModalBody(id="portfolio-details-content"),
        dbc.ModalFooter([
            dbc.Button("Close", id="close-portfolio-modal", className="ms-auto", n_clicks=0)
        ])
    ], id="portfolio-details-modal", is_open=False, size="lg"),
    
    # Hidden divs for data storage
    html.Div(id="portfolio-data", style={"display": "none"}),
    html.Div(id="analytics-data", style={"display": "none"}),
    html.Div(id="selected-portfolio-id", style={"display": "none"}),
    html.Div(id="stock-rows-count", children="1", style={"display": "none"})
]


@app.callback(
    Output("stock-prices-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_stock_prices_chart(active_tab):
    """Update stock prices chart with real data."""
    if active_tab != "market-tab":
        return go.Figure()
    
    try:
        # Get stock prices data
        stock_data = data_service.get_stock_prices()
        
        if stock_data.empty:
            return go.Figure().add_annotation(
                text="No stock data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        fig = go.Figure()
        
        # Plot each symbol
        for symbol in stock_data['symbol'].unique():
            symbol_data = stock_data[stock_data['symbol'] == symbol].copy()
            symbol_data = symbol_data.sort_values('date')
            
            fig.add_trace(go.Scatter(
                x=symbol_data['date'],
                y=symbol_data['close'],
                mode='lines',
                name=symbol,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="Stock Prices Over Time",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            height=500
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating stock prices chart: {str(e)}")
        return go.Figure().add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )


@app.callback(
    Output("portfolio-performance-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_portfolio_performance_chart(active_tab):
    """Update portfolio performance chart with real data."""
    if active_tab != "portfolio-tab":
        return go.Figure()
    
    try:
        # Get portfolio performance data
        portfolio_data = data_service.get_portfolio_performance()
        
        if portfolio_data.empty:
            return go.Figure().add_annotation(
                text="No portfolio data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Calculate cumulative returns
        portfolio_data = portfolio_data.sort_values(['date', 'symbol'])
        portfolio_data['cumulative_return'] = portfolio_data.groupby('symbol')['returns'].cumsum()
        
        fig = go.Figure()
        
        # Plot each symbol's cumulative returns
        for symbol in portfolio_data['symbol'].unique():
            symbol_data = portfolio_data[portfolio_data['symbol'] == symbol]
            
            fig.add_trace(go.Scatter(
                x=symbol_data['date'],
                y=symbol_data['cumulative_return'] * 100,  # Convert to percentage
                mode='lines',
                name=symbol,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="Portfolio Performance - Cumulative Returns",
            xaxis_title="Date",
            yaxis_title="Cumulative Return (%)",
            hovermode='x unified',
            height=500
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating portfolio performance chart: {str(e)}")
        return go.Figure().add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )


@app.callback(
    Output("risk-metrics-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_risk_metrics_chart(active_tab):
    """Update risk metrics chart with real data."""
    if active_tab != "risk-tab":
        return go.Figure()
    
    try:
        # Get portfolio performance data for volatility calculation
        portfolio_data = data_service.get_portfolio_performance()
        
        if portfolio_data.empty:
            return go.Figure().add_annotation(
                text="No portfolio data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Calculate rolling volatility (30-day window)
        portfolio_data = portfolio_data.sort_values('date')
        portfolio_returns = portfolio_data.groupby('date')['returns'].mean()  # Equal weight portfolio
        rolling_vol = portfolio_returns.rolling(window=30).std() * np.sqrt(252)  # Annualized
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=rolling_vol.index,
            y=rolling_vol.values * 100,  # Convert to percentage
            mode='lines',
            name='30-Day Rolling Volatility',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title="Portfolio Volatility Over Time",
            xaxis_title="Date",
            yaxis_title="Volatility (%)",
            hovermode='x unified',
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating risk metrics chart: {str(e)}")
        return go.Figure().add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )


@app.callback(
    Output("risk-summary", "children"),
    [Input("tabs", "active_tab")]
)
def update_risk_summary(active_tab):
    """Update risk summary with real data."""
    if active_tab != "risk-tab":
        return ""
    
    try:
        # Get risk metrics
        risk_metrics = data_service.get_risk_metrics()
        
        if risk_metrics.empty:
            return html.P("No risk metrics available", className="text-muted")
        
        metrics = risk_metrics.iloc[0]
        
        summary_items = [
            ("Sharpe Ratio", f"{metrics['sharpe_ratio']:.3f}"),
            ("VaR (95%)", f"{metrics['var_95']:.3f}"),
            ("VaR (99%)", f"{metrics['var_99']:.3f}"),
            ("Max Drawdown", f"{metrics['max_drawdown']:.3f}"),
            ("Volatility", f"{metrics['volatility']:.3f}"),
            ("Beta", f"{metrics['beta']:.3f}")
        ]
        
        return html.Div([
            html.Div([
                html.Strong(item[0] + ":"),
                html.Span(f" {item[1]}", className="ml-2")
            ], className="mb-2") for item in summary_items
        ])
        
    except Exception as e:
        logger.error(f"Error updating risk summary: {str(e)}")
        return html.P(f"Error loading data: {str(e)}", className="text-danger")


@app.callback(
    Output("var-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_var_chart(active_tab):
    """Update VaR chart with real data."""
    if active_tab != "risk-tab":
        return go.Figure()
    
    try:
        # Get portfolio performance data
        portfolio_data = data_service.get_portfolio_performance()
        
        if portfolio_data.empty:
            return go.Figure().add_annotation(
                text="No portfolio data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Calculate daily VaR
        portfolio_returns = portfolio_data.groupby('date')['returns'].mean()
        var_95 = np.percentile(portfolio_returns, 5)
        var_99 = np.percentile(portfolio_returns, 1)
        
        fig = go.Figure()
        
        # Add VaR lines
        fig.add_hline(y=var_95, line_dash="dash", line_color="orange", 
                     annotation_text=f"VaR 95%: {var_95:.3f}")
        fig.add_hline(y=var_99, line_dash="dash", line_color="red", 
                     annotation_text=f"VaR 99%: {var_99:.3f}")
        
        # Add returns histogram
        fig.add_trace(go.Histogram(
            x=portfolio_returns,
            nbinsx=50,
            name="Daily Returns",
            opacity=0.7
        ))
        
        fig.update_layout(
            title="Value at Risk Analysis",
            xaxis_title="Daily Returns",
            yaxis_title="Frequency",
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating VaR chart: {str(e)}")
        return go.Figure().add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )


@app.callback(
    Output("drawdown-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_drawdown_chart(active_tab):
    """Update drawdown chart with real data."""
    if active_tab != "risk-tab":
        return go.Figure()
    
    try:
        # Get portfolio performance data
        portfolio_data = data_service.get_portfolio_performance()
        
        if portfolio_data.empty:
            return go.Figure().add_annotation(
                text="No portfolio data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Calculate cumulative returns and drawdown
        portfolio_returns = portfolio_data.groupby('date')['returns'].mean()
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=drawdown.index,
            y=drawdown.values * 100,  # Convert to percentage
            mode='lines',
            name='Drawdown',
            line=dict(color='red', width=2),
            fill='tonexty'
        ))
        
        fig.update_layout(
            title="Portfolio Drawdown",
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            hovermode='x unified',
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating drawdown chart: {str(e)}")
        return go.Figure().add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )


@app.callback(
    Output("correlation-matrix", "figure"),
    [Input("tabs", "active_tab")]
)
def update_correlation_matrix(active_tab):
    """Update correlation matrix with real data."""
    if active_tab != "correlation-tab":
        return go.Figure()
    
    try:
        # Get correlation matrix
        correlation_matrix = data_service.get_correlation_matrix()
        
        if correlation_matrix.empty:
            return go.Figure().add_annotation(
                text="No correlation data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=np.round(correlation_matrix.values, 3),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Asset Correlation Matrix",
            xaxis_title="Assets",
            yaxis_title="Assets",
            height=500
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating correlation matrix: {str(e)}")
        return go.Figure().add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )


# Stock Filtering Callbacks
@app.callback(
    [Output("stock-filtered-data", "children"),
     Output("stock-filtered-count", "children"),
     Output("stock-avg-pe", "children"),
     Output("stock-avg-dividend", "children")],
    [Input("stock-apply-filters", "n_clicks")],
    [State("stock-market-cap-filter", "value"),
     State("stock-sector-filter", "value"),
     State("stock-industry-filter", "value"),
     State("stock-price-min", "value"),
     State("stock-price-max", "value"),
     State("stock-pe-min", "value"),
     State("stock-pe-max", "value"),
     State("stock-div-min", "value"),
     State("stock-div-max", "value")]
)
def apply_stock_filters(n_clicks, market_cap, sectors, industries, price_min, price_max,
                       pe_min, pe_max, div_min, div_max):
    """Apply stock filters and return filtered data."""
    
    if n_clicks is None:
        # Return all stocks on initial load
        filtered_data = stock_filtering_service.get_all_stocks()
    else:
        # Build filter criteria
        filters = {}
        
        if market_cap:
            filters['market_cap_categories'] = market_cap
        if sectors:
            filters['sectors'] = sectors
        if industries:
            filters['industries'] = industries
        if price_min is not None:
            filters['price_min'] = price_min
        if price_max is not None:
            filters['price_max'] = price_max
        if pe_min is not None:
            filters['pe_ratio_min'] = pe_min
        if pe_max is not None:
            filters['pe_ratio_max'] = pe_max
        if div_min is not None:
            filters['dividend_yield_min'] = div_min / 100  # Convert percentage to decimal
        if div_max is not None:
            filters['dividend_yield_max'] = div_max / 100
        
        # Apply filters
        filtered_data = stock_filtering_service.get_stocks_by_filters(filters)
    
    # Calculate summary metrics
    filtered_count = len(filtered_data)
    avg_pe = filtered_data['pe_ratio'].mean() if not filtered_data.empty else 0
    avg_dividend = filtered_data['dividend_yield'].mean() if not filtered_data.empty else 0
    
    # Store filtered data as JSON
    filtered_json = filtered_data.to_json(orient='records') if not filtered_data.empty else "[]"
    
    return filtered_json, filtered_count, f"{avg_pe:.2f}", f"{avg_dividend:.4f}"


@app.callback(
    [Output("stock-market-cap-chart", "figure"),
     Output("stock-sector-chart", "figure")],
    [Input("stock-filtered-data", "children")]
)
def update_stock_charts(filtered_json):
    """Update stock charts based on filtered data."""
    
    if not filtered_json or filtered_json == "[]":
        # Return empty charts
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig
    
    try:
        from io import StringIO
        filtered_data = pd.read_json(StringIO(filtered_json), orient='records')
        
        # Market Cap Distribution
        cap_counts = filtered_data['market_cap_category'].value_counts()
        cap_fig = px.pie(values=cap_counts.values, names=cap_counts.index, title="Market Cap Distribution")
        
        # Sector Distribution
        sector_counts = filtered_data['sector'].value_counts()
        sector_fig = px.bar(x=sector_counts.index, y=sector_counts.values, title="Sector Distribution")
        sector_fig.update_layout(xaxis_tickangle=45)
        
        return cap_fig, sector_fig
        
    except Exception as e:
        logger.error(f"Error updating stock charts: {str(e)}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Error loading data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig


@app.callback(
    Output("stock-results-table", "children"),
    [Input("stock-filtered-data", "children")]
)
def update_stock_table(filtered_json):
    """Update stock table based on filtered data."""
    
    if not filtered_json or filtered_json == "[]":
        return html.P("No stocks match the current filters.")
    
    try:
        from io import StringIO
        filtered_data = pd.read_json(StringIO(filtered_json), orient='records')
        
        # Select relevant columns for display
        display_columns = [
            'symbol', 'name', 'sector', 'industry', 'market_cap_category',
            'current_price', 'pe_ratio', 'dividend_yield', 'beta', 'volume'
        ]
        
        # Create table
        table_data = filtered_data[display_columns].round(2)
        
        return dbc.Table.from_dataframe(
            table_data,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            size="sm"
        )
        
    except Exception as e:
        logger.error(f"Error updating stock table: {str(e)}")
        return html.P("Error loading stock data.")


@app.callback(
    [Output("stock-market-cap-filter", "value"),
     Output("stock-sector-filter", "value"),
     Output("stock-industry-filter", "value"),
     Output("stock-price-min", "value"),
     Output("stock-price-max", "value"),
     Output("stock-pe-min", "value"),
     Output("stock-pe-max", "value"),
     Output("stock-div-min", "value"),
     Output("stock-div-max", "value")],
    [Input("stock-clear-filters", "n_clicks")]
)
def clear_stock_filters(n_clicks):
    """Clear all stock filters."""
    if n_clicks:
        return [None] * 9  # Clear all 9 filter inputs
    return [dash.no_update] * 9


@app.callback(
    Output("stock-total-count", "children"),
    [Input("stock-filtered-data", "children")]
)
def update_stock_total_count(filtered_json):
    """Update total stocks count."""
    try:
        all_stocks = stock_filtering_service.get_all_stocks()
        return len(all_stocks)
    except Exception as e:
        logger.error(f"Error getting total stocks: {str(e)}")
        return 0


# Portfolio Management Callbacks
@app.callback(
    Output("portfolio-list", "children"),
    [Input("create-portfolio-btn", "n_clicks"),
     Input("tabs", "active_tab")],
    prevent_initial_call=False
)
def update_portfolio_list(n_clicks, active_tab):
    """Update portfolio list and dropdown options"""
    logger.info(f"Update portfolio list called: n_clicks={n_clicks}, active_tab={active_tab}")
    
    if active_tab == "portfolio-manager-tab":
        try:
            portfolios = portfolio_management_service.get_all_portfolios()
            logger.info(f"Retrieved {len(portfolios)} portfolios from database")
            
            # Create portfolio list display
            portfolio_cards = []
            for portfolio in portfolios:
                card = dbc.Card([
                    dbc.CardBody([
                        html.H5(portfolio['name'], className="card-title"),
                        html.P(portfolio['description'], className="card-text"),
                        html.Small(f"Strategy: {portfolio['strategy']}", className="text-muted"),
                        html.Br(),
                        html.Small(f"Stocks: {', '.join(portfolio['symbols'])}", className="text-muted"),
                        html.Br(),
                        html.Small(f"Weights: {', '.join([f'{w:.1%}' for w in portfolio['weights']])}", className="text-muted"),
                        html.Br(),
                        html.Small(f"Created: {portfolio['created_at'][:10] if portfolio['created_at'] else 'N/A'}", className="text-muted"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("View Details", 
                                          id={"type": "view-details-btn", "index": portfolio['id']}, 
                                          size="sm", color="info", className="me-1"),
                                dbc.Button("Delete", 
                                          id={"type": "delete-portfolio-btn", "index": portfolio['id']}, 
                                          size="sm", color="danger")
                            ], width=12)
                        ], className="mt-2")
                    ])
                ], className="mb-2")
                portfolio_cards.append(card)
            
            # Create dropdown options
            portfolio_options = [{"label": p['name'], "value": p['id']} for p in portfolios]
            
            return portfolio_cards
            
        except Exception as e:
            logger.error(f"Error updating portfolio list: {str(e)}")
            return [html.P("Error loading portfolios")]
    
    return dash.no_update


# Dynamic Stock Form Callbacks
@app.callback(
    [Output("stock-holdings-container", "children"),
     Output("stock-rows-count", "children")],
    [Input({"type": "add-stock-btn", "index": dash.dependencies.ALL}, "n_clicks")],
    [State("stock-rows-count", "children"),
     State({"type": "stock-dropdown", "index": dash.dependencies.ALL}, "value"),
     State({"type": "weight-input", "index": dash.dependencies.ALL}, "value")],
    prevent_initial_call=True
)
def add_stock_row(n_clicks_list, current_count, stock_values, weight_values):
    """Add a new stock row when Add Stock button is clicked"""
    if not any(n_clicks_list):
        return dash.no_update, dash.no_update
    
    # Get available stocks for dropdown options
    available_stocks = stock_filtering_service.get_all_stocks()
    stock_options = [{"label": f"{row['symbol']} - {row['name']}", "value": row['symbol']} 
                     for _, row in available_stocks.iterrows()]
    
    current_count = int(current_count)
    new_count = current_count + 1
    
    # Create all rows preserving existing values
    all_rows = []
    for i in range(new_count + 1):
        # Get existing values for this row
        stock_value = stock_values[i] if i < len(stock_values) else None
        weight_value = weight_values[i] if i < len(weight_values) else None
        
        row = dbc.Row([
            dbc.Col([
                dbc.Label("Stock Symbol"),
                dcc.Dropdown(
                    id={"type": "stock-dropdown", "index": i},
                    options=stock_options,
                    placeholder="Select stock",
                    value=stock_value
                )
            ], width=6),
            dbc.Col([
                dbc.Label("Weight (%)"),
                dbc.Input(
                    id={"type": "weight-input", "index": i},
                    type="number",
                    placeholder="0",
                    min=0,
                    max=100,
                    step=0.1,
                    value=weight_value
                )
            ], width=4),
            dbc.Col([
                dbc.Label("Action"),
                dbc.Button(
                    "Add Stock",
                    id={"type": "add-stock-btn", "index": i},
                    color="success",
                    size="sm",
                    className="mt-3"
                )
            ], width=2)
        ], className="mb-2", id={"type": "stock-row", "index": i})
        
        all_rows.append(row)
    
    return all_rows, str(new_count)


@app.callback(
    Output("weight-summary", "children"),
    [Input({"type": "weight-input", "index": dash.dependencies.ALL}, "value")],
    prevent_initial_call=False
)
def update_weight_summary(weight_values):
    """Update the weight summary when any weight input changes"""
    if not weight_values:
        return "Total Weight: 0%"
    
    # Calculate total weight
    total_weight = 0
    for weight in weight_values:
        if weight is not None:
            total_weight += float(weight)
    
    # Determine color based on total
    if total_weight == 100:
        color = "success"
        message = f"Total Weight: {total_weight:.1f}% ✓ Perfect!"
    elif total_weight > 100:
        color = "danger"
        message = f"Total Weight: {total_weight:.1f}% ⚠️ Exceeds 100%"
    elif total_weight > 0:
        color = "warning"
        message = f"Total Weight: {total_weight:.1f}% (Need {100-total_weight:.1f}% more)"
    else:
        color = "info"
        message = f"Total Weight: {total_weight:.1f}%"
    
    return dbc.Alert(message, color=color, className="mt-2")


@app.callback(
    [Output("portfolio-name", "value"),
     Output("portfolio-description", "value"),
     Output("stock-holdings-container", "children", allow_duplicate=True),
     Output("stock-rows-count", "children", allow_duplicate=True),
     Output("portfolio-list", "children", allow_duplicate=True),
     Output("portfolio-error-alert", "children")],
    [Input("create-portfolio-btn", "n_clicks")],
    [State("portfolio-name", "value"),
     State("portfolio-description", "value"),
     State("portfolio-strategy", "value"),
     State({"type": "stock-dropdown", "index": dash.dependencies.ALL}, "value"),
     State({"type": "weight-input", "index": dash.dependencies.ALL}, "value")],
    prevent_initial_call=True
)
def create_portfolio_dynamic(n_clicks, name, description, strategy, stock_values, weight_values):
    """Create portfolio using dynamic form data"""
    logger.info(f"Create portfolio called: n_clicks={n_clicks}, name={name}")
    
    if n_clicks and name and stock_values and weight_values:
        try:
            # Filter out None values and create stock-weight pairs
            stocks = []
            weights = []
            
            for stock, weight in zip(stock_values, weight_values):
                if stock is not None and weight is not None and weight > 0:
                    stocks.append(stock)
                    weights.append(float(weight) / 100)  # Convert percentage to decimal
            
            if not stocks:
                logger.error("No valid stocks selected")
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update
            
            # Normalize weights to ensure they sum to 1.0
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            else:
                weights = [1.0 / len(stocks)] * len(stocks)
            
            logger.info(f"Creating portfolio with stocks: {stocks}, weights: {weights}")
            
            # Create portfolio
            portfolio = portfolio_management_service.create_portfolio(
                name=name,
                description=description or "",
                symbols=stocks,
                weights=weights,
                strategy=strategy or "Custom"
            )
            
            logger.info(f"Successfully created portfolio: {portfolio['name']} with ID {portfolio['id']}")
            
            # Reset form
            available_stocks = stock_filtering_service.get_all_stocks()
            stock_options = [{"label": f"{row['symbol']} - {row['name']}", "value": row['symbol']} 
                             for _, row in available_stocks.iterrows()]
            
            # Reset to single row
            reset_rows = [dbc.Row([
                dbc.Col([
                    dbc.Label("Stock Symbol"),
                    dcc.Dropdown(
                        id={"type": "stock-dropdown", "index": 0},
                        options=stock_options,
                        placeholder="Select stock"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Weight (%)"),
                    dbc.Input(
                        id={"type": "weight-input", "index": 0},
                        type="number",
                        placeholder="0",
                        min=0,
                        max=100,
                        step=0.1
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label("Action"),
                    dbc.Button(
                        "Add Stock",
                        id={"type": "add-stock-btn", "index": 0},
                        color="success",
                        size="sm",
                        className="mt-3"
                    )
                ], width=2)
            ], className="mb-2", id={"type": "stock-row", "index": 0})]
            
            # Update portfolio list
            portfolios = portfolio_management_service.get_all_portfolios()
            portfolio_cards = []
            for portfolio in portfolios:
                card = dbc.Card([
                    dbc.CardBody([
                        html.H5(portfolio['name'], className="card-title"),
                        html.P(portfolio['description'], className="card-text"),
                        html.Small(f"Strategy: {portfolio['strategy']}", className="text-muted"),
                        html.Br(),
                        html.Small(f"Stocks: {', '.join(portfolio['symbols'])}", className="text-muted"),
                        html.Br(),
                        html.Small(f"Weights: {', '.join([f'{w:.1%}' for w in portfolio['weights']])}", className="text-muted"),
                        html.Br(),
                        html.Small(f"Created: {portfolio['created_at'][:10] if portfolio['created_at'] else 'N/A'}", className="text-muted"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("View Details", 
                                          id={"type": "view-details-btn", "index": portfolio['id']}, 
                                          size="sm", color="info", className="me-1"),
                                dbc.Button("Delete", 
                                          id={"type": "delete-portfolio-btn", "index": portfolio['id']}, 
                                          size="sm", color="danger")
                            ], width=12)
                        ], className="mt-2")
                    ])
                ], className="mb-2")
                portfolio_cards.append(card)
            
            return "", "", reset_rows, "1", portfolio_cards, ""
            
        except Exception as e:
            logger.error(f"Error creating portfolio: {str(e)}")
            import traceback
            traceback.print_exc()
            # Check if it's a duplicate name error
            if "duplicate key value violates unique constraint" in str(e):
                error_msg = "Portfolio name already exists. Please use a different name."
                logger.error(error_msg)
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dbc.Alert(error_msg, color="danger")
            else:
                error_msg = f"Error creating portfolio: {str(e)}"
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dbc.Alert(error_msg, color="danger")
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, ""


# Portfolio Details Modal Callbacks
@app.callback(
    Output("portfolio-details-content", "children"),
    [Input("selected-portfolio-id", "data")],
    prevent_initial_call=True
)
def update_portfolio_details_content(selected_portfolio_id):
    """Update portfolio details content when portfolio ID is selected"""
    if selected_portfolio_id:
        try:
            portfolio = portfolio_management_service.get_portfolio(selected_portfolio_id)
            if portfolio:
                # Create detailed content
                content = [
                    dbc.Row([
                        dbc.Col([
                            html.H4(portfolio['name'], className="mb-3"),
                            html.P(portfolio['description'], className="text-muted mb-3")
                        ], width=12)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Portfolio Information"),
                                dbc.CardBody([
                                    html.P(f"Strategy: {portfolio['strategy']}", className="mb-2"),
                                    html.P(f"Created: {portfolio['created_at'][:10] if portfolio['created_at'] else 'N/A'}", className="mb-2"),
                                    html.P(f"Last Updated: {portfolio['updated_at'][:10] if portfolio['updated_at'] else 'N/A'}", className="mb-0")
                                ])
                            ])
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Holdings Summary"),
                                dbc.CardBody([
                                    html.P(f"Number of Stocks: {len(portfolio['symbols'])}", className="mb-2"),
                                    html.P(f"Total Weight: {sum(portfolio['weights']):.1%}", className="mb-0")
                                ])
                            ])
                        ], width=6)
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Portfolio Holdings"),
                                dbc.CardBody([
                                    dbc.Table([
                                        html.Thead([
                                            html.Tr([
                                                html.Th("Symbol"),
                                                html.Th("Weight"),
                                                html.Th("Allocation")
                                            ])
                                        ]),
                                        html.Tbody([
                                            html.Tr([
                                                html.Td(symbol),
                                                html.Td(f"{weight:.1%}"),
                                                html.Td([
                                                    dbc.Progress(
                                                        value=weight*100,
                                                        color="primary",
                                                        className="mb-0",
                                                        style={"height": "20px"}
                                                    )
                                                ])
                                            ]) for symbol, weight in zip(portfolio['symbols'], portfolio['weights'])
                                        ])
                                    ], striped=True, bordered=True, hover=True)
                                ])
                            ])
                        ], width=12)
                    ])
                ]
                return True, content
            else:
                return False, "Portfolio not found"
        except Exception as e:
            logger.error(f"Error getting portfolio details: {str(e)}")
            return False, f"Error loading portfolio: {str(e)}"
    
    return ""


# Separate callback for close button
@app.callback(
    [Output("portfolio-details-modal", "is_open", allow_duplicate=True),
     Output("selected-portfolio-id", "data", allow_duplicate=True)],
    [Input("close-portfolio-modal", "n_clicks")],
    prevent_initial_call=True
)
def close_portfolio_modal(close_clicks):
    """Close portfolio modal and clear selected portfolio ID"""
    if close_clicks:
        return False, None
    return dash.no_update, dash.no_update


# Separate callback for view details button clicks - using a different approach
@app.callback(
    [Output("selected-portfolio-id", "data"),
     Output("portfolio-details-modal", "is_open", allow_duplicate=True)],
    [Input({"type": "view-details-btn", "index": dash.dependencies.ALL}, "n_clicks")],
    prevent_initial_call=True
)
def handle_view_details_click(view_clicks):
    """Handle view details button clicks and store portfolio ID"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    trigger_id = ctx.triggered[0]["prop_id"]
    
    if "view-details-btn" in trigger_id:
        # Extract portfolio ID from the trigger using a more robust method
        trigger_data = ctx.triggered[0]["prop_id"].split(".")[0]
        # Parse the JSON-like structure to extract the index
        try:
            # The trigger_data looks like: {"type":"view-details-btn","index":22}
            portfolio_id = int(trigger_data.split('"index":')[1].split(',')[0].split('}')[0])
            logger.info(f"View details clicked for portfolio ID: {portfolio_id}")
            return portfolio_id, True  # Return portfolio ID and open modal
        except (IndexError, ValueError):
            # Fallback: try to extract number from the string
            import re
            numbers = re.findall(r'\d+', trigger_data)
            if numbers:
                portfolio_id = int(numbers[-1])  # Take the last number found
                logger.info(f"View details clicked for portfolio ID (fallback): {portfolio_id}")
                return portfolio_id, True  # Return portfolio ID and open modal
            else:
                logger.error(f"Could not extract portfolio ID from trigger: {trigger_data}")
                return dash.no_update, dash.no_update
    
    return dash.no_update, dash.no_update


@app.callback(
    Output("portfolio-list", "children", allow_duplicate=True),
    [Input({"type": "delete-portfolio-btn", "index": dash.dependencies.ALL}, "n_clicks")],
    prevent_initial_call=True
)
def delete_portfolio(delete_clicks):
    """Delete a portfolio"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]["prop_id"]
    
    if "delete-portfolio-btn" in trigger_id:
        # Extract portfolio ID from the trigger using a more robust method
        trigger_data = ctx.triggered[0]["prop_id"].split(".")[0]
        # Parse the JSON-like structure to extract the index
        try:
            # The trigger_data looks like: {"type":"delete-portfolio-btn","index":22}
            portfolio_id = int(trigger_data.split('"index":')[1].split(',')[0].split('}')[0])
        except (IndexError, ValueError):
            # Fallback: try to extract number from the string
            import re
            numbers = re.findall(r'\d+', trigger_data)
            if numbers:
                portfolio_id = int(numbers[-1])  # Take the last number found
            else:
                logger.error(f"Could not extract portfolio ID from trigger: {trigger_data}")
                return dash.no_update
        
        try:
            # Delete portfolio
            portfolio_management_service.delete_portfolio(portfolio_id)
            logger.info(f"Deleted portfolio with ID {portfolio_id}")
            
            # Refresh portfolio list
            portfolios = portfolio_management_service.get_all_portfolios()
            portfolio_cards = []
            for portfolio in portfolios:
                card = dbc.Card([
                    dbc.CardBody([
                        html.H5(portfolio['name'], className="card-title"),
                        html.P(portfolio['description'], className="card-text"),
                        html.Small(f"Strategy: {portfolio['strategy']}", className="text-muted"),
                        html.Br(),
                        html.Small(f"Stocks: {', '.join(portfolio['symbols'])}", className="text-muted"),
                        html.Br(),
                        html.Small(f"Weights: {', '.join([f'{w:.1%}' for w in portfolio['weights']])}", className="text-muted"),
                        html.Br(),
                        html.Small(f"Created: {portfolio['created_at'][:10] if portfolio['created_at'] else 'N/A'}", className="text-muted"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("View Details", 
                                          id={"type": "view-details-btn", "index": portfolio['id']}, 
                                          size="sm", color="info", className="me-1"),
                                dbc.Button("Delete", 
                                          id={"type": "delete-portfolio-btn", "index": portfolio['id']}, 
                                          size="sm", color="danger")
                            ], width=12)
                        ], className="mt-2")
                    ])
                ], className="mb-2")
                portfolio_cards.append(card)
            
            return portfolio_cards
            
        except Exception as e:
            logger.error(f"Error deleting portfolio: {str(e)}")
            return dash.no_update
    
    return dash.no_update


@app.callback(
    [Output("total-return-metric", "children"),
     Output("annualized-return-metric", "children"),
     Output("sharpe-ratio-metric", "children"),
     Output("max-drawdown-metric", "children"),
     Output("portfolio-volatility-metric", "children"),
     Output("var-95-metric", "children"),
     Output("cvar-95-metric", "children"),
     Output("diversification-ratio-metric", "children"),
     Output("analytics-data", "children")],
    [Input("calculate-analytics-btn", "n_clicks")],
    [State("analytics-portfolio-select", "value"),
     State("analytics-period", "value")]
)
def calculate_portfolio_analytics(n_clicks, portfolio_id, period):
    """Calculate portfolio analytics"""
    if n_clicks and portfolio_id:
        try:
            portfolio = portfolio_management_service.get_portfolio(portfolio_id)
            if not portfolio:
                return ["N/A"] * 8 + ["{}"]
            
            # Calculate analytics
            analytics = portfolio_management_service.calculate_portfolio_analytics(
                portfolio['symbols'], portfolio['weights']
            )
            
            if "error" in analytics:
                return ["Error"] * 8 + [json.dumps(analytics)]
            
            # Format metrics
            total_return = f"{analytics.get('total_return', 0) * 100:.2f}%"
            annualized_return = f"{analytics.get('annualized_return', 0) * 100:.2f}%"
            sharpe_ratio = f"{analytics.get('sharpe_ratio', 0):.3f}"
            max_drawdown = f"{analytics.get('max_drawdown', 0) * 100:.2f}%"
            volatility = f"{analytics.get('portfolio_volatility', 0) * 100:.2f}%"
            var_95 = f"{analytics.get('var_95', 0) * 100:.2f}%"
            cvar_95 = f"{analytics.get('cvar_95', 0) * 100:.2f}%"
            diversification = f"{analytics.get('diversification_ratio', 0):.3f}"
            
            return [total_return, annualized_return, sharpe_ratio, max_drawdown, 
                   volatility, var_95, cvar_95, diversification, json.dumps(analytics)]
            
        except Exception as e:
            logger.error(f"Error calculating analytics: {str(e)}")
            return ["Error"] * 8 + [json.dumps({"error": str(e)})]
    
    return ["N/A"] * 8 + ["{}"]


@app.callback(
    [Output("portfolio-performance-chart-manager", "figure"),
     Output("portfolio-drawdown-chart", "figure")],
    [Input("analytics-data", "children")]
)
def update_portfolio_charts(analytics_json):
    """Update portfolio performance and drawdown charts"""
    if not analytics_json or analytics_json == "{}":
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No analytics data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig
    
    try:
        analytics = json.loads(analytics_json)
        
        if "error" in analytics:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text=f"Error: {analytics['error']}", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return empty_fig, empty_fig
        
        # Create performance chart (placeholder - would need actual time series data)
        performance_fig = go.Figure()
        performance_fig.add_annotation(text="Performance chart would show portfolio value over time", 
                                     xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        performance_fig.update_layout(title="Portfolio Performance", showlegend=False)
        
        # Create drawdown chart (placeholder)
        drawdown_fig = go.Figure()
        drawdown_fig.add_annotation(text="Drawdown chart would show portfolio drawdowns over time", 
                                  xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        drawdown_fig.update_layout(title="Portfolio Drawdown", showlegend=False)
        
        return performance_fig, drawdown_fig
        
    except Exception as e:
        logger.error(f"Error updating portfolio charts: {str(e)}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Error loading charts", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig


@app.callback(
    Output("portfolio-comparison-results", "children"),
    [Input("compare-portfolios-btn", "n_clicks")],
    [State("comparison-portfolios", "value")]
)
def compare_portfolios(n_clicks, portfolio_ids):
    """Compare multiple portfolios"""
    if n_clicks and portfolio_ids and len(portfolio_ids) > 1:
        try:
            comparison = portfolio_management_service.compare_portfolios(portfolio_ids)
            
            if "error" in comparison:
                return html.P(f"Error: {comparison['error']}")
            
            # Create comparison table
            comparison_data = []
            for portfolio in comparison['portfolios']:
                analytics = portfolio.get('analytics', {})
                comparison_data.append({
                    'Portfolio': portfolio['name'],
                    'Strategy': portfolio['strategy'],
                    'Total Return': f"{analytics.get('total_return', 0) * 100:.2f}%",
                    'Annualized Return': f"{analytics.get('annualized_return', 0) * 100:.2f}%",
                    'Sharpe Ratio': f"{analytics.get('sharpe_ratio', 0):.3f}",
                    'Max Drawdown': f"{analytics.get('max_drawdown', 0) * 100:.2f}%",
                    'Volatility': f"{analytics.get('portfolio_volatility', 0) * 100:.2f}%"
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            return dbc.Table.from_dataframe(
                comparison_df,
                striped=True,
                bordered=True,
                hover=True,
                responsive=True,
                size="sm"
            )
            
        except Exception as e:
            logger.error(f"Error comparing portfolios: {str(e)}")
            return html.P(f"Error: {str(e)}")
    
    return html.P("Select at least 2 portfolios to compare")


if __name__ == "__main__":
    print("Starting Quantitative Finance Pipeline Dashboard with Real Data...")
    print("Dashboard will be available at: http://localhost:8050")
    print("Press Ctrl+C to stop the server")
    app.run_server(debug=True, host='0.0.0.0', port=8050)
