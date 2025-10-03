"""
Portfolio Management Service for creating, saving, and analyzing multiple portfolios
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import create_engine, text
import logging
from datetime import datetime, timedelta
import json
from config.config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class PortfolioManagementService:
    """Service for managing multiple portfolios"""
    
    def __init__(self):
        self.engine = create_engine(
            f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@"
            f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['name']}"
        )
    
    def create_portfolio(self, name: str, description: str, symbols: List[str], 
                        weights: List[float], strategy: str = "Custom") -> Dict[str, Any]:
        """Create a new portfolio"""
        try:
            # Validate inputs
            if len(symbols) != len(weights):
                raise ValueError("Number of symbols must match number of weights")
            
            if abs(sum(weights) - 1.0) > 0.01:
                raise ValueError("Weights must sum to 1.0")
            
            # Create portfolio record
            portfolio_data = {
                'name': name,
                'description': description,
                'symbols': symbols,
                'weights': weights,
                'strategy': strategy,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Store in database
            query = f"""
                INSERT INTO portfolios (name, description, symbols, weights, strategy, created_at, updated_at)
                VALUES ('{name}', '{description}', '{json.dumps(symbols)}', '{json.dumps(weights)}', 
                        '{strategy}', '{portfolio_data['created_at']}', '{portfolio_data['updated_at']}')
                RETURNING id
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                portfolio_id = result.fetchone()[0]
                conn.commit()
            
            portfolio_data['id'] = portfolio_id
            logger.info(f"Created portfolio '{name}' with ID {portfolio_id}")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error creating portfolio: {str(e)}")
            raise
    
    def get_all_portfolios(self) -> List[Dict[str, Any]]:
        """Get all saved portfolios"""
        try:
            query = "SELECT * FROM portfolios ORDER BY created_at DESC"
            df = pd.read_sql(query, self.engine)
            
            portfolios = []
            for _, row in df.iterrows():
                # Handle JSON parsing safely
                symbols = row['symbols']
                weights = row['weights']
                
                # If it's already a list, use it; otherwise parse JSON
                if isinstance(symbols, str):
                    symbols = json.loads(symbols)
                if isinstance(weights, str):
                    weights = json.loads(weights)
                
                portfolio = {
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'symbols': symbols,
                    'weights': weights,
                    'strategy': row['strategy'],
                    'created_at': row['created_at'].isoformat() if pd.notna(row['created_at']) else None,
                    'updated_at': row['updated_at'].isoformat() if pd.notna(row['updated_at']) else None
                }
                portfolios.append(portfolio)
            
            return portfolios
            
        except Exception as e:
            logger.error(f"Error getting portfolios: {str(e)}")
            return []
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific portfolio by ID"""
        try:
            query = f"SELECT * FROM portfolios WHERE id = {portfolio_id}"
            df = pd.read_sql(query, self.engine)
            
            if df.empty:
                return None
            
            row = df.iloc[0]
            
            # Handle JSON parsing safely
            symbols = row['symbols']
            weights = row['weights']
            
            # If it's already a list, use it; otherwise parse JSON
            if isinstance(symbols, str):
                symbols = json.loads(symbols)
            if isinstance(weights, str):
                weights = json.loads(weights)
            
            portfolio = {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'symbols': symbols,
                'weights': weights,
                'strategy': row['strategy'],
                'created_at': row['created_at'].isoformat() if pd.notna(row['created_at']) else None,
                'updated_at': row['updated_at'].isoformat() if pd.notna(row['updated_at']) else None
            }
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting portfolio {portfolio_id}: {str(e)}")
            return None
    
    def update_portfolio(self, portfolio_id: int, name: str = None, description: str = None,
                        symbols: List[str] = None, weights: List[float] = None,
                        strategy: str = None) -> bool:
        """Update an existing portfolio"""
        try:
            # Build the update query using SQLAlchemy's text with named parameters
            update_fields = []
            params = {}
            
            if name is not None:
                update_fields.append("name = :name")
                params['name'] = name
            
            if description is not None:
                update_fields.append("description = :description")
                params['description'] = description
            
            if symbols is not None:
                update_fields.append("symbols = :symbols")
                params['symbols'] = json.dumps(symbols)
            
            if weights is not None:
                update_fields.append("weights = :weights")
                params['weights'] = json.dumps(weights)
            
            if strategy is not None:
                update_fields.append("strategy = :strategy")
                params['strategy'] = strategy
            
            if not update_fields:
                return True
            
            update_fields.append("updated_at = :updated_at")
            params['updated_at'] = datetime.now().isoformat()
            params['portfolio_id'] = portfolio_id
            
            query = f"UPDATE portfolios SET {', '.join(update_fields)} WHERE id = :portfolio_id"
            
            with self.engine.connect() as conn:
                conn.execute(text(query), params)
                conn.commit()
            
            logger.info(f"Updated portfolio {portfolio_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating portfolio {portfolio_id}: {str(e)}")
            return False
    
    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete a portfolio"""
        try:
            query = f"DELETE FROM portfolios WHERE id = {portfolio_id}"
            
            with self.engine.connect() as conn:
                conn.execute(text(query))
                conn.commit()
            
            logger.info(f"Deleted portfolio {portfolio_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting portfolio {portfolio_id}: {str(e)}")
            return False
    
    def calculate_portfolio_analytics(self, symbols: List[str], weights: List[float], 
                                    start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Calculate comprehensive portfolio analytics"""
        try:
            # Get stock price data
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Build query for stock prices
            symbol_list = "','".join(symbols)
            query = f"""
                SELECT symbol, date, close, volume
                FROM stock_prices 
                WHERE symbol IN ('{symbol_list}')
                AND date >= '{start_date}' AND date <= '{end_date}'
                ORDER BY date, symbol
            """
            
            price_data = pd.read_sql(query, self.engine)
            
            if price_data.empty:
                return {"error": "No price data available for the selected symbols"}
            
            # Pivot data to get prices by date
            price_pivot = price_data.pivot(index='date', columns='symbol', values='close')
            price_pivot = price_pivot.fillna(method='ffill').fillna(method='bfill')
            
            # Check which symbols have data
            available_symbols = list(price_pivot.columns)
            missing_symbols = [s for s in symbols if s not in available_symbols]
            
            if missing_symbols:
                logger.warning(f"Missing data for symbols: {missing_symbols}")
            
            # If no symbols have data, return error
            if not available_symbols:
                return {"error": f"No price data available for any of the symbols: {symbols}"}
            
            # Calculate returns
            returns = price_pivot.pct_change().dropna()
            
            # Create weights array that matches available symbols
            weights_dict = dict(zip(symbols, weights))
            available_weights = [weights_dict.get(symbol, 0.0) for symbol in available_symbols]
            weights_array = np.array(available_weights)
            
            # Normalize weights to sum to 1
            if weights_array.sum() > 0:
                weights_array = weights_array / weights_array.sum()
            else:
                # If no weights available, use equal weights
                weights_array = np.array([1.0 / len(available_symbols)] * len(available_symbols))
            
            # Calculate portfolio returns
            portfolio_returns = (returns * weights_array).sum(axis=1)
            
            # Calculate analytics
            analytics = self._calculate_risk_metrics(portfolio_returns, returns, weights_array)
            analytics.update(self._calculate_performance_metrics(portfolio_returns))
            analytics.update(self._calculate_drawdown_metrics(portfolio_returns))
            analytics.update(self._calculate_volatility_metrics(portfolio_returns, returns, weights_array))
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error calculating portfolio analytics: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_risk_metrics(self, portfolio_returns: pd.Series, 
                               asset_returns: pd.DataFrame, weights: List[float]) -> Dict[str, float]:
        """Calculate risk metrics"""
        try:
            # VaR (Value at Risk) - 95% confidence
            var_95 = np.percentile(portfolio_returns, 5)
            
            # CVaR (Conditional Value at Risk) - Expected Shortfall
            cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
            
            # Beta (if we had market data)
            beta = 1.0  # Placeholder - would need market index data
            
            # Maximum Drawdown
            cumulative_returns = (1 + portfolio_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            return {
                'var_95': float(var_95),
                'cvar_95': float(cvar_95),
                'beta': float(beta),
                'max_drawdown': float(max_drawdown)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {str(e)}")
            return {}
    
    def _calculate_performance_metrics(self, portfolio_returns: pd.Series) -> Dict[str, float]:
        """Calculate performance metrics"""
        try:
            # Total return
            total_return = (1 + portfolio_returns).prod() - 1
            
            # Annualized return
            days = len(portfolio_returns)
            annualized_return = (1 + total_return) ** (252 / days) - 1
            
            # Sharpe ratio (assuming 2% risk-free rate)
            risk_free_rate = 0.02
            excess_returns = portfolio_returns - risk_free_rate / 252
            sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
            
            # Sortino ratio
            downside_returns = portfolio_returns[portfolio_returns < 0]
            downside_std = downside_returns.std()
            sortino_ratio = excess_returns.mean() / downside_std * np.sqrt(252) if downside_std > 0 else 0
            
            return {
                'total_return': float(total_return),
                'annualized_return': float(annualized_return),
                'sharpe_ratio': float(sharpe_ratio),
                'sortino_ratio': float(sortino_ratio)
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            return {}
    
    def _calculate_drawdown_metrics(self, portfolio_returns: pd.Series) -> Dict[str, float]:
        """Calculate drawdown metrics"""
        try:
            cumulative_returns = (1 + portfolio_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            
            # Maximum drawdown
            max_drawdown = drawdown.min()
            
            # Average drawdown
            avg_drawdown = drawdown[drawdown < 0].mean()
            
            # Drawdown duration (simplified)
            drawdown_periods = (drawdown < 0).sum()
            total_periods = len(drawdown)
            drawdown_frequency = drawdown_periods / total_periods
            
            return {
                'max_drawdown': float(max_drawdown),
                'avg_drawdown': float(avg_drawdown),
                'drawdown_frequency': float(drawdown_frequency)
            }
            
        except Exception as e:
            logger.error(f"Error calculating drawdown metrics: {str(e)}")
            return {}
    
    def _calculate_volatility_metrics(self, portfolio_returns: pd.Series, 
                                     asset_returns: pd.DataFrame, weights: List[float]) -> Dict[str, float]:
        """Calculate volatility metrics"""
        try:
            # Portfolio volatility (annualized)
            portfolio_volatility = portfolio_returns.std() * np.sqrt(252)
            
            # Individual asset volatilities
            asset_volatilities = asset_returns.std() * np.sqrt(252)
            
            # Weighted average volatility
            weighted_avg_vol = (asset_volatilities * weights).sum()
            
            # Diversification ratio
            diversification_ratio = weighted_avg_vol / portfolio_volatility if portfolio_volatility > 0 else 1
            
            return {
                'portfolio_volatility': float(portfolio_volatility),
                'weighted_avg_volatility': float(weighted_avg_vol),
                'diversification_ratio': float(diversification_ratio)
            }
            
        except Exception as e:
            logger.error(f"Error calculating volatility metrics: {str(e)}")
            return {}
    
    def backtest_portfolio(self, symbols: List[str], weights: List[float],
                          start_date: str, end_date: str, rebalance_frequency: str = 'monthly') -> Dict[str, Any]:
        """Perform backtesting on a portfolio"""
        try:
            # Get price data
            symbol_list = "','".join(symbols)
            query = f"""
                SELECT symbol, date, close
                FROM stock_prices 
                WHERE symbol IN ('{symbol_list}')
                AND date >= '{start_date}' AND date <= '{end_date}'
                ORDER BY date, symbol
            """
            
            price_data = pd.read_sql(query, self.engine)
            
            if price_data.empty:
                return {"error": "No price data available for backtesting"}
            
            # Pivot and calculate returns
            price_pivot = price_data.pivot(index='date', columns='symbol', values='close')
            price_pivot = price_pivot.fillna(method='ffill').fillna(method='bfill')
            
            # Simple backtesting (buy and hold with rebalancing)
            initial_value = 10000  # $10,000 starting value
            portfolio_value = [initial_value]
            dates = [price_pivot.index[0]]
            
            # Calculate portfolio value over time
            for i in range(1, len(price_pivot)):
                current_date = price_pivot.index[i]
                previous_date = price_pivot.index[i-1]
                
                # Calculate returns for this period
                period_returns = (price_pivot.iloc[i] / price_pivot.iloc[i-1] - 1) * weights
                period_return = period_returns.sum()
                
                # Update portfolio value
                new_value = portfolio_value[-1] * (1 + period_return)
                portfolio_value.append(new_value)
                dates.append(current_date)
            
            # Create backtest results
            backtest_results = {
                'dates': [d.isoformat() for d in dates],
                'portfolio_values': portfolio_value,
                'total_return': (portfolio_value[-1] / initial_value - 1) * 100,
                'annualized_return': ((portfolio_value[-1] / initial_value) ** (252 / len(dates)) - 1) * 100,
                'max_value': max(portfolio_value),
                'min_value': min(portfolio_value),
                'final_value': portfolio_value[-1]
            }
            
            return backtest_results
            
        except Exception as e:
            logger.error(f"Error in backtesting: {str(e)}")
            return {"error": str(e)}
    
    def compare_portfolios(self, portfolio_ids: List[int]) -> Dict[str, Any]:
        """Compare multiple portfolios"""
        try:
            portfolios = []
            for pid in portfolio_ids:
                portfolio = self.get_portfolio(pid)
                if portfolio:
                    analytics = self.calculate_portfolio_analytics(
                        portfolio['symbols'], portfolio['weights']
                    )
                    portfolio['analytics'] = analytics
                    portfolios.append(portfolio)
            
            if not portfolios:
                return {"error": "No valid portfolios found for comparison"}
            
            # Create comparison data
            comparison = {
                'portfolios': portfolios,
                'summary': {
                    'best_return': max(p['analytics'].get('annualized_return', 0) for p in portfolios),
                    'best_sharpe': max(p['analytics'].get('sharpe_ratio', 0) for p in portfolios),
                    'lowest_volatility': min(p['analytics'].get('portfolio_volatility', float('inf')) for p in portfolios),
                    'lowest_drawdown': max(p['analytics'].get('max_drawdown', -1) for p in portfolios)
                }
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing portfolios: {str(e)}")
            return {"error": str(e)}
