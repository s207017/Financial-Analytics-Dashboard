"""
Simplified Dash application that can run without database connection.
"""
import dash
from dash import dcc, html, Input, Output, callback_context, no_update
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
import logging
import sys
import os
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from src.data_access.portfolio_management_service import PortfolioManagementService
    PORTFOLIO_SERVICE = PortfolioManagementService()
    DATABASE_AVAILABLE = True
except Exception as e:
    print(f"Database not available: {e}")
    PORTFOLIO_SERVICE = None
    DATABASE_AVAILABLE = False

def calculate_portfolio_return(symbols, weights, start_date=None, end_date=None):
    """Calculate actual portfolio return based on historical data."""
    try:
        if DATABASE_AVAILABLE and PORTFOLIO_SERVICE:
            # Use the portfolio service to calculate real analytics
            analytics = PORTFOLIO_SERVICE.calculate_portfolio_analytics(
                symbols=symbols,
                weights=weights,
                start_date=start_date or "2023-01-01",
                end_date=end_date or datetime.now().strftime("%Y-%m-%d")
            )
            # Check if analytics contains an error
            if "error" in analytics:
                return "Data Unavailable"
            return analytics.get("total_return", "Data Unavailable")
        else:
            # Database not available
            return "Data Unavailable"
    except Exception as e:
        print(f"Error calculating portfolio return: {e}")
        # Return "Data Unavailable" on error
        return "Data Unavailable"

def format_return_display(return_value):
    """Format return value for display - handles both numeric and string values."""
    if isinstance(return_value, str):
        return return_value
    else:
        return f"{return_value:.1%}"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Quantitative Finance Pipeline Dashboard"

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Quantitative Finance Pipeline Dashboard", 
                   className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    # Navigation tabs
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="Portfolio Overview", tab_id="portfolio-tab"),
                dbc.Tab(label="Portfolio Management", tab_id="portfolio-mgmt-tab"),
                dbc.Tab(label="Risk Analysis", tab_id="risk-tab"),
                dbc.Tab(label="Performance Metrics", tab_id="performance-tab"),
                dbc.Tab(label="Correlation Analysis", tab_id="correlation-tab"),
                dbc.Tab(label="Optimization", tab_id="optimization-tab"),
            ], id="tabs", active_tab="portfolio-tab")
        ])
    ], className="mb-4"),
    
    # Tab content
    html.Div(id="tab-content"),
    
    # Hidden div to store portfolio data
    html.Div(id="portfolio-storage", style={"display": "none"}),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Quantitative Finance Pipeline Dashboard - Demo Mode", 
                  className="text-center text-muted")
        ])
    ])
], fluid=True)

# Portfolio Overview Tab
def create_portfolio_overview():
    """Create portfolio overview tab content."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Portfolio Performance"),
                dcc.Graph(id="portfolio-performance-chart")
            ], width=8),
            dbc.Col([
                html.H3("Key Metrics"),
                html.Div(id="key-metrics")
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Asset Allocation"),
                dcc.Graph(id="asset-allocation-chart")
            ], width=6),
            dbc.Col([
                html.H3("Returns Distribution"),
                dcc.Graph(id="returns-distribution-chart")
            ], width=6)
        ])
    ])

# Risk Analysis Tab
def create_risk_analysis():
    """Create risk analysis tab content."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Risk Metrics Over Time"),
                dcc.Graph(id="risk-metrics-chart")
            ], width=8),
            dbc.Col([
                html.H3("Risk Summary"),
                html.Div(id="risk-summary")
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Value at Risk (VaR)"),
                dcc.Graph(id="var-chart")
            ], width=6),
            dbc.Col([
                html.H3("Drawdown Analysis"),
                dcc.Graph(id="drawdown-chart")
            ], width=6)
        ])
    ])

# Performance Metrics Tab
def create_performance_metrics():
    """Create performance metrics tab content."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Performance Comparison"),
                dcc.Graph(id="performance-comparison-chart")
            ], width=8),
            dbc.Col([
                html.H3("Performance Summary"),
                html.Div(id="performance-summary")
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Rolling Sharpe Ratio"),
                dcc.Graph(id="rolling-sharpe-chart")
            ], width=6),
            dbc.Col([
                html.H3("Rolling Volatility"),
                dcc.Graph(id="rolling-volatility-chart")
            ], width=6)
        ])
    ])

# Correlation Analysis Tab
def create_correlation_analysis():
    """Create correlation analysis tab content."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Correlation Heatmap"),
                dcc.Graph(id="correlation-heatmap")
            ], width=8),
            dbc.Col([
                html.H3("Correlation Statistics"),
                html.Div(id="correlation-stats")
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Rolling Correlation"),
                dcc.Graph(id="rolling-correlation-chart")
            ], width=12)
        ])
    ])

