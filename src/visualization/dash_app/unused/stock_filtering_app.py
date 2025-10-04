"""
Stock Filtering Dashboard Application
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from typing import Dict, List, Any
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.data_access.stock_filtering_service import StockFilteringService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Stock Filtering Dashboard"

# Initialize the stock filtering service
stock_service = StockFilteringService()

def create_filter_controls():
    """Create filter control components"""
    
    # Get available filter options
    available_filters = stock_service.get_available_filters()
    
    return dbc.Card([
        dbc.CardHeader("Stock Filters"),
        dbc.CardBody([
            dbc.Row([
                # Market Cap Categories
                dbc.Col([
                    dbc.Label("Market Cap Categories"),
                    dcc.Dropdown(
                        id="market-cap-filter",
                        options=[{"label": cat, "value": cat} for cat in available_filters.get('market_cap_categories', [])],
                        multi=True,
                        placeholder="Select market cap categories"
                    )
                ], width=6),
                
                # Sectors
                dbc.Col([
                    dbc.Label("Sectors"),
                    dcc.Dropdown(
                        id="sector-filter",
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
                        id="industry-filter",
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
                                id="price-min",
                                type="number",
                                placeholder="Min Price",
                                min=0
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Input(
                                id="price-max",
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
                                id="pe-min",
                                type="number",
                                placeholder="Min PE",
                                min=0
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Input(
                                id="pe-max",
                                type="number",
                                placeholder="Max PE",
                                min=0
                            )
                        ], width=6)
                    ])
                ], width=6),
                
                # PEG Ratio Range
                dbc.Col([
                    dbc.Label("PEG Ratio Range"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id="peg-min",
                                type="number",
                                placeholder="Min PEG",
                                min=0
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Input(
                                id="peg-max",
                                type="number",
                                placeholder="Max PEG",
                                min=0
                            )
                        ], width=6)
                    ])
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                # Dividend Yield Range
                dbc.Col([
                    dbc.Label("Dividend Yield Range (%)"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id="div-min",
                                type="number",
                                placeholder="Min Div %",
                                min=0,
                                step=0.1
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Input(
                                id="div-max",
                                type="number",
                                placeholder="Max Div %",
                                min=0,
                                step=0.1
                            )
                        ], width=6)
                    ])
                ], width=6),
                
                # Beta Range
                dbc.Col([
                    dbc.Label("Beta Range"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id="beta-min",
                                type="number",
                                placeholder="Min Beta",
                                min=0
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Input(
                                id="beta-max",
                                type="number",
                                placeholder="Max Beta",
                                min=0
                            )
                        ], width=6)
                    ])
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                # Volume
                dbc.Col([
                    dbc.Label("Minimum Volume"),
                    dbc.Input(
                        id="volume-min",
                        type="number",
                        placeholder="Min Volume",
                        min=0
                    )
                ], width=6),
                
                # Action Buttons
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Apply Filters", id="apply-filters", color="primary", className="me-2")
                        ], width=6),
                        dbc.Col([
                            dbc.Button("Clear Filters", id="clear-filters", color="secondary")
                        ], width=6)
                    ])
                ], width=6)
            ])
        ])
    ])

def create_summary_cards():
    """Create summary cards"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-stocks", className="card-title"),
                    html.P("Total Stocks", className="card-text")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="filtered-stocks", className="card-title"),
                    html.P("Filtered Stocks", className="card-text")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-pe", className="card-title"),
                    html.P("Average PE Ratio", className="card-text")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-dividend", className="card-title"),
                    html.P("Average Dividend Yield", className="card-text")
                ])
            ])
        ], width=3)
    ], className="mb-4")

