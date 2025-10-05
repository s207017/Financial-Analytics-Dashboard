"""
Callback functions for the dashboard application.
"""
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from dash import Input, Output, callback_context, no_update
import dash_bootstrap_components as dbc
from dash import html

from .utils import (
    DatabaseManager, PortfolioCalculator, ValidationHelper, 
    ChartHelper, DateHelper, ErrorHandler, ensure_pandas_series
)
from .config import (
    RISK_METRICS, DEFAULT_RISK_METRIC, ROLLING_WINDOW_DAYS,
    CHART_HEIGHT, CHART_HEIGHT_SMALL, ERROR_MESSAGES,
    LOADING_MESSAGES, SUCCESS_MESSAGES
)


class CallbackManager:
    """Manages all dashboard callbacks."""
    
    def __init__(self, app, db_manager: DatabaseManager):
        self.app = app
        self.db_manager = db_manager
        self._register_callbacks()
    
    def _register_callbacks(self):
        """Register all callback functions."""
        self._register_tab_callbacks()
        self._register_portfolio_callbacks()
        self._register_risk_callbacks()
        self._register_performance_callbacks()
    
    def _register_tab_callbacks(self):
        """Register tab-related callbacks."""
        
        @self.app.callback(
            Output("tab-content", "children"),
            [Input("tabs", "active_tab")]
        )
        def render_tab_content(active_tab: str):
            """Render content based on active tab."""
            from .layouts import (
                create_portfolio_overview, create_portfolio_management,
                create_risk_analysis, create_performance_metrics
            )
            
            if active_tab == "portfolio-tab":
                return create_portfolio_overview()
            elif active_tab == "portfolio-mgmt-tab":
                return create_portfolio_management()
            elif active_tab == "risk-tab":
                return create_risk_analysis()
            elif active_tab == "performance-tab":
                return create_performance_metrics()
            else:
                return html.Div("Select a tab to view content")
    
    def _register_portfolio_callbacks(self):
        """Register portfolio-related callbacks."""
        
        @self.app.callback(
            Output("portfolios-list", "children"),
            [Input("tabs", "active_tab")]
        )
        def update_portfolios_list(active_tab: str):
            """Update portfolios list when tab changes."""
            if active_tab != "portfolio-mgmt-tab":
                return html.Div()
            
            portfolios = self.db_manager.get_all_portfolios()
            if not portfolios:
                return dbc.Alert("No portfolios found. Create your first portfolio!", 
                               color="info")
            
            portfolio_cards = []
            for portfolio in portfolios:
                return_value = PortfolioCalculator.calculate_portfolio_return(
                    portfolio["symbols"], portfolio["weights"], db_manager=self.db_manager
                )
                formatted_return = PortfolioCalculator.format_return_display(return_value)
                formatted_assets = PortfolioCalculator.format_assets_with_percentages(portfolio)
                
                card = dbc.Card([
                    dbc.CardBody([
                        html.H5(portfolio["name"], className="card-title"),
                        html.P(f"Strategy: {portfolio.get('strategy', 'N/A')}", 
                              className="card-text"),
                        html.P(f"Assets: {formatted_assets}", className="card-text"),
                        html.P(f"Return: {formatted_return}", className="card-text"),
                        html.Small(f"Created: {portfolio.get('created_at', 'N/A')}", 
                                 className="text-muted")
                    ])
                ], className="mb-3")
                portfolio_cards.append(card)
            
            return portfolio_cards
        
        @self.app.callback(
            [Output("asset-selector", "options"),
             Output("asset-selector", "value", allow_duplicate=True),
             Output("custom-symbol-input", "value")],
            [Input("add-symbol-btn", "n_clicks"),
             Input("custom-symbol-input", "value")],
            [Input("asset-selector", "options"),
             Input("asset-selector", "value")],
            prevent_initial_call=True
        )
        def add_custom_symbol(n_clicks: int, custom_symbol: str, 
                            current_options: List[Dict], current_values: List[str]):
            """Add custom symbol to asset selector."""
            if not n_clicks or not custom_symbol:
                return no_update, no_update, no_update
            
            symbol = custom_symbol.strip().upper()
            valid_symbols, invalid_symbols = ValidationHelper.validate_stock_symbols([symbol])
            
            if not valid_symbols:
                return no_update, no_update, ""
            
            new_symbol = valid_symbols[0]
            current_options = current_options or []
            current_values = current_values or []
            
            # Add to options if not already present
            if not any(opt["value"] == new_symbol for opt in current_options):
                current_options.append({"label": new_symbol, "value": new_symbol})
            
            # Add to values if not already selected
            if new_symbol not in current_values:
                current_values.append(new_symbol)
            
            return current_options, current_values, ""
    
    def _register_risk_callbacks(self):
        """Register risk analysis callbacks."""
        
        @self.app.callback(
            Output("risk-portfolio-selector", "options"),
            [Input("tabs", "active_tab")]
        )
        def update_risk_portfolio_selector(active_tab: str):
            """Update risk portfolio selector options."""
            if active_tab != "risk-tab":
                return []
            
            portfolios = self.db_manager.get_all_portfolios()
            options = []
            for portfolio in portfolios:
                options.append({
                    "label": f"{portfolio['name']} ({portfolio.get('strategy', 'N/A')})",
                    "value": portfolio['name']
                })
            return options
        
        @self.app.callback(
            Output("risk-metrics-chart", "figure"),
            [Input("tabs", "active_tab"),
             Input("risk-portfolio-selector", "value"),
             Input("risk-metric-selector", "value")],
            prevent_initial_call=True
        )
        def update_risk_metrics_chart(active_tab: str, selected_portfolios: List[str], 
                                    selected_metric: str):
            """Update risk metrics chart."""
            if active_tab != "risk-tab":
                return ChartHelper.create_empty_figure()
            
            if not selected_portfolios:
                return ChartHelper.create_empty_figure("Please select portfolios to analyze risk metrics")
            
            if not selected_metric:
                return ChartHelper.create_empty_figure("Please select a risk metric to display")
            
            fig = go.Figure()
            portfolios = self.db_manager.get_all_portfolios()
            portfolios_to_analyze = [p for p in portfolios if p['name'] in selected_portfolios]
            
            if not portfolios_to_analyze:
                return ChartHelper.create_empty_figure("No valid portfolios selected")
            
            start_date, end_date = DateHelper.get_analysis_date_range()
            
            for i, portfolio in enumerate(portfolios_to_analyze):
                try:
                    analytics = self.db_manager.calculate_portfolio_analytics(
                        portfolio['symbols'], portfolio['weights'], start_date, end_date
                    )
                    
                    if analytics and 'returns' in analytics:
                        returns = ensure_pandas_series(analytics['returns'])
                        
                        # Calculate rolling metrics
                        rolling_sharpe = returns.rolling(window=ROLLING_WINDOW_DAYS).mean() / \
                                       returns.rolling(window=ROLLING_WINDOW_DAYS).std() * np.sqrt(252)
                        rolling_volatility = returns.rolling(window=ROLLING_WINDOW_DAYS).std() * np.sqrt(252)
                        rolling_var = returns.rolling(window=ROLLING_WINDOW_DAYS).quantile(0.05)
                        
                        # Remove NaN values
                        valid_idx = ~(rolling_sharpe.isna() | rolling_volatility.isna() | rolling_var.isna())
                        dates = returns.index[valid_idx]
                        color = ChartHelper.get_color_for_portfolio(i)
                        
                        # Add trace based on selected metric
                        if selected_metric == "sharpe":
                            fig.add_trace(go.Scatter(
                                x=dates, y=rolling_sharpe[valid_idx],
                                mode='lines+markers',
                                name=f'{portfolio["name"]} - Sharpe',
                                line=dict(color=color, width=2),
                                yaxis='y'
                            ))
                        elif selected_metric == "volatility":
                            fig.add_trace(go.Scatter(
                                x=dates, y=rolling_volatility[valid_idx],
                                mode='lines+markers',
                                name=f'{portfolio["name"]} - Volatility',
                                line=dict(color=color, width=2, dash='dash'),
                                yaxis='y'
                            ))
                        elif selected_metric == "var_95":
                            fig.add_trace(go.Scatter(
                                x=dates, y=rolling_var[valid_idx],
                                mode='lines+markers',
                                name=f'{portfolio["name"]} - VaR (95%)',
                                line=dict(color=color, width=2, dash='dot'),
                                yaxis='y'
                            ))
                
                except Exception as e:
                    ErrorHandler.handle_calculation_error(e, f"risk metrics for {portfolio['name']}")
                    continue
            
            # Update layout
            metric_title = RISK_METRICS.get(selected_metric, selected_metric.title())
            fig.update_layout(
                title=f"Risk Metrics Over Time - {metric_title} (Real Data)",
                xaxis_title="Date",
                yaxis=dict(title=metric_title, side="left"),
                hovermode='x unified',
                height=CHART_HEIGHT
            )
            
            return fig
    
    def _register_performance_callbacks(self):
        """Register performance metrics callbacks."""
        
        @self.app.callback(
            Output("performance-portfolio-selector", "options"),
            [Input("tabs", "active_tab")]
        )
        def update_performance_portfolio_selector(active_tab: str):
            """Update performance portfolio selector options."""
            if active_tab != "performance-tab":
                return []
            
            portfolios = self.db_manager.get_all_portfolios()
            return [{"label": p["name"], "value": p["name"]} for p in portfolios]
        
        @self.app.callback(
            Output("performance-comparison-chart", "figure"),
            [Input("tabs", "active_tab"),
             Input("performance-portfolio-selector", "value")],
            prevent_initial_call=True
        )
        def update_performance_comparison(active_tab: str, selected_portfolios: List[str]):
            """Update performance comparison chart."""
            if active_tab != "performance-tab":
                return ChartHelper.create_empty_figure()
            
            if not selected_portfolios:
                return ChartHelper.create_empty_figure("Please select portfolios to compare performance")
            
            fig = go.Figure()
            portfolios = self.db_manager.get_all_portfolios()
            portfolios_to_analyze = [p for p in portfolios if p['name'] in selected_portfolios]
            
            if not portfolios_to_analyze:
                return ChartHelper.create_empty_figure("No valid portfolios selected")
            
            start_date, end_date = DateHelper.get_analysis_date_range()
            
            for i, portfolio in enumerate(portfolios_to_analyze):
                try:
                    analytics = self.db_manager.calculate_portfolio_analytics(
                        portfolio['symbols'], portfolio['weights'], start_date, end_date
                    )
                    
                    if analytics and 'returns' in analytics:
                        returns = ensure_pandas_series(analytics['returns'])
                        cumulative_returns = (1 + returns).cumprod()
                        
                        color = ChartHelper.get_color_for_portfolio(i)
                        fig.add_trace(go.Scatter(
                            x=returns.index,
                            y=cumulative_returns,
                            mode='lines',
                            name=portfolio['name'],
                            line=dict(color=color, width=2)
                        ))
                
                except Exception as e:
                    ErrorHandler.handle_calculation_error(e, f"performance for {portfolio['name']}")
                    continue
            
            fig.update_layout(
                title="Portfolio Performance Comparison",
                xaxis_title="Date",
                yaxis_title="Cumulative Return",
                hovermode='x unified',
                height=CHART_HEIGHT
            )
            
            return fig