# Portfolio Management Tab
def create_portfolio_management():
    """Create portfolio management tab content."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Create New Portfolio"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Portfolio Name:"),
                                dbc.Input(id="portfolio-name", placeholder="Enter portfolio name", type="text")
                            ], width=6),
                            dbc.Col([
                                html.Label("Strategy:"),
                                dcc.Dropdown(
                                    id="portfolio-strategy",
                                    options=[
                                        {"label": "Equal Weight", "value": "equal_weight"},
                                        {"label": "Market Cap", "value": "market_cap"},
                                        {"label": "Risk Parity", "value": "risk_parity"},
                                        {"label": "Custom", "value": "custom"}
                                    ],
                                    value="equal_weight"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        # Custom strategy individual stock amounts
                        html.Div(id="custom-amounts-container", style={"display": "none"}),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Label("Description:"),
                                dbc.Textarea(id="portfolio-description", placeholder="Enter portfolio description")
                            ], width=12)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Label("Select Assets:"),
                                dcc.Dropdown(
                                    id="asset-selector",
                                    options=[
                                        {"label": "AAPL - Apple Inc.", "value": "AAPL"},
                                        {"label": "GOOGL - Alphabet Inc.", "value": "GOOGL"},
                                        {"label": "MSFT - Microsoft Corp.", "value": "MSFT"},
                                        {"label": "AMZN - Amazon.com Inc.", "value": "AMZN"},
                                        {"label": "TSLA - Tesla Inc.", "value": "TSLA"},
                                        {"label": "META - Meta Platforms Inc.", "value": "META"},
                                        {"label": "NVDA - NVIDIA Corp.", "value": "NVDA"},
                                        {"label": "NFLX - Netflix Inc.", "value": "NFLX"}
                                    ],
                                    multi=True,
                                    value=["AAPL", "GOOGL", "MSFT"]
                                )
                            ], width=8),
                            dbc.Col([
                                html.Label("Portfolio Value:"),
                                dbc.Input(id="portfolio-value", value=100000, type="number", min=1000)
                            ], width=4)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("Create Portfolio", id="create-portfolio-btn", 
                                         color="primary", className="me-2"),
                                dbc.Button("Update Portfolio", id="update-portfolio-btn", 
                                         color="success", className="me-2", style={"display": "none"}),
                                dbc.Button("Auto-Allocate", id="auto-allocate-btn", 
                                         color="secondary", className="me-2"),
                                dbc.Button("Clear", id="clear-portfolio-btn", 
                                         color="outline-secondary")
                            ], width=12)
                        ])
                    ])
                ])
            ], width=6),
            dbc.Col([
                html.H3("Portfolio Weights"),
                html.Div(id="portfolio-weights-display"),
                html.Hr(),
                html.H3("Portfolio Summary"),
                html.Div(id="portfolio-summary")
            ], width=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.H3("My Portfolios"),
                html.Div(id="portfolios-list")
            ], width=8),
            dbc.Col([
                html.H3("Portfolio Actions"),
                dbc.Card([
                    dbc.CardBody([
                        html.Label("Select Portfolio:"),
                        dcc.Dropdown(id="portfolio-selector", placeholder="Choose a portfolio"),
                        html.Br(),
                        dbc.Button("View Details", id="view-portfolio-btn", 
                                 color="info", className="me-2 mb-2", size="sm"),
                        dbc.Button("Edit Portfolio", id="edit-portfolio-btn", 
                                 color="warning", className="me-2 mb-2", size="sm"),
                        dbc.Button("Delete Portfolio", id="delete-portfolio-btn", 
                                 color="danger", className="me-2 mb-2", size="sm"),
                        html.Br(),
                        dbc.Button("Export Portfolio", id="export-portfolio-btn", 
                                 color="success", className="me-2 mb-2", size="sm"),
                        dbc.Button("Clone Portfolio", id="clone-portfolio-btn", 
                                 color="secondary", className="me-2 mb-2", size="sm")
                    ])
                ]),
                html.Div(id="portfolio-actions-feedback", className="mt-3")
            ], width=4)
        ])
    ])

# Optimization Tab
def create_optimization():
    """Create optimization tab content."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Efficient Frontier"),
                dcc.Graph(id="efficient-frontier-chart")
            ], width=8),
            dbc.Col([
                html.H3("Optimization Parameters"),
                dbc.Card([
                    dbc.CardBody([
                        html.Label("Risk Aversion:"),
                        dcc.Slider(
                            id="risk-aversion-slider",
                            min=0.1, max=5.0, step=0.1, value=1.0,
                            marks={i: str(i) for i in [0.1, 1.0, 2.0, 3.0, 4.0, 5.0]}
                        ),
                        html.Br(),
                        html.Label("Target Return:"),
                        dcc.Slider(
                            id="target-return-slider",
                            min=0.0, max=0.3, step=0.01, value=0.1,
                            marks={i/10: f"{i*10}%" for i in range(0, 31, 5)}
                        ),
                        html.Br(),
                        dbc.Button("Optimize Portfolio", id="optimize-button", 
                                 color="primary", className="mt-2")
                    ])
                ])
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Optimized Portfolio Weights"),
                dcc.Graph(id="optimized-weights-chart")
            ], width=6),
            dbc.Col([
                html.H3("Optimization Results"),
                html.Div(id="optimization-results")
            ], width=6)
        ])
    ])

# Callback for tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    """Render content based on active tab."""
    if active_tab == "portfolio-tab":
        return create_portfolio_overview()
    elif active_tab == "portfolio-mgmt-tab":
        return create_portfolio_management()
    elif active_tab == "risk-tab":
        return create_risk_analysis()
    elif active_tab == "performance-tab":
        return create_performance_metrics()
    elif active_tab == "correlation-tab":
        return create_correlation_analysis()
    elif active_tab == "optimization-tab":
        return create_optimization()
    else:
        return html.Div("Select a tab to view content")

# Callback for portfolio performance chart
@app.callback(
    Output("portfolio-performance-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_portfolio_performance(active_tab):
    """Update portfolio performance chart."""
    if active_tab != "portfolio-tab":
        return go.Figure()
    
    # Generate sample data
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    np.random.seed(42)
    portfolio_values = 10000 * (1 + np.random.normal(0.0005, 0.02, len(dates))).cumprod()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=portfolio_values,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title="Portfolio Performance Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        hovermode='x unified'
    )
    
    return fig

# Callback for key metrics
@app.callback(
    Output("key-metrics", "children"),
    [Input("tabs", "active_tab")]
)
def update_key_metrics(active_tab):
    """Update key metrics display."""
    if active_tab != "portfolio-tab":
        return html.Div()
    
    # Sample metrics
    metrics = [
        {"label": "Total Return", "value": "12.5%", "color": "success"},
        {"label": "Annualized Return", "value": "15.2%", "color": "success"},
        {"label": "Volatility", "value": "18.3%", "color": "warning"},
        {"label": "Sharpe Ratio", "value": "0.83", "color": "info"},
        {"label": "Max Drawdown", "value": "-8.7%", "color": "danger"},
        {"label": "VaR (95%)", "value": "-2.1%", "color": "danger"}
    ]
    
    metric_cards = []
    for metric in metrics:
        metric_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H5(metric["value"], className=f"text-{metric['color']}"),
                    html.P(metric["label"], className="mb-0")
                ])
            ], className="mb-2")
        )
    
    return metric_cards

