"""
Main Dash application for portfolio visualization and analysis.
"""
import dash
from dash import dcc, html, Input, Output, callback_context
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
from typing import Dict, List, Optional
import logging

# Import our custom modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_CONFIG, DATA_SOURCES
from etl.loaders.database_loader import DatabaseLoader
from analytics.portfolio_optimization.optimizer import PortfolioOptimizer
from analytics.risk_metrics.calculator import RiskCalculator

logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Quantitative Finance Pipeline Dashboard"

# Initialize components
try:
    db_loader = DatabaseLoader(DATABASE_CONFIG["url"])
    portfolio_optimizer = PortfolioOptimizer()
    risk_calculator = RiskCalculator()
except Exception as e:
    logger.error(f"Error initializing components: {str(e)}")
    db_loader = None
    portfolio_optimizer = None
    risk_calculator = None

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
                dbc.Tab(label="Risk Analysis", tab_id="risk-tab"),
                dbc.Tab(label="Performance Metrics", tab_id="performance-tab"),
                dbc.Tab(label="Correlation Analysis", tab_id="correlation-tab"),
                dbc.Tab(label="Optimization", tab_id="optimization-tab"),
            ], id="tabs", active_tab="portfolio-tab")
        ])
    ], className="mb-4"),
    
    # Tab content
    html.Div(id="tab-content"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Quantitative Finance Pipeline Dashboard", 
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
    if active_tab != "portfolio-tab" or db_loader is None:
        return go.Figure()
    
    try:
        # Get portfolio data from database
        query = """
            SELECT date, symbol, value as portfolio_value 
            FROM portfolio_data 
            WHERE portfolio_name = 'main_portfolio'
            ORDER BY date
        """
        data = db_loader.query_data(query)
        
        if data.empty:
            # Create sample data if no real data
            dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
            portfolio_values = 10000 * (1 + np.random.normal(0.0005, 0.02, len(dates))).cumprod()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=portfolio_values,
                mode='lines',
                name='Portfolio Value',
                line=dict(color='blue', width=2)
            ))
        else:
            # Use real data
            portfolio_data = data.pivot(index='date', columns='symbol', values='portfolio_value')
            portfolio_total = portfolio_data.sum(axis=1)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=portfolio_total.index,
                y=portfolio_total.values,
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
        
    except Exception as e:
        logger.error(f"Error updating portfolio performance chart: {str(e)}")
        return go.Figure()

# Callback for key metrics
@app.callback(
    Output("key-metrics", "children"),
    [Input("tabs", "active_tab")]
)
def update_key_metrics(active_tab):
    """Update key metrics display."""
    if active_tab != "portfolio-tab":
        return html.Div()
    
    # Sample metrics - in real implementation, these would come from database
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
    if portfolio_optimizer is None:
        return go.Figure()
    
    try:
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
                weights, port_ret, port_vol = portfolio_optimizer.markowitz_optimization(
                    expected_returns, cov_matrix, target_return=target_ret
                )
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
                weights, port_ret, port_vol = portfolio_optimizer.markowitz_optimization(
                    expected_returns, cov_matrix, target_return=target_return
                )
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
        
    except Exception as e:
        logger.error(f"Error updating efficient frontier: {str(e)}")
        return go.Figure()

# Callback for optimized weights
@app.callback(
    Output("optimized-weights-chart", "figure"),
    [Input("optimize-button", "n_clicks"),
     Input("target-return-slider", "value")]
)
def update_optimized_weights(n_clicks, target_return):
    """Update optimized portfolio weights chart."""
    if not n_clicks or portfolio_optimizer is None:
        return go.Figure()
    
    try:
        # Sample data
        np.random.seed(42)
        n_assets = 8
        n_periods = 252
        
        returns_data = pd.DataFrame(
            np.random.normal(0.0005, 0.02, (n_periods, n_assets)),
            columns=['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
        )
        
        # Optimize portfolio
        expected_returns = returns_data.mean().values
        cov_matrix = returns_data.cov().values
        
        weights, port_ret, port_vol = portfolio_optimizer.markowitz_optimization(
            expected_returns, cov_matrix, target_return=target_return
        )
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=returns_data.columns,
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
        
    except Exception as e:
        logger.error(f"Error updating optimized weights: {str(e)}")
        return go.Figure()

# Callback for optimization results
@app.callback(
    Output("optimization-results", "children"),
    [Input("optimize-button", "n_clicks"),
     Input("target-return-slider", "value")]
)
def update_optimization_results(n_clicks, target_return):
    """Update optimization results display."""
    if not n_clicks or portfolio_optimizer is None:
        return html.Div()
    
    try:
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
        
    except Exception as e:
        logger.error(f"Error updating optimization results: {str(e)}")
        return html.Div()

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)