def create_charts():
    """Create chart components"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Market Cap Distribution"),
                dbc.CardBody([
                    dcc.Graph(id="market-cap-chart")
                ])
            ])
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Sector Distribution"),
                dbc.CardBody([
                    dcc.Graph(id="sector-chart")
                ])
            ])
        ], width=6)
    ], className="mb-4")

def create_stock_table():
    """Create stock results table"""
    return dbc.Card([
        dbc.CardHeader("Filtered Stocks"),
        dbc.CardBody([
            html.Div(id="stock-table")
        ])
    ])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Stock Filtering Dashboard", className="text-center mb-4")
        ])
    ]),
    
    # Summary Cards
    create_summary_cards(),
    
    # Filter Controls
    create_filter_controls(),
    
    # Charts
    create_charts(),
    
    # Stock Table
    create_stock_table(),
    
    # Hidden div to store filtered data
    html.Div(id="filtered-data", style={"display": "none"})
    
], fluid=True)

# Callbacks
@app.callback(
    [Output("filtered-data", "children"),
     Output("filtered-stocks", "children"),
     Output("avg-pe", "children"),
     Output("avg-dividend", "children")],
    [Input("apply-filters", "n_clicks")],
    [State("market-cap-filter", "value"),
     State("sector-filter", "value"),
     State("industry-filter", "value"),
     State("price-min", "value"),
     State("price-max", "value"),
     State("pe-min", "value"),
     State("pe-max", "value"),
     State("peg-min", "value"),
     State("peg-max", "value"),
     State("div-min", "value"),
     State("div-max", "value"),
     State("beta-min", "value"),
     State("beta-max", "value"),
     State("volume-min", "value")]
)
def apply_filters(n_clicks, market_cap, sectors, industries, price_min, price_max,
                 pe_min, pe_max, peg_min, peg_max, div_min, div_max, beta_min, beta_max, volume_min):
    """Apply filters and return filtered data"""
    
    if n_clicks is None:
        # Return all stocks on initial load
        filtered_data = stock_service.get_all_stocks()
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
        if peg_min is not None:
            filters['peg_ratio_min'] = peg_min
        if peg_max is not None:
            filters['peg_ratio_max'] = peg_max
        if div_min is not None:
            filters['dividend_yield_min'] = div_min / 100  # Convert percentage to decimal
        if div_max is not None:
            filters['dividend_yield_max'] = div_max / 100
        if beta_min is not None:
            filters['beta_min'] = beta_min
        if beta_max is not None:
            filters['beta_max'] = beta_max
        if volume_min is not None:
            filters['volume_min'] = volume_min
        
        # Apply filters
        filtered_data = stock_service.get_stocks_by_filters(filters)
    
    # Calculate summary metrics
    filtered_count = len(filtered_data)
    avg_pe = filtered_data['pe_ratio'].mean() if not filtered_data.empty else 0
    avg_dividend = filtered_data['dividend_yield'].mean() if not filtered_data.empty else 0
    
    # Store filtered data as JSON
    filtered_json = filtered_data.to_json(orient='records') if not filtered_data.empty else "[]"
    
    return filtered_json, filtered_count, f"{avg_pe:.2f}", f"{avg_dividend:.4f}"

@app.callback(
    [Output("market-cap-chart", "figure"),
     Output("sector-chart", "figure")],
    [Input("filtered-data", "children")]
)
def update_charts(filtered_json):
    """Update charts based on filtered data"""
    
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
        logger.error(f"Error updating charts: {str(e)}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Error loading data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig

@app.callback(
    Output("stock-table", "children"),
    [Input("filtered-data", "children")]
)
def update_stock_table(filtered_json):
    """Update stock table based on filtered data"""
    
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
    [Output("market-cap-filter", "value"),
     Output("sector-filter", "value"),
     Output("industry-filter", "value"),
     Output("price-min", "value"),
     Output("price-max", "value"),
     Output("pe-min", "value"),
     Output("pe-max", "value"),
     Output("peg-min", "value"),
     Output("peg-max", "value"),
     Output("div-min", "value"),
     Output("div-max", "value"),
     Output("beta-min", "value"),
     Output("beta-max", "value"),
     Output("volume-min", "value")],
    [Input("clear-filters", "n_clicks")]
)
def clear_filters(n_clicks):
    """Clear all filters"""
    if n_clicks:
        return [None] * 14  # Clear all 14 filter inputs
    return [dash.no_update] * 14

@app.callback(
    Output("total-stocks", "children"),
    [Input("filtered-data", "children")]
)
def update_total_stocks(filtered_json):
    """Update total stocks count"""
    try:
        all_stocks = stock_service.get_all_stocks()
        return len(all_stocks)
    except Exception as e:
        logger.error(f"Error getting total stocks: {str(e)}")
        return 0

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8051)