# Callback for asset allocation chart
@app.callback(
    Output("asset-allocation-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_asset_allocation(active_tab):
    """Update asset allocation pie chart."""
    if active_tab != "portfolio-tab":
        return go.Figure()
    
    # Sample allocation data
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    weights = [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.06, 0.04]
    
    fig = go.Figure(data=[go.Pie(
        labels=assets,
        values=weights,
        hole=0.3
    )])
    
    fig.update_layout(
        title="Current Asset Allocation",
        showlegend=True
    )
    
    return fig

# Callback for correlation heatmap
@app.callback(
    Output("correlation-heatmap", "figure"),
    [Input("tabs", "active_tab")]
)
def update_correlation_heatmap(active_tab):
    """Update correlation heatmap."""
    if active_tab != "correlation-tab":
        return go.Figure()
    
    # Sample correlation data
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    np.random.seed(42)
    correlation_matrix = np.random.rand(len(assets), len(assets))
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
    np.fill_diagonal(correlation_matrix, 1.0)
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix,
        x=assets,
        y=assets,
        colorscale='RdBu',
        zmid=0,
        text=np.round(correlation_matrix, 2),
        texttemplate="%{text}",
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title="Asset Correlation Matrix",
        xaxis_title="Assets",
        yaxis_title="Assets"
    )
    
    return fig

# Callback for efficient frontier
@app.callback(
    Output("efficient-frontier-chart", "figure"),
    [Input("optimize-button", "n_clicks"),
     Input("risk-aversion-slider", "value"),
     Input("target-return-slider", "value")]
)
def update_efficient_frontier(n_clicks, risk_aversion, target_return):
    """Update efficient frontier chart."""
    # Sample data for demonstration
    np.random.seed(42)
    n_assets = 8
    n_periods = 252
    
    # Generate sample returns
    returns_data = pd.DataFrame(
        np.random.normal(0.0005, 0.02, (n_periods, n_assets)),
        columns=['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    )
    
    # Calculate efficient frontier
    expected_returns = returns_data.mean().values
    cov_matrix = returns_data.cov().values
    
    # Generate efficient frontier
    min_ret = expected_returns.min()
    max_ret = expected_returns.max()
    target_returns = np.linspace(min_ret, max_ret, 50)
    
    returns_ef = []
    volatilities_ef = []
    
    for target_ret in target_returns:
        try:
            # Simple optimization (equal weights for demo)
            weights = np.ones(n_assets) / n_assets
            port_ret = np.dot(weights, expected_returns)
            port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            returns_ef.append(port_ret)
            volatilities_ef.append(port_vol)
        except:
            continue
    
    # Create efficient frontier plot
    fig = go.Figure()
    
    # Efficient frontier
    fig.add_trace(go.Scatter(
        x=volatilities_ef,
        y=returns_ef,
        mode='lines',
        name='Efficient Frontier',
        line=dict(color='blue', width=2)
    ))
    
    # Individual assets
    individual_vols = np.sqrt(np.diag(cov_matrix))
    fig.add_trace(go.Scatter(
        x=individual_vols,
        y=expected_returns,
        mode='markers+text',
        name='Individual Assets',
        text=returns_data.columns,
        textposition="top center",
        marker=dict(size=10, color='red')
    ))
    
    # Current portfolio (if optimized)
    if n_clicks and n_clicks > 0:
        try:
            weights = np.ones(n_assets) / n_assets
            port_ret = np.dot(weights, expected_returns)
            port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            fig.add_trace(go.Scatter(
                x=[port_vol],
                y=[port_ret],
                mode='markers',
                name='Optimized Portfolio',
                marker=dict(size=15, color='green', symbol='star')
            ))
        except:
            pass
    
    fig.update_layout(
        title="Efficient Frontier",
        xaxis_title="Volatility",
        yaxis_title="Expected Return",
        hovermode='closest'
    )
    
    return fig

# Callback for optimized weights
@app.callback(
    Output("optimized-weights-chart", "figure"),
    [Input("optimize-button", "n_clicks"),
     Input("target-return-slider", "value")]
)
def update_optimized_weights(n_clicks, target_return):
    """Update optimized portfolio weights chart."""
    if not n_clicks:
        return go.Figure()
    
    # Sample data
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    np.random.seed(42)
    weights = np.random.dirichlet(np.ones(len(assets)))
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=assets,
            y=weights,
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title="Optimized Portfolio Weights",
        xaxis_title="Assets",
        yaxis_title="Weight",
        yaxis=dict(tickformat='.1%')
    )
    
    return fig

# Callback for optimization results
@app.callback(
    Output("optimization-results", "children"),
    [Input("optimize-button", "n_clicks"),
     Input("target-return-slider", "value")]
)
def update_optimization_results(n_clicks, target_return):
    """Update optimization results display."""
    if not n_clicks:
        return html.Div()
    
    # Sample optimization results
    results = [
        {"label": "Expected Return", "value": f"{target_return:.1%}"},
        {"label": "Expected Volatility", "value": "15.2%"},
        {"label": "Sharpe Ratio", "value": "0.89"},
        {"label": "Portfolio Value", "value": "$125,430"},
        {"label": "Number of Assets", "value": "8"},
        {"label": "Rebalancing Cost", "value": "$125"}
    ]
    
    result_cards = []
    for result in results:
        result_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6(result["value"], className="text-primary"),
                    html.P(result["label"], className="mb-0 text-muted")
                ])
            ], className="mb-2")
        )
    
    return result_cards

# Callback for risk metrics chart
@app.callback(
    Output("risk-metrics-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_risk_metrics_chart(active_tab):
    """Update risk metrics over time chart."""
    if active_tab != "risk-tab":
        return go.Figure()
    
    # Generate sample risk metrics data
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='M')
    np.random.seed(42)
    
    # Generate realistic risk metrics
    sharpe_ratio = 0.5 + 0.3 * np.sin(np.arange(len(dates)) * 0.5) + np.random.normal(0, 0.1, len(dates))
    volatility = 0.15 + 0.05 * np.sin(np.arange(len(dates)) * 0.3) + np.random.normal(0, 0.02, len(dates))
    var_95 = -0.02 - 0.01 * np.sin(np.arange(len(dates)) * 0.4) + np.random.normal(0, 0.005, len(dates))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=sharpe_ratio,
        mode='lines+markers',
        name='Sharpe Ratio',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=volatility,
        mode='lines+markers',
        name='Volatility',
        line=dict(color='red', width=2),
        yaxis='y2'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=var_95,
        mode='lines+markers',
        name='VaR (95%)',
        line=dict(color='orange', width=2),
        yaxis='y3'
    ))
    
    fig.update_layout(
        title="Risk Metrics Over Time",
        xaxis_title="Date",
        yaxis=dict(title="Sharpe Ratio", side="left"),
        yaxis2=dict(title="Volatility", side="right", overlaying="y"),
        yaxis3=dict(title="VaR (95%)", side="right", overlaying="y", position=0.85),
        hovermode='x unified'
    )
    
    return fig

# Callback for risk summary
@app.callback(
    Output("risk-summary", "children"),
    [Input("tabs", "active_tab")]
)
def update_risk_summary(active_tab):
    """Update risk summary display."""
    if active_tab != "risk-tab":
        return html.Div()
    
    # Sample risk metrics
    risk_metrics = [
        {"label": "Current Sharpe Ratio", "value": "0.83", "color": "success"},
        {"label": "Portfolio Volatility", "value": "18.3%", "color": "warning"},
        {"label": "VaR (95%)", "value": "-2.1%", "color": "danger"},
        {"label": "VaR (99%)", "value": "-3.2%", "color": "danger"},
        {"label": "Max Drawdown", "value": "-8.7%", "color": "danger"},
        {"label": "Beta", "value": "1.12", "color": "info"}
    ]
    
    metric_cards = []
    for metric in risk_metrics:
        metric_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H5(metric["value"], className=f"text-{metric['color']}"),
                    html.P(metric["label"], className="mb-0")
                ])
            ], className="mb-2")
        )
    
    return metric_cards

# Callback for VaR chart
@app.callback(
    Output("var-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_var_chart(active_tab):
    """Update Value at Risk chart."""
    if active_tab != "risk-tab":
        return go.Figure()
    
    # Generate sample VaR data
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='W')
    np.random.seed(42)
    
    # Generate realistic VaR data
    var_95 = -0.02 + 0.01 * np.sin(np.arange(len(dates)) * 0.3) + np.random.normal(0, 0.005, len(dates))
    var_99 = -0.03 + 0.015 * np.sin(np.arange(len(dates)) * 0.3) + np.random.normal(0, 0.008, len(dates))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=var_95,
        mode='lines+markers',
        name='VaR (95%)',
        line=dict(color='red', width=2),
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=var_99,
        mode='lines+markers',
        name='VaR (99%)',
        line=dict(color='darkred', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title="Value at Risk Over Time",
        xaxis_title="Date",
        yaxis_title="VaR",
        yaxis=dict(tickformat='.1%'),
        hovermode='x unified'
    )
    
    return fig

# Callback for drawdown chart
@app.callback(
    Output("drawdown-chart", "figure"),
    [Input("tabs", "active_tab")]
)
def update_drawdown_chart(active_tab):
    """Update drawdown analysis chart."""
    if active_tab != "risk-tab":
        return go.Figure()
    
    # Generate sample drawdown data
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    np.random.seed(42)
    
    # Generate realistic drawdown data
    returns = np.random.normal(0.0005, 0.02, len(dates))
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=drawdown,
        mode='lines',
        name='Drawdown',
        line=dict(color='red', width=2),
        fill='tozeroy'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title="Portfolio Drawdown Analysis",
        xaxis_title="Date",
        yaxis_title="Drawdown",
        yaxis=dict(tickformat='.1%'),
        hovermode='x unified'
    )
    
    return fig

# Portfolio Management Callbacks

# Callback for portfolio weights display
@app.callback(
    Output("portfolio-weights-display", "children"),
    [Input("asset-selector", "value"),
     Input("portfolio-strategy", "value")]
)
def update_portfolio_weights(selected_assets, strategy):
    """Update portfolio weights display based on selected assets and strategy."""
    if not selected_assets:
        return html.Div("Select assets to see weights")
    
    # Calculate weights based on strategy
    n_assets = len(selected_assets)
    if strategy == "equal_weight":
        weights = [1.0/n_assets] * n_assets
    elif strategy == "market_cap":
        # Sample market cap weights (in real app, would fetch from API)
        market_caps = {"AAPL": 0.35, "GOOGL": 0.25, "MSFT": 0.20, "AMZN": 0.15, 
                      "TSLA": 0.10, "META": 0.08, "NVDA": 0.12, "NFLX": 0.05}
        total_cap = sum(market_caps.get(asset, 0.1) for asset in selected_assets)
        weights = [market_caps.get(asset, 0.1)/total_cap for asset in selected_assets]
    else:  # custom or risk_parity
        weights = [1.0/n_assets] * n_assets
    
    # Create weight display
    weight_items = []
    for asset, weight in zip(selected_assets, weights):
        weight_items.append(
            dbc.Row([
                dbc.Col(html.Strong(asset), width=4),
                dbc.Col(html.Span(f"{weight:.1%}"), width=4),
                dbc.Col(
                    dbc.Progress(value=weight*100, color="primary", className="mb-1"),
                    width=4
                )
            ], className="mb-2")
        )
    
    return weight_items

# Callback for portfolio summary
@app.callback(
    Output("portfolio-summary", "children"),
    [Input("asset-selector", "value"),
     Input("portfolio-value", "value"),
     Input("portfolio-strategy", "value")]
)
def update_portfolio_summary(selected_assets, portfolio_value, strategy):
    """Update portfolio summary."""
    if not selected_assets or not portfolio_value:
        return html.Div("Configure portfolio to see summary")
    
    n_assets = len(selected_assets)
    weight_per_asset = 1.0 / n_assets
    value_per_asset = portfolio_value * weight_per_asset
    
    # Sample metrics (in real app, would calculate from actual data)
    expected_return = 0.12
    volatility = 0.18
    sharpe_ratio = 0.67
    
    summary_cards = [
        dbc.Card([
            dbc.CardBody([
                html.H6(f"${portfolio_value:,.0f}", className="text-primary"),
                html.P("Total Value", className="mb-0 text-muted")
            ])
        ], className="mb-2"),
        dbc.Card([
            dbc.CardBody([
                html.H6(f"{n_assets}", className="text-info"),
                html.P("Assets", className="mb-0 text-muted")
            ])
        ], className="mb-2"),
        dbc.Card([
            dbc.CardBody([
                html.H6(f"{expected_return:.1%}", className="text-success"),
                html.P("Expected Return", className="mb-0 text-muted")
            ])
        ], className="mb-2"),
        dbc.Card([
            dbc.CardBody([
                html.H6(f"{volatility:.1%}", className="text-warning"),
                html.P("Volatility", className="mb-0 text-muted")
            ])
        ], className="mb-2"),
        dbc.Card([
            dbc.CardBody([
                html.H6(f"{sharpe_ratio:.2f}", className="text-info"),
                html.P("Sharpe Ratio", className="mb-0 text-muted")
            ])
        ], className="mb-2")
    ]
    
    return summary_cards

# Callback for portfolios list
@app.callback(
    Output("portfolios-list", "children"),
    [Input("tabs", "active_tab")],
    [dash.dependencies.State("portfolio-storage", "children")]
)
def update_portfolios_list(active_tab, stored_data):
    """Update the list of portfolios."""
    if active_tab != "portfolio-mgmt-tab":
        return html.Div()
    
    try:
        if DATABASE_AVAILABLE and PORTFOLIO_SERVICE:
            # Load portfolios from database
            db_portfolios = PORTFOLIO_SERVICE.get_all_portfolios()
            portfolios = []
            for p in db_portfolios:
                # Calculate real portfolio return
                portfolio_return = calculate_portfolio_return(
                    symbols=p["symbols"],
                    weights=p["weights"]
                )
                
                portfolios.append({
                    "id": p["id"],
                    "name": p["name"],
                    "description": p.get("description", ""),
                    "strategy": p["strategy"],
                    "assets": p["symbols"],
                    "value": 100000,  # Default value
                    "return": portfolio_return,
                    "created": p["created_at"][:10] if p.get("created_at") else datetime.now().strftime("%Y-%m-%d")
                })
        else:
            # Fallback to in-memory storage
            if stored_data:
                try:
                    portfolios = json.loads(stored_data)
                except:
                    portfolios = []
            else:
                # Default portfolios
                portfolios = [
                    {
                        "name": "Tech Growth Portfolio",
                        "strategy": "Equal Weight",
                        "assets": ["AAPL", "GOOGL", "MSFT", "NVDA"],
                        "value": 125000,
                        "return": 0.15,
                        "created": "2024-01-15"
                    },
                    {
                        "name": "Conservative Portfolio",
                        "strategy": "Market Cap",
                        "assets": ["AAPL", "MSFT", "GOOGL"],
                        "value": 85000,
                        "return": 0.08,
                        "created": "2024-02-01"
                    },
                    {
                        "name": "High Risk Portfolio",
                        "strategy": "Custom",
                        "assets": ["TSLA", "NVDA", "META"],
                        "value": 75000,
                        "return": 0.22,
                        "created": "2024-02-10"
                    }
                ]
    except Exception as e:
        print(f"Error loading portfolios: {e}")
        portfolios = []
    
    portfolio_cards = []
    for portfolio in portfolios:
        portfolio_cards.append(
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5(portfolio["name"], className="mb-1"),
                            html.P(f"Strategy: {portfolio['strategy']}", className="mb-1 text-muted"),
                            html.P(f"Assets: {', '.join(portfolio['assets'])}", className="mb-1 text-muted"),
                            html.P(f"Created: {portfolio['created']}", className="mb-0 text-muted")
                        ], width=8),
                        dbc.Col([
                            html.H6(f"${portfolio['value']:,.0f}", className="text-primary mb-1"),
                            html.P(f"Return: {format_return_display(portfolio['return'])}", 
                                  className=f"mb-0 text-{'success' if isinstance(portfolio['return'], (int, float)) and portfolio['return'] > 0.1 else 'warning'}"),
                            dbc.Button("Select", size="sm", color="outline-primary", 
                                     className="mt-2", id=f"select-{portfolio['name'].lower().replace(' ', '-')}")
                        ], width=4)
                    ])
                ])
            ], className="mb-3")
        )
    
    return portfolio_cards

# Callback for portfolio selector dropdown
@app.callback(
    Output("portfolio-selector", "options"),
    [Input("tabs", "active_tab")],
    [dash.dependencies.State("portfolio-storage", "children")]
)
def update_portfolio_selector(active_tab, stored_data):
    """Update portfolio selector dropdown options."""
    if active_tab != "portfolio-mgmt-tab":
        return []
    
    try:
        if DATABASE_AVAILABLE and PORTFOLIO_SERVICE:
            # Load portfolios from database
            db_portfolios = PORTFOLIO_SERVICE.get_all_portfolios()
            portfolios = []
            for p in db_portfolios:
                # Calculate real portfolio return
                portfolio_return = calculate_portfolio_return(
                    symbols=p["symbols"],
                    weights=p["weights"]
                )
                
                portfolios.append({
                    "name": p["name"],
                    "strategy": p["strategy"],
                    "assets": p["symbols"],
                    "value": 100000,
                    "return": portfolio_return,
                    "created": p["created_at"][:10] if p.get("created_at") else datetime.now().strftime("%Y-%m-%d")
                })
        else:
            # Fallback to in-memory storage
            if stored_data:
                try:
                    portfolios = json.loads(stored_data)
                except:
                    portfolios = []
            else:
                # Default portfolios
                portfolios = [
                    {
                        "name": "Tech Growth Portfolio",
                        "strategy": "Equal Weight",
                        "assets": ["AAPL", "GOOGL", "MSFT", "NVDA"],
                        "value": 125000,
                        "return": 0.15,
                        "created": "2024-01-15"
                    },
                    {
                        "name": "Conservative Portfolio",
                        "strategy": "Market Cap",
                        "assets": ["AAPL", "MSFT", "GOOGL"],
                        "value": 85000,
                        "return": 0.08,
                        "created": "2024-02-01"
                    },
                    {
                        "name": "High Risk Portfolio",
                        "strategy": "Custom",
                        "assets": ["TSLA", "NVDA", "META"],
                        "value": 75000,
                        "return": 0.22,
                        "created": "2024-02-10"
                    }
                ]
    except Exception as e:
        print(f"Error loading portfolios for selector: {e}")
        portfolios = []
    
    # Create dropdown options
    options = []
    for portfolio in portfolios:
        options.append({
            "label": f"{portfolio['name']} ({portfolio['strategy']})",
            "value": portfolio['name']
        })
    
    return options

# Callback for portfolio action buttons
@app.callback(
    [Output("portfolio-name", "value", allow_duplicate=True),
     Output("portfolio-description", "value", allow_duplicate=True),
     Output("asset-selector", "value", allow_duplicate=True),
     Output("portfolio-value", "value", allow_duplicate=True),
     Output("portfolio-strategy", "value", allow_duplicate=True)],
    [Input("edit-portfolio-btn", "n_clicks"),
     Input("clone-portfolio-btn", "n_clicks")],
    [dash.dependencies.State("portfolio-selector", "value"),
     dash.dependencies.State("portfolio-storage", "children")],
    prevent_initial_call=True
)
def handle_portfolio_actions(edit_clicks, clone_clicks, selected_portfolio, stored_data):
    """Handle portfolio action buttons."""
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update, no_update
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if not selected_portfolio:
        return no_update, no_update, no_update, no_update, no_update
    
    # Load portfolios from storage
    if stored_data:
        try:
            import json
            portfolios = json.loads(stored_data)
        except:
            portfolios = []
    else:
        # Use default portfolios if no stored data
        portfolios = [
            {
                "name": "Tech Growth Portfolio",
                "strategy": "Equal Weight",
                "assets": ["AAPL", "GOOGL", "MSFT", "NVDA"],
                "value": 125000,
                "return": 0.15,
                "created": "2024-01-15"
            },
            {
                "name": "Conservative Portfolio",
                "strategy": "Market Cap",
                "assets": ["AAPL", "MSFT", "GOOGL"],
                "value": 85000,
                "return": 0.08,
                "created": "2024-02-01"
            },
            {
                "name": "High Risk Portfolio",
                "strategy": "Custom",
                "assets": ["TSLA", "NVDA", "META"],
                "value": 75000,
                "return": 0.22,
                "created": "2024-02-10"
            }
        ]
    
    # Find the selected portfolio
    selected_portfolio_data = None
    for portfolio in portfolios:
        if portfolio["name"] == selected_portfolio:
            selected_portfolio_data = portfolio
            break
    
    if not selected_portfolio_data:
        return no_update, no_update, no_update, no_update, no_update
    
    if button_id == "edit-portfolio-btn":
        # Fill form with selected portfolio data
        return (selected_portfolio_data["name"],
                selected_portfolio_data.get("description", ""),
                selected_portfolio_data["assets"],
                selected_portfolio_data["value"],
                selected_portfolio_data["strategy"].lower().replace(" ", "_"))
    
    elif button_id == "clone-portfolio-btn":
        # Fill form with selected portfolio data for cloning
        return (f"{selected_portfolio_data['name']} (Copy)",
                selected_portfolio_data.get("description", ""),
                selected_portfolio_data["assets"],
                selected_portfolio_data["value"],
                selected_portfolio_data["strategy"].lower().replace(" ", "_"))
    
    return no_update, no_update, no_update, no_update, no_update

# Callback to show/hide Update button when editing
@app.callback(
    [Output("create-portfolio-btn", "style"),
     Output("update-portfolio-btn", "style")],
    [Input("edit-portfolio-btn", "n_clicks"),
     Input("clear-portfolio-btn", "n_clicks")],
    prevent_initial_call=True
)
def toggle_update_button(edit_clicks, clear_clicks):
    """Show Update button when editing, hide when clearing."""
    ctx = callback_context
    if not ctx.triggered:
        return {"display": "inline-block"}, {"display": "none"}
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "edit-portfolio-btn":
        # Show Update button, hide Create button
        return {"display": "none"}, {"display": "inline-block"}
    elif button_id == "clear-portfolio-btn":
        # Show Create button, hide Update button
        return {"display": "inline-block"}, {"display": "none"}
    
    return {"display": "inline-block"}, {"display": "none"}

# Callback for other portfolio action buttons (View Details, Delete, Export)
@app.callback(
    Output("portfolio-actions-feedback", "children"),
    [Input("view-portfolio-btn", "n_clicks"),
     Input("delete-portfolio-btn", "n_clicks"),
     Input("export-portfolio-btn", "n_clicks")],
    [dash.dependencies.State("portfolio-selector", "value"),
     dash.dependencies.State("portfolio-storage", "children")],
    prevent_initial_call=True
)
def handle_other_portfolio_actions(view_clicks, delete_clicks, export_clicks, selected_portfolio, stored_data):
    """Handle other portfolio action buttons."""
    ctx = callback_context
    if not ctx.triggered:
        return ""
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if not selected_portfolio:
        return dbc.Alert("Please select a portfolio first.", color="warning", dismissable=True)
    
    # Load portfolios from storage
    if stored_data:
        try:
            import json
            portfolios = json.loads(stored_data)
        except:
            portfolios = []
    else:
        # Use default portfolios if no stored data
        portfolios = [
            {
                "name": "Tech Growth Portfolio",
                "strategy": "Equal Weight",
                "assets": ["AAPL", "GOOGL", "MSFT", "NVDA"],
                "value": 125000,
                "return": 0.15,
                "created": "2024-01-15"
            },
            {
                "name": "Conservative Portfolio",
                "strategy": "Market Cap",
                "assets": ["AAPL", "MSFT", "GOOGL"],
                "value": 85000,
                "return": 0.08,
                "created": "2024-02-01"
            },
            {
                "name": "High Risk Portfolio",
                "strategy": "Custom",
                "assets": ["TSLA", "NVDA", "META"],
                "value": 75000,
                "return": 0.22,
                "created": "2024-02-10"
            }
        ]
    
    # Find the selected portfolio
    selected_portfolio_data = None
    for portfolio in portfolios:
        if portfolio["name"] == selected_portfolio:
            selected_portfolio_data = portfolio
            break
    
    if not selected_portfolio_data:
        return dbc.Alert("Portfolio not found.", color="danger", dismissable=True)
    
    if button_id == "view-portfolio-btn":
        # Show portfolio details
        details = dbc.Card([
            dbc.CardHeader("Portfolio Details"),
            dbc.CardBody([
                html.H5(selected_portfolio_data["name"]),
                html.P(f"Strategy: {selected_portfolio_data['strategy']}"),
                html.P(f"Assets: {', '.join(selected_portfolio_data['assets'])}"),
                html.P(f"Value: ${selected_portfolio_data['value']:,.0f}"),
                html.P(f"Return: {format_return_display(selected_portfolio_data['return'])}"),
                html.P(f"Created: {selected_portfolio_data['created']}")
            ])
        ])
        return details
    
    elif button_id == "delete-portfolio-btn":
        # For now, just show a message (in real app, would delete from storage)
        return dbc.Alert(f"Delete functionality for '{selected_portfolio}' would be implemented here.", color="info", dismissable=True)
    
    elif button_id == "export-portfolio-btn":
        # For now, just show a message (in real app, would export to file)
        return dbc.Alert(f"Export functionality for '{selected_portfolio}' would be implemented here.", color="info", dismissable=True)
    
    return ""

# Callback to handle custom strategy UI
@app.callback(
    [Output("custom-amounts-container", "children"),
     Output("custom-amounts-container", "style"),
     Output("portfolio-value", "readonly"),
     Output("portfolio-value", "style")],
    [Input("portfolio-strategy", "value"),
     Input("asset-selector", "value")],
    prevent_initial_call=False
)
def handle_custom_strategy(strategy, selected_assets):
    """Handle custom strategy UI - show individual stock amounts."""
    if strategy == "custom" and selected_assets:
        # Create individual amount inputs for each selected asset
        amount_inputs = []
        for i, asset in enumerate(selected_assets):
            amount_inputs.append(
                dbc.Row([
                    dbc.Col([
                        html.Label(f"{asset} Amount ($):"),
                        dbc.Input(
                            id={"type": "amount-input", "index": asset},
                            type="number",
                            value=0,
                            min=0,
                            step=100
                        )
                    ], width=6)
                ], className="mb-2")
            )
        
        return amount_inputs, {"display": "block"}, True, {"backgroundColor": "#f8f9fa", "color": "#6c757d"}
    else:
        return [], {"display": "none"}, False, {}

# Callback to calculate total portfolio value for custom strategy
@app.callback(
    Output("portfolio-value", "value"),
    [Input("portfolio-strategy", "value"),
     Input("asset-selector", "value")],
    [dash.dependencies.State({"type": "amount-input", "index": dash.dependencies.ALL}, "value")],
    prevent_initial_call=False
)
def calculate_custom_portfolio_value(strategy, selected_assets, amount_values):
    """Calculate total portfolio value for custom strategy."""
    if strategy == "custom" and selected_assets:
        # Sum all amount values
        total = sum(amount for amount in amount_values if amount is not None)
        return total
    else:
        return 100000  # Default value for non-custom strategies

# Pattern matching callback to handle dynamic amount inputs
@app.callback(
    Output("portfolio-value", "value", allow_duplicate=True),
    [Input({"type": "amount-input", "index": dash.dependencies.ALL}, "value")],
    [dash.dependencies.State("portfolio-strategy", "value"),
     dash.dependencies.State("asset-selector", "value")],
    prevent_initial_call=True
)
def update_portfolio_value_on_amount_change(amount_values, strategy, selected_assets):
    """Update portfolio value when individual amounts change using pattern matching."""
    if strategy == "custom" and selected_assets:
        # Sum all amount values
        total = sum(amount for amount in amount_values if amount is not None)
        return total
    else:
        return 100000  # Default value for non-custom strategies

# Callback for update portfolio button
@app.callback(
    [Output("portfolios-list", "children", allow_duplicate=True),
     Output("portfolio-storage", "children", allow_duplicate=True),
     Output("portfolio-selector", "options", allow_duplicate=True),
     Output("create-portfolio-btn", "style", allow_duplicate=True),
     Output("update-portfolio-btn", "style", allow_duplicate=True),
     Output("portfolio-name", "value", allow_duplicate=True),
     Output("portfolio-description", "value", allow_duplicate=True),
     Output("asset-selector", "value", allow_duplicate=True),
     Output("portfolio-value", "value", allow_duplicate=True),
     Output("portfolio-strategy", "value", allow_duplicate=True)],
    [Input("update-portfolio-btn", "n_clicks")],
    [dash.dependencies.State("portfolio-name", "value"),
     dash.dependencies.State("portfolio-description", "value"),
     dash.dependencies.State("asset-selector", "value"),
     dash.dependencies.State("portfolio-value", "value"),
     dash.dependencies.State("portfolio-strategy", "value"),
     dash.dependencies.State("portfolio-selector", "value"),
     dash.dependencies.State("portfolio-storage", "children")],
    prevent_initial_call=True
)
def update_portfolio(n_clicks, name, description, assets, value, strategy, selected_portfolio, stored_data):
    """Update an existing portfolio."""
    if not n_clicks or not name or not assets or not selected_portfolio:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    try:
        if DATABASE_AVAILABLE and PORTFOLIO_SERVICE:
            # Update portfolio in database
            # First, get all portfolios to find the one to update
            db_portfolios = PORTFOLIO_SERVICE.get_all_portfolios()
            portfolio_to_update = None
            
            for p in db_portfolios:
                if p["name"] == selected_portfolio:
                    portfolio_to_update = p
                    break
            
            if portfolio_to_update:
                # Calculate weights based on strategy
                if strategy == "equal_weight":
                    weights = [1.0 / len(assets)] * len(assets)
                elif strategy == "market_cap":
                    # Simplified market cap weights (in real app, would fetch actual market caps)
                    weights = [0.4, 0.3, 0.2, 0.1][:len(assets)] if len(assets) >= 4 else [1.0 / len(assets)] * len(assets)
                elif strategy == "risk_parity":
                    # Simplified risk parity weights
                    weights = [0.25, 0.25, 0.25, 0.25][:len(assets)] if len(assets) >= 4 else [1.0 / len(assets)] * len(assets)
                else:  # custom
                    weights = [1.0 / len(assets)] * len(assets)
                
                # Update the portfolio in database
                updated_portfolio = PORTFOLIO_SERVICE.update_portfolio(
                    portfolio_id=portfolio_to_update["id"],
                    name=name,
                    description=description or f"Updated {name} portfolio",
                    symbols=assets,
                    weights=weights,
                    strategy=strategy.replace("_", " ").title()
                )
                
                if updated_portfolio:
                    # Reload all portfolios from database
                    db_portfolios = PORTFOLIO_SERVICE.get_all_portfolios()
                    portfolios = []
                    for p in db_portfolios:
                        portfolio_return = calculate_portfolio_return(
                            symbols=p["symbols"],
                            weights=p["weights"]
                        )
                        portfolios.append({
                            "name": p["name"],
                            "strategy": p["strategy"],
                            "assets": p["symbols"],
                            "value": value or 100000,
                            "return": portfolio_return,
                            "created": p["created_at"][:10] if p["created_at"] else datetime.now().strftime("%Y-%m-%d")
                        })
                else:
                    # Fallback to in-memory update if database update fails
                    portfolios = []
            else:
                # Portfolio not found in database, fallback to in-memory
                portfolios = []
        else:
            # Database not available, fallback to in-memory storage
            portfolios = []
            
    except Exception as e:
        print(f"Error updating portfolio in database: {e}")
        # Fallback to in-memory storage
        portfolios = []
    
    # Fallback to in-memory storage if database operations failed
    if not portfolios:
        # Load portfolios from storage
        if stored_data:
            try:
                import json
                portfolios = json.loads(stored_data)
            except:
                portfolios = []
        else:
            # Use default portfolios if no stored data
            portfolios = [
                {
                    "name": "Tech Growth Portfolio",
                    "strategy": "Equal Weight",
                    "assets": ["AAPL", "GOOGL", "MSFT", "NVDA"],
                    "value": 125000,
                    "return": 0.15,
                    "created": "2024-01-15"
                },
                {
                    "name": "Conservative Portfolio",
                    "strategy": "Market Cap",
                    "assets": ["AAPL", "MSFT", "GOOGL"],
                    "value": 85000,
                    "return": 0.08,
                    "created": "2024-02-01"
                },
                {
                    "name": "High Risk Portfolio",
                    "strategy": "Custom",
                    "assets": ["TSLA", "NVDA", "META"],
                    "value": 75000,
                    "return": 0.22,
                    "created": "2024-02-10"
                }
            ]
        
        # Find and update the selected portfolio
        for i, portfolio in enumerate(portfolios):
            if portfolio["name"] == selected_portfolio:
                portfolios[i] = {
                    "name": name,
                    "strategy": strategy.replace("_", " ").title(),
                    "assets": assets,
                    "value": value or 100000,
                    "return": portfolio.get("return", "Data Unavailable"),
                    "created": portfolio.get("created", datetime.now().strftime("%Y-%m-%d"))
                }
                break
    
    # Create portfolio cards
    portfolio_cards = []
    for portfolio in portfolios:
        portfolio_cards.append(
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5(portfolio["name"], className="mb-1"),
                            html.P(f"Strategy: {portfolio['strategy']}", className="mb-1 text-muted"),
                            html.P(f"Assets: {', '.join(portfolio['assets'])}", className="mb-1 text-muted"),
                            html.P(f"Created: {portfolio['created']}", className="mb-0 text-muted")
                        ], width=8),
                        dbc.Col([
                            html.H6(f"${portfolio['value']:,.0f}", className="text-primary mb-1"),
                            html.P(f"Return: {format_return_display(portfolio['return'])}", 
                                  className=f"mb-0 text-{'success' if isinstance(portfolio['return'], (int, float)) and portfolio['return'] > 0.1 else 'warning'}"),
                            dbc.Button("Select", size="sm", color="outline-primary", 
                                     className="mt-2", id=f"select-{portfolio['name'].lower().replace(' ', '-')}")
                        ], width=4)
                    ])
                ])
            ], className="mb-3")
        )
    
    # Store updated portfolios data (for fallback scenarios)
    import json
    stored_portfolios = json.dumps(portfolios)
    
    # Create dropdown options
    dropdown_options = []
    for portfolio in portfolios:
        dropdown_options.append({
            "label": f"{portfolio['name']} ({portfolio['strategy']})",
            "value": portfolio['name']
        })
    
    # Show Create button, hide Update button, and clear form
    return (portfolio_cards, stored_portfolios, dropdown_options, 
            {"display": "inline-block"}, {"display": "none"},
            "", "", [], 100000, "equal_weight")

# Callback for auto-allocate button (only affects asset selector)
@app.callback(
    Output("asset-selector", "value"),
    [Input("auto-allocate-btn", "n_clicks"),
     Input("portfolio-strategy", "value")],
    prevent_initial_call=True
)
def auto_allocate_assets(auto_allocate_clicks, strategy):
    """Auto-allocate assets based on strategy."""
    if not auto_allocate_clicks:
        return ["AAPL", "GOOGL", "MSFT"]  # Default selection
    
    if strategy == "equal_weight":
        return ["AAPL", "GOOGL", "MSFT", "AMZN"]
    elif strategy == "market_cap":
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    elif strategy == "risk_parity":
        return ["AAPL", "GOOGL", "MSFT", "NVDA"]
    else:  # custom
        return ["AAPL", "GOOGL", "MSFT"]

# Callback for clear portfolio button
@app.callback(
    [Output("portfolio-name", "value"),
     Output("portfolio-description", "value"),
     Output("asset-selector", "value", allow_duplicate=True),
     Output("portfolio-value", "value", allow_duplicate=True),
     Output("portfolio-strategy", "value", allow_duplicate=True)],
    [Input("clear-portfolio-btn", "n_clicks")],
    prevent_initial_call=True
)
def clear_portfolio_form(clear_clicks):
    """Clear the portfolio creation form."""
    if clear_clicks:
        return "", "", [], 100000, "equal_weight"
    return "", "", ["AAPL", "GOOGL", "MSFT"], 100000, "equal_weight"

# Callback for create portfolio button
@app.callback(
    [Output("portfolios-list", "children", allow_duplicate=True),
     Output("portfolio-storage", "children"),
     Output("portfolio-selector", "options", allow_duplicate=True)],
    [Input("create-portfolio-btn", "n_clicks")],
    [dash.dependencies.State("portfolio-name", "value"),
     dash.dependencies.State("portfolio-description", "value"),
     dash.dependencies.State("asset-selector", "value"),
     dash.dependencies.State("portfolio-value", "value"),
     dash.dependencies.State("portfolio-strategy", "value"),
     dash.dependencies.State("portfolio-storage", "children")],
    prevent_initial_call=True
)
def create_portfolio(n_clicks, name, description, assets, value, strategy, stored_data):
    """Create a new portfolio."""
    if not n_clicks or not name or not assets:
        return no_update, no_update, no_update
    
    try:
        if DATABASE_AVAILABLE and PORTFOLIO_SERVICE:
            # Calculate weights for custom strategy
            if strategy == "custom" and value and value > 0:
                # For custom strategy, we need to get individual amounts from the form
                # This is a simplified approach - in a real app, you'd pass the individual amounts
                weights = [1.0 / len(assets)] * len(assets)  # Equal weights as fallback
            else:
                # For other strategies, use equal weights
                weights = [1.0 / len(assets)] * len(assets)
            
            # Save to database
            portfolio_data = PORTFOLIO_SERVICE.create_portfolio(
                name=name,
                description=description or "",
                symbols=assets,
                weights=weights,
                strategy=strategy.replace("_", " ").title()
            )
            
            # Load all portfolios from database
            db_portfolios = PORTFOLIO_SERVICE.get_all_portfolios()
            existing_portfolios = []
            for p in db_portfolios:
                # Calculate real portfolio return
                portfolio_return = calculate_portfolio_return(
                    symbols=p["symbols"],
                    weights=p["weights"]
                )
                
                existing_portfolios.append({
                    "id": p["id"],
                    "name": p["name"],
                    "description": p.get("description", ""),
                    "strategy": p["strategy"],
                    "assets": p["symbols"],
                    "value": value or 100000,
                    "return": portfolio_return,
                    "created": p["created_at"][:10] if p.get("created_at") else datetime.now().strftime("%Y-%m-%d")
                })
        else:
            # Fallback to in-memory storage
            if stored_data:
                try:
                    existing_portfolios = json.loads(stored_data)
                except:
                    existing_portfolios = []
            else:
                existing_portfolios = []
            
            # Calculate real return for new portfolio
            portfolio_return = calculate_portfolio_return(
                symbols=assets,
                weights=weights
            )
            
            # Create new portfolio data
            new_portfolio = {
                "name": name,
                "strategy": strategy.replace("_", " ").title(),
                "assets": assets,
                "value": value or 100000,
                "return": portfolio_return,
                "created": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add new portfolio to the list
            existing_portfolios.insert(0, new_portfolio)
    except Exception as e:
        print(f"Error creating portfolio: {e}")
        return no_update, no_update, no_update
    
    # Create portfolio cards
    portfolio_cards = []
    for portfolio in existing_portfolios:
        portfolio_cards.append(
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5(portfolio["name"], className="mb-1"),
                            html.P(f"Strategy: {portfolio['strategy']}", className="mb-1 text-muted"),
                            html.P(f"Assets: {', '.join(portfolio['assets'])}", className="mb-1 text-muted"),
                            html.P(f"Created: {portfolio['created']}", className="mb-0 text-muted")
                        ], width=8),
                        dbc.Col([
                            html.H6(f"${portfolio['value']:,.0f}", className="text-primary mb-1"),
                            html.P(f"Return: {format_return_display(portfolio['return'])}", 
                                  className=f"mb-0 text-{'success' if isinstance(portfolio['return'], (int, float)) and portfolio['return'] > 0.1 else 'warning'}"),
                            dbc.Button("Select", size="sm", color="outline-primary", 
                                     className="mt-2", id=f"select-{portfolio['name'].lower().replace(' ', '-')}")
                        ], width=4)
                    ])
                ])
            ], className="mb-3")
        )
    
    # Store updated portfolios data
    import json
    stored_portfolios = json.dumps(existing_portfolios)
    
    # Create dropdown options
    dropdown_options = []
    for portfolio in existing_portfolios:
        dropdown_options.append({
            "label": f"{portfolio['name']} ({portfolio['strategy']})",
            "value": portfolio['name']
        })
    
    return portfolio_cards, stored_portfolios, dropdown_options

if __name__ == "__main__":
    print("Starting Quantitative Finance Pipeline Dashboard...")
    print("Dashboard will be available at: http://localhost:8050")
    print("Press Ctrl+C to stop the server")
    app.run_server(debug=True, host='0.0.0.0', port=8050)
